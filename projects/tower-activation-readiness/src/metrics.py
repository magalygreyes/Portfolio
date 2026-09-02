"""Readiness, blocker and aging calculations.

All functions take *cleaned* DataFrames (output of validate.py) and an
`as_of` Timestamp so results are reproducible on any day.
"""

from __future__ import annotations

import pandas as pd

DONE = ["Complete", "Verified"]
OPEN = ["Not Started", "In Progress", "Blocked"]
EQUIP_DONE = "Accepted"

AGE_BINS = [-1, 7, 14, 30, 60, 10_000]
AGE_LABELS = ["0-7 days", "8-14 days", "15-30 days", "31-60 days", "60+ days"]


def enrich_items(items: pd.DataFrame, rooms: pd.DataFrame, owners: pd.DataFrame,
                 as_of: pd.Timestamp) -> pd.DataFrame:
    """Join room and owner attributes onto checklist items and add derived columns."""
    df = items.merge(rooms[["room_id", "floor", "unit", "room_type", "target_activation_date"]],
                     on="room_id", how="left")
    df = df.merge(owners[["owner_id", "owner_name", "department"]], on="owner_id", how="left")
    df["is_done"] = df["status"].isin(DONE)
    df["is_open"] = ~df["is_done"]
    df["is_blocked"] = df["status"] == "Blocked"
    df["age_days"] = (as_of - df["created_date"]).dt.days.where(df["is_open"])
    df["days_since_update"] = (as_of - df["last_updated"]).dt.days.where(df["is_open"])
    df["is_overdue"] = df["is_open"] & df["due_date"].notna() & (df["due_date"] < as_of)
    df["days_overdue"] = (as_of - df["due_date"]).dt.days.where(df["is_overdue"])
    df["age_bucket"] = pd.cut(df["age_days"], bins=AGE_BINS, labels=AGE_LABELS)
    return df


def enrich_equipment(equipment: pd.DataFrame, rooms: pd.DataFrame, owners: pd.DataFrame) -> pd.DataFrame:
    df = equipment.merge(rooms[["room_id", "floor", "unit"]], on="room_id", how="left")
    df = df.merge(owners[["owner_id", "owner_name", "department"]], on="owner_id", how="left")
    df["is_accepted"] = df["status"] == EQUIP_DONE
    return df


def room_readiness(items: pd.DataFrame, equipment: pd.DataFrame, rooms: pd.DataFrame) -> pd.DataFrame:
    """One row per room with completion counts and a readiness state.

    A room is READY when every checklist item is Complete/Verified and every
    piece of equipment is Accepted. Readiness % is items done + equipment
    accepted over the total of both.
    """
    i = items.groupby("room_id").agg(items_total=("item_id", "size"),
                                     items_done=("is_done", "sum"),
                                     items_blocked=("is_blocked", "sum"),
                                     items_overdue=("is_overdue", "sum"))
    e = equipment.groupby("room_id").agg(equip_total=("equipment_id", "size"),
                                         equip_accepted=("is_accepted", "sum"))
    r = rooms.set_index("room_id")[["floor", "unit", "room_type", "target_activation_date"]]
    df = r.join(i, how="left").join(e, how="left").fillna(0)
    for c in ["items_total", "items_done", "items_blocked", "items_overdue", "equip_total", "equip_accepted"]:
        df[c] = df[c].astype(int)
    denom = (df["items_total"] + df["equip_total"]).replace(0, pd.NA)
    df["readiness_pct"] = ((df["items_done"] + df["equip_accepted"]) / denom * 100).astype(float).round(1)
    df["is_ready"] = (df["items_done"] == df["items_total"]) & (df["equip_accepted"] == df["equip_total"]) & (denom.notna())
    df["state"] = "Not ready"
    df.loc[df["readiness_pct"] >= 80, "state"] = "Nearly ready"
    df.loc[df["is_ready"], "state"] = "Ready"
    df.loc[df["items_blocked"] > 0, "state"] = "Blocked"
    return df.reset_index()


def summary(items: pd.DataFrame, equipment: pd.DataFrame, rooms_ready: pd.DataFrame) -> dict:
    total = len(items)
    done = int(items["is_done"].sum())
    return {
        "readiness_pct": round(done / total * 100, 1) if total else 0.0,
        "items_total": total,
        "items_done": done,
        "items_open": total - done,
        "rooms_total": len(rooms_ready),
        "rooms_ready": int(rooms_ready["is_ready"].sum()),
        "rooms_blocked": int((rooms_ready["items_blocked"] > 0).sum()),
        "blockers": int(items["is_blocked"].sum()),
        "overdue": int(items["is_overdue"].sum()),
        "high_priority_open": int((items["is_open"] & (items["priority"] == "High")).sum()),
        "equip_total": len(equipment),
        "equip_accepted": int(equipment["is_accepted"].sum()),
        "equip_pct": round(equipment["is_accepted"].mean() * 100, 1) if len(equipment) else 0.0,
        "median_open_age": float(items.loc[items["is_open"], "age_days"].median()) if (total - done) else 0.0,
        "stale_open": int((items["days_since_update"] > 14).sum()),
    }


def readiness_by(items: pd.DataFrame, col: str) -> pd.DataFrame:
    g = items.groupby(col).agg(total=("item_id", "size"), done=("is_done", "sum"),
                               blocked=("is_blocked", "sum"), overdue=("is_overdue", "sum"))
    g["readiness_pct"] = (g["done"] / g["total"] * 100).round(1)
    g["open"] = g["total"] - g["done"]
    return g.reset_index().sort_values("readiness_pct")


def blockers(items: pd.DataFrame) -> pd.DataFrame:
    b = items[items["is_blocked"]].copy()
    cols = ["item_id", "room_id", "floor", "unit", "category", "description", "priority",
            "owner_name", "department", "blocker_reason", "age_days", "days_since_update",
            "due_date", "is_overdue"]
    return b[cols].sort_values(["priority", "age_days"], key=lambda s: s.map({"High": 0, "Medium": 1, "Low": 2}) if s.name == "priority" else -s)


def aging(items: pd.DataFrame) -> pd.DataFrame:
    o = items[items["is_open"]]
    a = o.groupby("age_bucket", observed=False).size().rename("open_items").reset_index()
    return a


def aging_by(items: pd.DataFrame, col: str) -> pd.DataFrame:
    o = items[items["is_open"]]
    return (o.pivot_table(index=col, columns="age_bucket", values="item_id",
                          aggfunc="size", fill_value=0, observed=False)
            .reindex(columns=AGE_LABELS, fill_value=0))


def owner_workload(items: pd.DataFrame) -> pd.DataFrame:
    o = items[items["is_open"]]
    g = o.groupby(["owner_name", "department"]).agg(
        open_items=("item_id", "size"), blocked=("is_blocked", "sum"),
        overdue=("is_overdue", "sum"), high_priority=("priority", lambda s: (s == "High").sum()),
        oldest_days=("age_days", "max"), median_age=("age_days", "median"))
    return g.reset_index().sort_values("open_items", ascending=False)
