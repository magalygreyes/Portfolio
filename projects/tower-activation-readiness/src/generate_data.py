"""Generate the fake hospital-tower activation dataset.

Everything here is synthetic. No real facility, vendor, patient, or staff
data is used. The generator is seeded so the same files come out every run.

Run from the project root:
    python src/generate_data.py
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

SEED = 42
AS_OF = date(2026, 9, 1)            # "today" for the bundled dataset
ACTIVATION = date(2026, 11, 16)     # tower go-live target

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

FLOORS = {
    3: ("Emergency Department", 22),
    4: ("Surgery / OR", 16),
    5: ("ICU", 20),
    6: ("Med-Surg", 24),
    7: ("Labor & Delivery", 18),
    8: ("Oncology", 20),
}

ROOM_TYPES = ["Patient Room", "Patient Room", "Patient Room", "Procedure Room",
              "Support / Storage", "Nurse Station", "Medication Room"]

DEPARTMENTS = ["Facilities", "Biomedical Engineering", "IT / Low-Voltage",
               "Nursing", "Environmental Services", "Pharmacy", "Security",
               "Supply Chain"]

FIRST = ["Ana", "Marcus", "Priya", "Jordan", "Elena", "Samir", "Tasha", "Diego",
         "Grace", "Kenji", "Leah", "Omar", "Nadia", "Victor", "Ruth", "Tomas"]
LAST = ["Alvarez", "Chen", "Patel", "Okafor", "Nguyen", "Brooks", "Silva",
        "Kim", "Romero", "Fischer", "Haddad", "Lopez", "Novak", "Ibrahim"]

EQUIP_CATEGORIES = ["Patient Bed", "Vital Signs Monitor", "Infusion Pump",
                    "Clinical Workstation", "Nurse Call Station",
                    "Medication Dispensing Cabinet", "Wall Suction / O2 Outlet",
                    "Patient Lift"]
EQUIP_STATUS = ["Ordered", "Delivered", "Installed", "Tested", "Accepted"]
EQUIP_OWNER_DEPT = {
    "Patient Bed": "Supply Chain",
    "Vital Signs Monitor": "Biomedical Engineering",
    "Infusion Pump": "Biomedical Engineering",
    "Clinical Workstation": "IT / Low-Voltage",
    "Nurse Call Station": "IT / Low-Voltage",
    "Medication Dispensing Cabinet": "Pharmacy",
    "Wall Suction / O2 Outlet": "Facilities",
    "Patient Lift": "Facilities",
}

CHECK_CATEGORIES = {
    "Construction Punch List": "Facilities",
    "Low-Voltage / Network": "IT / Low-Voltage",
    "Biomed Equipment Check": "Biomedical Engineering",
    "Furniture & Fixtures": "Supply Chain",
    "Clinical Supplies Stocked": "Supply Chain",
    "Signage & Wayfinding": "Facilities",
    "Life Safety Inspection": "Security",
    "Terminal Clean": "Environmental Services",
    "Staff Training / Orientation": "Nursing",
    "Clinical Workflow Validation": "Nursing",
}
CHECK_DESCRIPTIONS = {
    "Construction Punch List": ["Patch and paint wall behind headwall", "Adjust door closer",
                                "Seal ceiling penetrations", "Replace scratched floor tile"],
    "Low-Voltage / Network": ["Activate data drops", "Test Wi-Fi coverage", "Label patch panel ports",
                              "Verify RTLS badge reader"],
    "Biomed Equipment Check": ["Electrical safety test", "Preventive maintenance tag",
                               "Asset tag and CMMS entry", "Alarm integration test"],
    "Furniture & Fixtures": ["Install overbed table", "Mount whiteboard", "Install privacy curtain",
                             "Deliver visitor chair"],
    "Clinical Supplies Stocked": ["Stock PPE cabinet", "Stock isolation cart", "Stock linen shelf",
                                  "Par-level check"],
    "Signage & Wayfinding": ["Install room number sign", "Install exit signage",
                             "Braille compliance check"],
    "Life Safety Inspection": ["Fire extinguisher inspection", "Sprinkler head clearance",
                               "Emergency power receptacle test", "Med gas alarm test"],
    "Terminal Clean": ["Terminal clean and UV cycle", "ATP swab verification"],
    "Staff Training / Orientation": ["Unit walk-through completed", "Nurse call training",
                                     "Bed controls training"],
    "Clinical Workflow Validation": ["Admission workflow tabletop", "Code blue drill",
                                     "Med admin end-to-end test"],
}
CHECK_STATUS = ["Not Started", "In Progress", "Blocked", "Complete", "Verified"]
BLOCKER_REASONS = ["Waiting on vendor", "Parts back-ordered", "Contractor rework required",
                   "Access restricted by construction", "Awaiting inspection sign-off",
                   "Dependency on another item"]
PRIORITY = ["High", "Medium", "Low"]


def build(seed: int = SEED):
    rng = random.Random(seed)

    # ---- owners ----------------------------------------------------------
    owners = []
    oid = 1
    for dept in DEPARTMENTS:
        for _ in range(rng.choice([2, 3])):
            name = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
            owners.append({
                "owner_id": f"OWN-{oid:03d}",
                "owner_name": name,
                "department": dept,
                "email": name.lower().replace(" ", ".") + "@example-health.org",
            })
            oid += 1
    owners_df = pd.DataFrame(owners)
    owners_by_dept = {d: owners_df[owners_df.department == d].owner_id.tolist()
                      for d in DEPARTMENTS}

    # ---- rooms -----------------------------------------------------------
    rooms = []
    for floor, (unit, count) in FLOORS.items():
        for n in range(1, count + 1):
            rooms.append({
                "room_id": f"T-{floor}{n:02d}",
                "floor": floor,
                "unit": unit,
                "room_type": rng.choice(ROOM_TYPES),
                "square_feet": rng.randint(180, 420),
                "target_activation_date": ACTIVATION - timedelta(days=rng.choice([0, 0, 7, 14])),
            })
    rooms_df = pd.DataFrame(rooms)

    # Floors progress at different rates so the dashboard has a story.
    floor_progress = {3: 0.96, 4: 0.80, 5: 0.55, 6: 0.70, 7: 0.40, 8: 0.62}

    # ---- equipment -------------------------------------------------------
    equipment = []
    eid = 1
    for r in rooms:
        cats = EQUIP_CATEGORIES if r["room_type"] == "Patient Room" else rng.sample(EQUIP_CATEGORIES, 3)
        for cat in cats:
            p = floor_progress[r["floor"]]
            roll = rng.random()
            if roll < p * 0.75:
                status = "Accepted"
            elif roll < p:
                status = rng.choice(["Tested", "Installed"])
            elif roll < p + (1 - p) * 0.5:
                status = "Delivered"
            else:
                status = "Ordered"
            idx = EQUIP_STATUS.index(status)
            ordered = AS_OF - timedelta(days=rng.randint(45, 160))
            delivered = ordered + timedelta(days=rng.randint(10, 40)) if idx >= 1 else None
            installed = delivered + timedelta(days=rng.randint(2, 20)) if idx >= 2 else None
            equipment.append({
                "equipment_id": f"EQ-{eid:04d}",
                "room_id": r["room_id"],
                "category": cat,
                "status": status,
                "owner_id": rng.choice(owners_by_dept[EQUIP_OWNER_DEPT[cat]]),
                "ordered_date": ordered,
                "delivered_date": delivered,
                "installed_date": installed,
            })
            eid += 1
    equipment_df = pd.DataFrame(equipment)

    # ---- checklist items -------------------------------------------------
    items = []
    iid = 1
    for r in rooms:
        p = floor_progress[r["floor"]]
        for cat, dept in CHECK_CATEGORIES.items():
            if cat == "Terminal Clean" and rng.random() < 0.3:
                continue
            roll = rng.random()
            if roll < p * 0.6:
                status = "Verified"
            elif roll < p:
                status = "Complete"
            elif roll < p + (1 - p) * 0.35:
                status = "In Progress"
            elif roll < p + (1 - p) * 0.5:
                status = "Blocked"
            else:
                status = "Not Started"
            created = AS_OF - timedelta(days=rng.randint(3, 100))
            # most items are due ahead of activation; some early-phase items
            # (punch list, low-voltage) were due weeks ago and may be overdue
            if cat in ("Construction Punch List", "Low-Voltage / Network", "Furniture & Fixtures") and rng.random() < 0.5:
                due = created + timedelta(days=rng.randint(14, 45))
            else:
                due = r["target_activation_date"] - timedelta(days=rng.randint(7, 45))
            if status in ("Complete", "Verified"):
                completed = min(created + timedelta(days=rng.randint(1, 40)), AS_OF)
                updated = completed
            else:
                completed = None
                # older open items go stale: last update lags for some
                lag = rng.randint(0, 5) if rng.random() < 0.6 else rng.randint(6, 35)
                updated = max(created, AS_OF - timedelta(days=lag))
            items.append({
                "item_id": f"CHK-{iid:05d}",
                "room_id": r["room_id"],
                "category": cat,
                "description": rng.choice(CHECK_DESCRIPTIONS[cat]),
                "owner_id": rng.choice(owners_by_dept[dept]),
                "status": status,
                "priority": rng.choices(PRIORITY, weights=[3, 5, 2])[0],
                "created_date": created,
                "due_date": due,
                "completed_date": completed,
                "last_updated": updated,
                "blocker_reason": rng.choice(BLOCKER_REASONS) if status == "Blocked" else None,
            })
            iid += 1
    items_df = pd.DataFrame(items)

    return owners_df, rooms_df, equipment_df, items_df


def make_dirty_sample(items_df: pd.DataFrame, rng: random.Random) -> pd.DataFrame:
    """A copy of checklist_items with realistic data problems for the validator demo."""
    d = items_df.head(60).copy()
    d.loc[3, "room_id"] = "T-999"                       # orphan room
    d.loc[5, "owner_id"] = "OWN-ZZZ"                    # orphan owner
    d.loc[7, "status"] = "Done"                         # bad status value
    d.loc[9, "priority"] = "Urgent"                     # bad priority value
    d.loc[11, "due_date"] = "not a date"                # unparseable date
    d.loc[13, "completed_date"] = None
    d.loc[13, "status"] = "Complete"                    # complete with no completed date
    d.loc[15, "created_date"] = date(2027, 1, 1)        # created after due
    d.loc[17, "item_id"] = d.loc[16, "item_id"]         # duplicate id
    d.loc[19, "status"] = "  in progress "              # whitespace / case
    d.loc[21, "owner_id"] = None                        # missing required
    d.loc[23, "status"] = "Blocked"
    d.loc[23, "blocker_reason"] = None                  # blocked without reason (warning)
    d.loc[25, "completed_date"] = date(2030, 5, 5)      # future completion
    d = d.drop(columns=["last_updated"])                # missing column
    return d


def main() -> None:
    owners, rooms, equipment, items = build()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "samples").mkdir(exist_ok=True)
    owners.to_csv(DATA_DIR / "owners.csv", index=False)
    rooms.to_csv(DATA_DIR / "rooms.csv", index=False)
    equipment.to_csv(DATA_DIR / "equipment.csv", index=False)
    items.to_csv(DATA_DIR / "checklist_items.csv", index=False)
    make_dirty_sample(items, random.Random(SEED)).to_csv(
        DATA_DIR / "samples" / "checklist_items_dirty.csv", index=False)
    print(f"owners {len(owners)} | rooms {len(rooms)} | equipment {len(equipment)} | "
          f"checklist items {len(items)}")


if __name__ == "__main__":
    main()
