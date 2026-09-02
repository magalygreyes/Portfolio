"""
validator.py
Loads the seven CSVs, cleans what can be cleaned silently, rejects what
cannot be trusted, and warns about the rest. Nothing downstream touches raw
data; every page and metric works from the `clean` tables this returns.

Usage:
    from validator import load_and_validate
    clean, issues, summary = load_and_validate("data")

clean   : dict of DataFrames keyed by table name
issues  : DataFrame with one row per finding
          columns: table, key, severity (reject | warn | fix), rule, detail
summary : DataFrame with rows in / rejected / warned / fixed / rows out per table

Rules: docs/data-model.md section 6.
"""

from pathlib import Path

import pandas as pd

import config as cfg

TABLES = {
    "project_managers": "project_managers.csv",
    "projects": "projects.csv",
    "status_updates": "status_updates.csv",
    "budget_lines": "budget_lines.csv",
    "milestones": "milestones.csv",
    "risks": "risks.csv",
    "capacity": "capacity.csv",
}


class Issues:
    """Collects findings. Small helper so every rule logs the same way."""

    def __init__(self):
        self.rows = []

    def add(self, table, keys, severity, rule, detail=""):
        for k in keys:
            self.rows.append({"table": table, "key": k, "severity": severity, "rule": rule, "detail": detail})

    def frame(self):
        cols = ["table", "key", "severity", "rule", "detail"]
        return pd.DataFrame(self.rows, columns=cols)


# ---------------------------------------------------------------- Generic helpers
def _trim_strings(df, table, key, issues):
    """Silent fix: strip whitespace from every text column."""
    for col in [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object]:
        before = df[col].astype("string")
        after = before.str.strip()
        changed = (before != after) & before.notna()
        if changed.any():
            issues.add(table, df.loc[changed, key], "fix", f"{col}: whitespace trimmed")
            df[col] = after
    return df


def _normalize_choice(df, col, allowed, table, key, issues):
    """Silent fix: case-insensitive match to the allowed list. Reject anything unmatched."""
    lookup = {a.lower(): a for a in allowed}
    raw = df[col].astype("string")
    fixed = raw.str.lower().map(lookup)
    casing_changed = fixed.notna() & (fixed != raw)
    if casing_changed.any():
        issues.add(table, df.loc[casing_changed, key], "fix", f"{col}: casing normalized")
    bad = fixed.isna() & raw.notna()
    if bad.any():
        issues.add(table, df.loc[bad, key], "reject", f"{col}: value outside allowed list",
                   "; ".join(sorted(raw[bad].unique()[:5])))
    df[col] = fixed
    return df, ~bad


def _require(df, col, table, key, issues):
    missing = df[col].isna() | (df[col].astype("string").str.len() == 0)
    if missing.any():
        issues.add(table, df.loc[missing, key], "reject", f"{col}: missing")
    return ~missing


def _numeric(df, col, table, key, issues, minimum=None, maximum=None, allow_blank=False):
    """Coerce to number. Non-numeric text is rejected; out-of-range is rejected."""
    raw = df[col]
    num = pd.to_numeric(raw, errors="coerce")
    blank = raw.isna() | (raw.astype("string").str.strip() == "")
    unparsable = num.isna() & ~blank
    if unparsable.any():
        issues.add(table, df.loc[unparsable, key], "reject", f"{col}: not a number")
    ok = ~unparsable
    if not allow_blank:
        if blank.any():
            issues.add(table, df.loc[blank, key], "reject", f"{col}: missing")
        ok &= ~blank
    if minimum is not None:
        low = num.notna() & (num < minimum)
        if low.any():
            issues.add(table, df.loc[low, key], "reject", f"{col}: below {minimum}")
        ok &= ~low
    if maximum is not None:
        high = num.notna() & (num > maximum)
        if high.any():
            issues.add(table, df.loc[high, key], "reject", f"{col}: above {maximum}")
        ok &= ~high
    df[col] = num
    return df, ok


def _date(df, col, table, key, issues, allow_blank=False):
    """Strict ISO dates (YYYY-MM-DD). Anything else is unreadable and rejected."""
    raw = df[col].astype("string").str.strip()
    parsed = pd.to_datetime(raw, format="%Y-%m-%d", errors="coerce")
    blank = raw.isna() | (raw == "")
    bad = parsed.isna() & ~blank
    if bad.any():
        issues.add(table, df.loc[bad, key], "reject", f"{col}: unreadable date",
                   "; ".join(raw[bad].unique()[:5]))
    ok = ~bad
    if not allow_blank and blank.any():
        issues.add(table, df.loc[blank, key], "reject", f"{col}: missing")
        ok &= ~blank
    df[col] = parsed
    return df, ok


def _unique(df, cols, table, key, issues):
    dup = df.duplicated(subset=cols, keep="first")
    if dup.any():
        issues.add(table, df.loc[dup, key], "reject", f"duplicate {' + '.join(cols)}")
    return ~dup


def _fk(df, col, parent_keys, table, key, issues):
    bad = df[col].notna() & ~df[col].isin(parent_keys)
    if bad.any():
        issues.add(table, df.loc[bad, key], "reject", f"{col}: not found in parent table",
                   "; ".join(df.loc[bad, col].astype(str).unique()[:5]))
    return ~bad


def _read(data_dir, name):
    path = Path(data_dir) / TABLES[name]
    return pd.read_csv(path, dtype=str, keep_default_na=False).replace({"": pd.NA})


# ---------------------------------------------------------------- Per-table validators
def validate_project_managers(df, issues):
    t, k = "project_managers", "pm_id"
    df = _trim_strings(df, t, k, issues)
    ok = _require(df, "pm_id", t, k, issues)
    ok &= _require(df, "pm_name", t, k, issues)
    ok &= _unique(df, ["pm_id"], t, k, issues)
    df, o = _normalize_choice(df, "department", cfg.DEPARTMENTS, t, k, issues); ok &= o
    df, o = _normalize_choice(df, "level", cfg.PM_LEVELS, t, k, issues); ok &= o
    df, o = _numeric(df, "default_weekly_hours", t, k, issues, minimum=1); ok &= o
    return df[ok].copy()


def validate_projects(df, pm_ids, issues):
    t, k = "projects", "project_id"
    df = _trim_strings(df, t, k, issues)
    ok = _require(df, "project_id", t, k, issues)
    ok &= _require(df, "project_name", t, k, issues)
    ok &= _unique(df, ["project_id"], t, k, issues)
    ok &= _fk(df, "pm_id", pm_ids, t, k, issues)
    df, o = _normalize_choice(df, "portfolio", cfg.PORTFOLIOS, t, k, issues); ok &= o
    df, o = _normalize_choice(df, "department", cfg.DEPARTMENTS, t, k, issues); ok &= o
    df, o = _normalize_choice(df, "phase", cfg.PHASES, t, k, issues); ok &= o
    for col in ["baseline_start", "baseline_finish", "forecast_finish"]:
        df, o = _date(df, col, t, k, issues); ok &= o
    order_bad = df["baseline_finish"].notna() & df["baseline_start"].notna() & (df["baseline_finish"] < df["baseline_start"])
    if order_bad.any():
        issues.add(t, df.loc[order_bad, k], "reject", "baseline_finish before baseline_start")
    ok &= ~order_bad
    df, o = _numeric(df, "approved_budget", t, k, issues, minimum=0); ok &= o
    for col in ["score_alignment", "score_value", "score_urgency", "score_risk", "score_effort"]:
        df, o = _numeric(df, col, t, k, issues, minimum=1, maximum=5); ok &= o
    # Warn: blank sponsor
    no_sponsor = df["sponsor"].isna()
    if no_sponsor.any():
        issues.add(t, df.loc[no_sponsor, k], "warn", "sponsor: blank")
    return df[ok].copy()


def validate_status_updates(df, project_ids, issues):
    t, k = "status_updates", "update_id"
    df = _trim_strings(df, t, k, issues)
    ok = _require(df, "update_id", t, k, issues)
    ok &= _unique(df, ["update_id"], t, k, issues)
    ok &= _fk(df, "project_id", project_ids, t, k, issues)
    df, o = _date(df, "update_date", t, k, issues); ok &= o
    df, o = _normalize_choice(df, "health", cfg.HEALTH, t, k, issues); ok &= o
    df, o = _numeric(df, "pct_complete", t, k, issues, minimum=0, maximum=100); ok &= o
    clean = df[ok].copy().sort_values(["project_id", "update_date"])
    # Warn: pct_complete went down between consecutive updates
    prev = clean.groupby("project_id")["pct_complete"].shift()
    dropped = prev.notna() & (clean["pct_complete"] < prev)
    if dropped.any():
        issues.add(t, clean.loc[dropped, k], "warn", "pct_complete decreased vs prior update")
    return clean


def validate_budget_lines(df, project_ids, issues):
    t = "budget_lines"
    df = _trim_strings(df, t, "project_id", issues)
    df["_key"] = df["project_id"].astype(str) + "|" + df["month"].astype(str)
    k = "_key"
    ok = _fk(df, "project_id", project_ids, t, k, issues)
    df, o = _date(df, "month", t, k, issues); ok &= o
    ok &= _unique(df, ["project_id", "month"], t, k, issues)
    df, o = _numeric(df, "planned", t, k, issues, minimum=0); ok &= o
    df, o = _numeric(df, "actual", t, k, issues, minimum=0, allow_blank=True); ok &= o
    # Warn: actual spend with no planned budget
    no_plan = ok & (df["planned"] == 0) & (df["actual"].fillna(0) > 0)
    if no_plan.any():
        issues.add(t, df.loc[no_plan, k], "warn", "actual spend with no planned budget")
    return df[ok].drop(columns="_key").copy()


def validate_milestones(df, project_ids, issues):
    t, k = "milestones", "milestone_id"
    df = _trim_strings(df, t, k, issues)
    ok = _require(df, "milestone_id", t, k, issues)
    ok &= _unique(df, ["milestone_id"], t, k, issues)
    ok &= _fk(df, "project_id", project_ids, t, k, issues)
    for col in ["baseline_date", "forecast_date"]:
        df, o = _date(df, col, t, k, issues); ok &= o
    df, o = _normalize_choice(df, "status", cfg.MILESTONE_STATUS, t, k, issues); ok &= o
    return df[ok].copy()


def validate_risks(df, project_ids, issues):
    t, k = "risks", "risk_id"
    df = _trim_strings(df, t, k, issues)
    ok = _require(df, "risk_id", t, k, issues)
    ok &= _unique(df, ["risk_id"], t, k, issues)
    ok &= _fk(df, "project_id", project_ids, t, k, issues)
    df, o = _numeric(df, "probability", t, k, issues, minimum=1, maximum=5); ok &= o
    df, o = _numeric(df, "impact", t, k, issues, minimum=1, maximum=5); ok &= o
    df, o = _normalize_choice(df, "status", cfg.RISK_STATUS, t, k, issues); ok &= o
    no_owner = df["owner"].isna()
    if no_owner.any():
        issues.add(t, df.loc[no_owner, k], "warn", "owner: blank, set to Unassigned")
        df.loc[no_owner, "owner"] = "Unassigned"
    return df[ok].copy()


def validate_capacity(df, pm_ids, project_ids, issues):
    t = "capacity"
    df = _trim_strings(df, t, "pm_id", issues)
    df["_key"] = df["pm_id"].astype(str) + "|" + df["project_id"].astype(str) + "|" + df["week_start"].astype(str)
    k = "_key"
    ok = _fk(df, "pm_id", pm_ids, t, k, issues)
    ok &= _fk(df, "project_id", project_ids, t, k, issues)
    df, o = _date(df, "week_start", t, k, issues); ok &= o
    ok &= _unique(df, ["pm_id", "project_id", "week_start"], t, k, issues)
    df, o = _numeric(df, "allocated_hours", t, k, issues, minimum=0); ok &= o
    df, o = _numeric(df, "available_hours", t, k, issues, minimum=0); ok &= o
    # Warn: week_start not a Monday (kept, but flagged)
    not_monday = ok & df["week_start"].notna() & (df["week_start"].dt.weekday != 0)
    if not_monday.any():
        issues.add(t, df.loc[not_monday, k], "warn", "week_start is not a Monday")
    clean = df[ok].drop(columns="_key").copy()
    # Warn: PM over 100% in any week
    weekly = clean.groupby(["pm_id", "week_start"]).agg(alloc=("allocated_hours", "sum"),
                                                        avail=("available_hours", "first")).reset_index()
    over = weekly[weekly["alloc"] > weekly["avail"]]
    if len(over):
        keys = over["pm_id"] + "|" + over["week_start"].dt.strftime("%Y-%m-%d")
        issues.add(t, keys, "warn", "PM over 100% allocation this week")
    return clean


# ---------------------------------------------------------------- Entry point
def load_and_validate(data_dir=cfg.DATA_DIR):
    issues = Issues()
    raw = {name: _read(data_dir, name) for name in TABLES}
    rows_in = {name: len(df) for name, df in raw.items()}

    clean = {}
    clean["project_managers"] = validate_project_managers(raw["project_managers"], issues)
    pm_ids = set(clean["project_managers"]["pm_id"])
    clean["projects"] = validate_projects(raw["projects"], pm_ids, issues)
    project_ids = set(clean["projects"]["project_id"])
    clean["status_updates"] = validate_status_updates(raw["status_updates"], project_ids, issues)
    clean["budget_lines"] = validate_budget_lines(raw["budget_lines"], project_ids, issues)
    clean["milestones"] = validate_milestones(raw["milestones"], project_ids, issues)
    clean["risks"] = validate_risks(raw["risks"], project_ids, issues)
    clean["capacity"] = validate_capacity(raw["capacity"], pm_ids, project_ids, issues)

    # Stale status warning (needs clean status updates + AS_OF)
    as_of = pd.Timestamp(cfg.AS_OF) if cfg.AS_OF else pd.Timestamp.today().normalize()
    active = clean["projects"][clean["projects"]["phase"].isin(cfg.ACTIVE_PHASES)]
    last = clean["status_updates"].groupby("project_id")["update_date"].max()
    days = (as_of - active["project_id"].map(last)).dt.days
    stale = active.loc[days.isna() | (days > cfg.STALE_DAYS), "project_id"]
    if len(stale):
        issues.add("projects", stale, "warn", f"no status update in {cfg.STALE_DAYS}+ days")

    issues_df = issues.frame()
    summary = []
    for name in TABLES:
        sub = issues_df[issues_df["table"] == name]
        summary.append({
            "table": name,
            "rows_in": rows_in[name],
            "rejected": sub[sub["severity"] == "reject"]["key"].nunique(),
            "warned": sub[sub["severity"] == "warn"]["key"].nunique(),
            "fixed": sub[sub["severity"] == "fix"]["key"].nunique(),
            "rows_out": len(clean[name]),
        })
    return clean, issues_df, pd.DataFrame(summary)


if __name__ == "__main__":
    clean, issues, summary = load_and_validate()
    print(summary.to_string(index=False))
    print(f"\nTotal findings: {len(issues)}  "
          f"(reject {(issues.severity == 'reject').sum()}, "
          f"warn {(issues.severity == 'warn').sum()}, "
          f"fix {(issues.severity == 'fix').sum()})")
