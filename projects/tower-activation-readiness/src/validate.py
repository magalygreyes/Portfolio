"""CSV validation for the Tower Activation Readiness dataset.

Every uploaded or bundled CSV runs through here before the dashboard uses it.
Findings are split into two levels:

* ERROR   - the row (or file) cannot be trusted; the dashboard will refuse to
            calculate readiness until it is fixed.
* WARNING - the data is usable but something looks off (stale row, blocked
            item with no reason, completion date in the future).

The validator also returns a *cleaned* copy of each table: trimmed strings,
normalised casing for status/priority values, parsed dates.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

ITEM_STATUSES = ["Not Started", "In Progress", "Blocked", "Complete", "Verified"]
DONE_STATUSES = ["Complete", "Verified"]
EQUIP_STATUSES = ["Ordered", "Delivered", "Installed", "Tested", "Accepted"]
PRIORITIES = ["High", "Medium", "Low"]

SCHEMA = {
    "rooms": {
        "key": "room_id",
        "required": ["room_id", "floor", "unit", "room_type", "target_activation_date"],
        "dates": ["target_activation_date"],
        "ints": ["floor", "square_feet"],
    },
    "owners": {
        "key": "owner_id",
        "required": ["owner_id", "owner_name", "department"],
        "dates": [],
        "ints": [],
    },
    "equipment": {
        "key": "equipment_id",
        "required": ["equipment_id", "room_id", "category", "status", "owner_id"],
        "dates": ["ordered_date", "delivered_date", "installed_date"],
        "ints": [],
        "allowed": {"status": EQUIP_STATUSES},
    },
    "checklist_items": {
        "key": "item_id",
        "required": ["item_id", "room_id", "category", "owner_id", "status",
                     "priority", "created_date", "due_date"],
        "dates": ["created_date", "due_date", "completed_date", "last_updated"],
        "ints": [],
        "allowed": {"status": ITEM_STATUSES, "priority": PRIORITIES},
    },
}


@dataclass
class Finding:
    level: str          # "ERROR" | "WARNING"
    table: str
    check: str
    message: str
    row_ids: list = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.row_ids)


@dataclass
class ValidationReport:
    findings: list[Finding] = field(default_factory=list)
    tables: dict[str, pd.DataFrame] = field(default_factory=dict)
    row_counts: dict[str, int] = field(default_factory=dict)

    def add(self, level, table, check, message, row_ids=None):
        self.findings.append(Finding(level, table, check, message, list(row_ids or [])))

    @property
    def errors(self):
        return [f for f in self.findings if f.level == "ERROR"]

    @property
    def warnings(self):
        return [f for f in self.findings if f.level == "WARNING"]

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_frame(self) -> pd.DataFrame:
        rows = [{
            "level": f.level, "table": f.table, "check": f.check,
            "rows_affected": f.count if f.row_ids else None,
            "message": f.message,
            "examples": ", ".join(map(str, f.row_ids[:5])) + (" …" if f.count > 5 else ""),
        } for f in self.findings]
        cols = ["level", "table", "check", "rows_affected", "message", "examples"]
        df = pd.DataFrame(rows, columns=cols)
        df["rows_affected"] = df["rows_affected"].astype("Int64")
        return df


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _canon(series: pd.Series, allowed: list[str]) -> pd.Series:
    """Trim whitespace and map case-insensitive matches onto the allowed spelling."""
    lookup = {a.lower(): a for a in allowed}
    s = series.astype("string").str.strip()
    return s.map(lambda v: lookup.get(v.lower(), v) if pd.notna(v) else v)


def _ids(df: pd.DataFrame, mask: pd.Series, key: str) -> list:
    if key in df.columns:
        return df.loc[mask, key].astype(str).tolist()
    return (df.index[mask] + 2).tolist()   # spreadsheet-style row numbers


# ---------------------------------------------------------------------------
# Per-table validation
# ---------------------------------------------------------------------------

def validate_table(name: str, df: pd.DataFrame, report: ValidationReport) -> pd.DataFrame:
    spec = SCHEMA[name]
    key = spec["key"]
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    report.row_counts[name] = len(df)

    # 1. required columns present
    missing = [c for c in spec["required"] if c not in df.columns]
    if missing:
        report.add("ERROR", name, "missing_columns",
                   f"Required column(s) missing: {', '.join(missing)}")
        # cannot go further without them
        return df
    optional_missing = [c for c in spec["dates"] if c not in df.columns]
    if optional_missing:
        report.add("WARNING", name, "missing_optional_columns",
                   f"Optional column(s) missing, treated as blank: {', '.join(optional_missing)}")
        for c in optional_missing:
            df[c] = pd.NA

    # 2. trim strings
    for c in df.columns:
        if df[c].dtype == object or str(df[c].dtype) == "string":
            df[c] = df[c].astype("string").str.strip()
            df.loc[df[c] == "", c] = pd.NA

    # 3. required values not blank
    for c in spec["required"]:
        mask = df[c].isna()
        if mask.any():
            report.add("ERROR", name, "missing_value",
                       f"'{c}' is blank", _ids(df, mask, key))

    # 4. duplicate keys
    dup = df[key].duplicated(keep=False) & df[key].notna()
    if dup.any():
        report.add("ERROR", name, "duplicate_id",
                   f"Duplicate '{key}' values", sorted(set(df.loc[dup, key])))

    # 5. allowed values (normalise first)
    for col, allowed in spec.get("allowed", {}).items():
        df[col] = _canon(df[col], allowed)
        bad = df[col].notna() & ~df[col].isin(allowed)
        if bad.any():
            report.add("ERROR", name, "invalid_value",
                       f"'{col}' has values outside {allowed}: "
                       f"{sorted(set(df.loc[bad, col]))}", _ids(df, bad, key))

    # 6. dates parse
    for col in spec["dates"]:
        raw = df[col]
        parsed = pd.to_datetime(raw, errors="coerce")
        bad = raw.notna() & parsed.isna()
        if bad.any():
            report.add("ERROR", name, "unparseable_date",
                       f"'{col}' has values that are not dates", _ids(df, bad, key))
        df[col] = parsed.dt.normalize()

    # 7. integers
    for col in spec["ints"]:
        if col in df.columns:
            num = pd.to_numeric(df[col], errors="coerce")
            bad = df[col].notna() & num.isna()
            if bad.any():
                report.add("ERROR", name, "not_a_number",
                           f"'{col}' must be numeric", _ids(df, bad, key))
            df[col] = num.astype("Int64")

    return df


def _cross_checks(t: dict[str, pd.DataFrame], report: ValidationReport, as_of: pd.Timestamp):
    rooms, owners = t.get("rooms"), t.get("owners")
    room_ids = set(rooms["room_id"].dropna()) if rooms is not None and "room_id" in rooms else None
    owner_ids = set(owners["owner_id"].dropna()) if owners is not None and "owner_id" in owners else None

    for name in ("equipment", "checklist_items"):
        df = t.get(name)
        if df is None:
            continue
        key = SCHEMA[name]["key"]
        if room_ids is not None and "room_id" in df:
            bad = df["room_id"].notna() & ~df["room_id"].isin(room_ids)
            if bad.any():
                report.add("ERROR", name, "orphan_room",
                           "room_id does not exist in rooms.csv", _ids(df, bad, key))
        if owner_ids is not None and "owner_id" in df:
            bad = df["owner_id"].notna() & ~df["owner_id"].isin(owner_ids)
            if bad.any():
                report.add("ERROR", name, "orphan_owner",
                           "owner_id does not exist in owners.csv", _ids(df, bad, key))

    items = t.get("checklist_items")
    if items is not None and "status" in items and "created_date" in items:
        key = "item_id"
        done = items["status"].isin(DONE_STATUSES)

        bad = done & items["completed_date"].isna()
        if bad.any():
            report.add("ERROR", "checklist_items", "done_without_date",
                       "Status is Complete/Verified but completed_date is blank", _ids(items, bad, key))

        bad = ~done & items["completed_date"].notna()
        if bad.any():
            report.add("WARNING", "checklist_items", "open_with_completed_date",
                       "Open item has a completed_date; status may be stale", _ids(items, bad, key))

        bad = items["created_date"].notna() & items["due_date"].notna() & (items["created_date"] > items["due_date"])
        if bad.any():
            report.add("ERROR", "checklist_items", "created_after_due",
                       "created_date is later than due_date", _ids(items, bad, key))

        bad = items["completed_date"].notna() & (items["completed_date"] > as_of)
        if bad.any():
            report.add("WARNING", "checklist_items", "future_completion",
                       f"completed_date is after the as-of date ({as_of.date()})", _ids(items, bad, key))

        bad = (items["status"] == "Blocked") & items["blocker_reason"].isna() if "blocker_reason" in items else pd.Series(False, index=items.index)
        if bad.any():
            report.add("WARNING", "checklist_items", "blocked_without_reason",
                       "Blocked item has no blocker_reason", _ids(items, bad, key))

        if "last_updated" in items:
            stale = ~done & items["last_updated"].notna() & ((as_of - items["last_updated"]).dt.days > 14)
            if stale.any():
                report.add("WARNING", "checklist_items", "stale_open_item",
                           "Open item not updated in more than 14 days", _ids(items, stale, key))


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def validate(tables: dict[str, pd.DataFrame], as_of=None) -> ValidationReport:
    """Validate a dict of raw DataFrames keyed by table name.

    Expected keys: rooms, owners, equipment, checklist_items (any subset).
    Returns a ValidationReport whose `.tables` holds the cleaned copies.
    """
    report = ValidationReport()
    for name, df in tables.items():
        if name not in SCHEMA:
            report.add("WARNING", name, "unknown_table", "Table not part of the schema; ignored")
            continue
        report.tables[name] = validate_table(name, df, report)

    if as_of is None:
        upd = report.tables.get("checklist_items", pd.DataFrame()).get("last_updated")
        as_of = upd.max() if upd is not None and upd.notna().any() else pd.Timestamp.today().normalize()
    _cross_checks(report.tables, report, pd.Timestamp(as_of))
    return report


def load_csvs(paths: dict[str, str]) -> dict[str, pd.DataFrame]:
    return {name: pd.read_csv(p, dtype=str) for name, p in paths.items()}


if __name__ == "__main__":
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent / "data"
    paths = {n: root / f"{n}.csv" for n in SCHEMA}
    if len(sys.argv) > 1:
        paths["checklist_items"] = Path(sys.argv[1])
    rep = validate(load_csvs(paths))
    print(rep.to_frame().to_string(index=False) if rep.findings else "No findings.")
    print(f"\n{'PASS' if rep.ok else 'FAIL'}: {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
    sys.exit(0 if rep.ok else 1)
