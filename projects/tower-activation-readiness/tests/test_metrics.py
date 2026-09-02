import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import metrics as m  # noqa: E402
import validate as v  # noqa: E402

AS_OF = pd.Timestamp("2026-09-01")


def tiny():
    rooms = pd.DataFrame({"room_id": ["R1", "R2"], "floor": [3, 3], "unit": ["ICU", "ICU"],
                          "room_type": ["Patient Room"] * 2,
                          "target_activation_date": pd.to_datetime(["2026-11-16"] * 2)})
    owners = pd.DataFrame({"owner_id": ["O1"], "owner_name": ["Ana"], "department": ["Facilities"]})
    items = pd.DataFrame({
        "item_id": ["I1", "I2", "I3", "I4"],
        "room_id": ["R1", "R1", "R2", "R2"],
        "category": ["A", "A", "A", "B"],
        "description": ["x"] * 4,
        "owner_id": ["O1"] * 4,
        "status": ["Verified", "Complete", "Blocked", "Not Started"],
        "priority": ["High", "Low", "High", "Medium"],
        "created_date": pd.to_datetime(["2026-08-01", "2026-08-01", "2026-06-01", "2026-08-25"]),
        "due_date": pd.to_datetime(["2026-09-15", "2026-09-15", "2026-08-15", "2026-10-01"]),
        "completed_date": pd.to_datetime(["2026-08-10", "2026-08-12", None, None]),
        "last_updated": pd.to_datetime(["2026-08-10", "2026-08-12", "2026-07-01", "2026-08-30"]),
        "blocker_reason": [None, None, "Waiting on vendor", None],
    })
    equipment = pd.DataFrame({
        "equipment_id": ["E1", "E2", "E3"], "room_id": ["R1", "R1", "R2"],
        "category": ["Bed"] * 3, "status": ["Accepted", "Accepted", "Ordered"], "owner_id": ["O1"] * 3,
    })
    it = m.enrich_items(items, rooms, owners, AS_OF)
    eq = m.enrich_equipment(equipment, rooms, owners)
    return rooms, it, eq


def test_room_readiness_states():
    rooms, it, eq = tiny()
    rr = m.room_readiness(it, eq, rooms).set_index("room_id")
    assert rr.loc["R1", "is_ready"] and rr.loc["R1", "state"] == "Ready"
    assert rr.loc["R1", "readiness_pct"] == 100.0
    assert rr.loc["R2", "state"] == "Blocked"
    assert rr.loc["R2", "readiness_pct"] == 0.0


def test_summary_counts():
    rooms, it, eq = tiny()
    rr = m.room_readiness(it, eq, rooms)
    s = m.summary(it, eq, rr)
    assert s["readiness_pct"] == 50.0
    assert s["rooms_ready"] == 1
    assert s["blockers"] == 1
    assert s["overdue"] == 1          # I3 was due 2026-08-15
    assert s["stale_open"] == 1       # I3 last updated 2026-07-01
    assert s["high_priority_open"] == 1


def test_aging_buckets():
    rooms, it, eq = tiny()
    a = m.aging(it).set_index("age_bucket")["open_items"]
    assert a["0-7 days"] == 1         # I4 created 2026-08-25
    assert a["60+ days"] == 1         # I3 created 2026-06-01
    assert a.sum() == 2


def test_bundled_pipeline_end_to_end():
    raw = v.load_csvs({n: ROOT / "data" / f"{n}.csv" for n in v.SCHEMA})
    rep = v.validate(raw, as_of=AS_OF)
    t = rep.tables
    it = m.enrich_items(t["checklist_items"], t["rooms"], t["owners"], AS_OF)
    eq = m.enrich_equipment(t["equipment"], t["rooms"], t["owners"])
    rr = m.room_readiness(it, eq, t["rooms"])
    s = m.summary(it, eq, rr)
    assert 0 < s["readiness_pct"] < 100
    assert s["rooms_total"] == 120
    assert len(m.blockers(it)) == s["blockers"]
