"""
make_seed_data.py
Generates the seven fictional CSV files for the Project Command Center.

Run from the project folder:
    py -3.12 make_seed_data.py

Output goes to data/. About 8% of rows carry deliberate defects so the
validation layer (Phase 2) has something to catch. Every defect is also
logged to data/_defect_log.csv so results can be checked.

Schema: docs/data-model.md
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

TODAY = date(2026, 9, 2)
CURRENT_WEEK = date(2026, 8, 31)            # Monday of the current week
WEEKS = [CURRENT_WEEK - timedelta(weeks=i) for i in range(25, -1, -1)]  # 26 Mondays
MONTHS = [date(2026, m, 1) for m in range(1, 13)]
DEFECT_RATE = 0.08

OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)

DEPARTMENTS = ["IT Infrastructure", "Applications", "Data & Analytics", "Security", "Business Systems"]
PORTFOLIOS = ["Run", "Grow", "Transform"]
PHASES = ["Backlog", "Planning", "Executing", "Closing", "On Hold", "Complete", "Cancelled"]
ACTIVE = {"Planning", "Executing", "Closing"}
HEALTH = ["Green", "Yellow", "Red"]

FIRST = ["Dana", "Marcus", "Priya", "Elena", "Jordan", "Samir", "Renee", "Victor", "Amara", "Theo"]
LAST = ["Whitfield", "Okafor", "Raman", "Castillo", "Blake", "Haddad", "Lindqvist", "Moreno", "Osei", "Brandt"]
SPONSORS = ["VP Operations", "CIO", "CFO", "VP Sales", "Chief Data Officer", "CISO", "VP Customer Success", ""]

PROJECT_WORDS = {
    "IT Infrastructure": ["Service Desk Migration", "Data Center Exit", "Network Refresh", "Endpoint Modernization",
                          "Backup Platform Replacement", "Cloud Landing Zone", "VoIP Retirement", "Wi-Fi Upgrade",
                          "Server Patching Automation", "DR Site Buildout"],
    "Applications": ["CRM Consolidation", "Billing System Upgrade", "HRIS Rollout", "Intranet Rebuild",
                     "Document Management Migration", "Expense Tool Replacement", "Mobile App v2",
                     "Contract Lifecycle Platform", "Ticketing Portal Redesign", "Legacy App Sunset"],
    "Data & Analytics": ["Warehouse Modernization", "Executive KPI Dashboard", "Customer 360",
                         "Data Quality Program", "Forecasting Model", "Self-Service BI", "Master Data Cleanup",
                         "Pipeline Monitoring", "Revenue Analytics", "Churn Model"],
    "Security": ["Zero Trust Rollout", "MFA Everywhere", "SIEM Replacement", "Vendor Risk Program",
                 "Privileged Access Management", "Phishing Simulation", "Endpoint Detection Upgrade",
                 "Security Awareness Refresh", "Identity Governance", "Log Retention Compliance"],
    "Business Systems": ["Order-to-Cash Automation", "Procurement Workflow", "Finance Close Automation",
                         "Sales Territory Tool", "Partner Portal", "Quote Configurator", "Inventory Sync",
                         "Commission Engine", "Onboarding Workflow", "Compliance Reporting"],
}

MILESTONE_NAMES = ["Requirements Sign-off", "Design Complete", "Build Complete", "UAT Sign-off", "Go-Live"]
RISK_TITLES = ["Key vendor resource unavailable", "Scope creep from stakeholder requests",
               "Integration API not ready", "Data migration volume higher than estimated",
               "Security review backlog", "Budget approval delayed", "SME availability during quarter close",
               "Third-party license renewal gap", "Testing environment instability", "Change management resistance"]
MITIGATIONS = ["Secure backup contractor", "Weekly scope review with sponsor", "Escalate to vendor PM",
               "Phase migration in two waves", "Pre-book review slot", "Prepare fallback funding request",
               "Schedule around close week", "Start renewal 60 days early", "Add env smoke tests", "Run change champion program"]
SUMMARIES = ["On track. No blockers this week.", "Vendor contract delayed; testing start moved.",
             "UAT defects higher than expected, triage in progress.", "Sponsor approved scope change.",
             "Resource conflict with quarter close, two tasks slipped.", "Go-live checklist 80% complete.",
             "Integration issue found, fix in progress.", "Budget re-forecast submitted to finance."]

defects = []


def log_defect(file, key, rule, note=""):
    defects.append({"file": file, "key": key, "rule": rule, "note": note})


def iso(d):
    return d.isoformat() if d else ""


# ---------------------------------------------------------------- PMs
pms = []
for i in range(10):
    dept = DEPARTMENTS[i % 5]
    pms.append({
        "pm_id": f"PM-{i+1:03d}",
        "pm_name": f"{FIRST[i]} {LAST[i]}",
        "department": dept,
        "level": random.choice(["Associate PM", "PM", "Senior PM", "Program Manager"]),
        "default_weekly_hours": 40,
    })
OVERLOADED = {"PM-002", "PM-007"}
UNDERUSED = {"PM-009"}

# ---------------------------------------------------------------- Projects
projects = []
pid = 0
for dept in DEPARTMENTS:
    dept_pms = [p["pm_id"] for p in pms if p["department"] == dept]
    for name in PROJECT_WORDS[dept][:10]:
        pid += 1
        if pid > 48:
            break
        phase = random.choices(PHASES, weights=[3, 5, 16, 4, 3, 5, 1])[0]
        start = date(2026, 1, 5) + timedelta(weeks=random.randint(0, 20))
        length = random.randint(16, 44)
        finish = start + timedelta(weeks=length)
        slip = random.choices([0, 0, 0, 7, 14, 21, 35, -7], k=1)[0]
        pm = random.choice(dept_pms)
        # steer load toward the overloaded PMs and away from the underused one
        if random.random() < 0.35:
            pm = random.choice(sorted(OVERLOADED & set(dept_pms)) or [pm])
        if pm in UNDERUSED and random.random() < 0.7:
            pm = [p for p in dept_pms if p not in UNDERUSED][0]
        projects.append({
            "project_id": f"PRJ-{pid:03d}",
            "project_name": name,
            "portfolio": random.choices(PORTFOLIOS, weights=[3, 4, 3])[0],
            "department": dept,
            "pm_id": pm,
            "sponsor": random.choice(SPONSORS),
            "phase": phase,
            "baseline_start": start,
            "baseline_finish": finish,
            "forecast_finish": finish + timedelta(days=slip),
            "approved_budget": random.randrange(60_000, 900_000, 5_000),
            "score_alignment": random.randint(1, 5),
            "score_value": random.randint(1, 5),
            "score_urgency": random.randint(1, 5),
            "score_risk": random.randint(1, 5),
            "score_effort": random.randint(1, 5),
        })

active_projects = [p for p in projects if p["phase"] in ACTIVE]

# ---------------------------------------------------------------- Status updates
status_updates = []
sid = 0
STALE = set(random.sample([p["project_id"] for p in active_projects], 3))
for p in projects:
    if p["phase"] in ("Backlog", "Cancelled"):
        continue
    weeks = WEEKS if p["phase"] in ACTIVE else WEEKS[:12]
    if p["project_id"] in STALE:
        weeks = weeks[:-4]                      # last update 4 weeks ago
    health = "Green"
    pct = random.randint(0, 20)
    for wk in weeks:
        # health drifts; some projects trend red
        r = random.random()
        if r < 0.12:
            health = random.choice(HEALTH)
        pct = min(100, pct + random.randint(1, 5))
        if p["phase"] == "Complete":
            pct = 100
        sid += 1
        status_updates.append({
            "update_id": f"SU-{sid:04d}",
            "project_id": p["project_id"],
            "update_date": wk + timedelta(days=4),   # Friday
            "health": health,
            "pct_complete": pct,
            "summary": random.choice(SUMMARIES),
        })

# ---------------------------------------------------------------- Budget lines
budget_lines = []
for p in projects:
    if p["phase"] in ("Backlog", "Cancelled"):
        continue
    months_in = [m for m in MONTHS if p["baseline_start"].replace(day=1) <= m <= p["baseline_finish"]]
    if not months_in:
        continue
    per_month = p["approved_budget"] // len(months_in)
    drift = random.choice([0.85, 0.95, 1.0, 1.05, 1.15, 1.3])   # spending tendency
    for m in months_in:
        actual = ""
        if m <= TODAY.replace(day=1) and p["phase"] != "Planning":
            actual = int(per_month * drift * random.uniform(0.8, 1.2))
        budget_lines.append({"project_id": p["project_id"], "month": m, "planned": per_month, "actual": actual})

# ---------------------------------------------------------------- Milestones
milestones = []
mid = 0
for p in projects:
    if p["phase"] in ("Backlog", "Cancelled"):
        continue
    span = (p["baseline_finish"] - p["baseline_start"]).days
    slip_days = (p["forecast_finish"] - p["baseline_finish"]).days
    for i, name in enumerate(MILESTONE_NAMES):
        mid += 1
        base = p["baseline_start"] + timedelta(days=int(span * (i + 1) / 5))
        fc = base + timedelta(days=max(0, slip_days) if i >= 2 else 0)
        if p["phase"] == "Complete":
            status = "Complete"
        elif fc < TODAY:
            status = random.choice(["Complete", "Complete", "Missed"])
        elif base < TODAY <= fc:
            status = "In Progress"
        else:
            status = "Not Started"
        milestones.append({
            "milestone_id": f"MS-{mid:04d}",
            "project_id": p["project_id"],
            "milestone_name": name,
            "baseline_date": base,
            "forecast_date": fc,
            "status": status,
        })

# ---------------------------------------------------------------- Risks
risks = []
rid = 0
for p in projects:
    if p["phase"] in ("Backlog", "Cancelled"):
        continue
    pm_name = next(x["pm_name"] for x in pms if x["pm_id"] == p["pm_id"])
    for k in random.sample(range(10), random.randint(2, 5)):
        rid += 1
        risks.append({
            "risk_id": f"RK-{rid:04d}",
            "project_id": p["project_id"],
            "title": RISK_TITLES[k],
            "probability": random.randint(1, 5),
            "impact": random.randint(1, 5),
            "status": random.choices(["Open", "Mitigating", "Closed"], weights=[5, 3, 3])[0],
            "owner": pm_name if random.random() > 0.15 else "",
            "mitigation": MITIGATIONS[k],
        })

# ---------------------------------------------------------------- Capacity
capacity = []
for pm in pms:
    my_projects = [p for p in active_projects if p["pm_id"] == pm["pm_id"]]
    for wk in WEEKS:
        available = 40
        if random.random() < 0.06:
            available = random.choice([32, 24, 16])      # PTO week
        # weekly target hours per PM, then split across their projects
        if pm["pm_id"] in OVERLOADED:
            target = random.uniform(42, 50)
        elif pm["pm_id"] in UNDERUSED:
            target = random.uniform(16, 22)
        else:
            target = random.uniform(26, 36)
        base = target / max(1, len(my_projects))
        for p in my_projects:
            hrs = round(max(1.0, random.gauss(base, base * 0.15)), 1)
            capacity.append({
                "pm_id": pm["pm_id"],
                "project_id": p["project_id"],
                "week_start": wk,
                "allocated_hours": hrs,
                "available_hours": available,
            })

# ---------------------------------------------------------------- Deliberate defects
def inject_project_defects(rows):
    picks = random.sample(rows, max(1, int(len(rows) * DEFECT_RATE)))
    for r in picks:
        kind = random.choice(["dup_id", "bad_pm", "bad_phase", "neg_budget", "date_order", "bad_score", "ws"])
        if kind == "dup_id":
            dup = dict(r)
            dup["project_name"] += " (copy)"
            rows.append(dup)
            log_defect("projects", r["project_id"], "duplicate project_id")
        elif kind == "bad_pm":
            r["pm_id"] = "PM-999"
            log_defect("projects", r["project_id"], "unknown pm_id")
        elif kind == "bad_phase":
            r["phase"] = "In Flight"
            log_defect("projects", r["project_id"], "phase outside allowed list")
        elif kind == "neg_budget":
            r["approved_budget"] = -r["approved_budget"]
            log_defect("projects", r["project_id"], "negative approved_budget")
        elif kind == "date_order":
            r["baseline_finish"], r["baseline_start"] = r["baseline_start"], r["baseline_finish"]
            log_defect("projects", r["project_id"], "baseline_finish before baseline_start")
        elif kind == "bad_score":
            r["score_value"] = 7
            log_defect("projects", r["project_id"], "score_value outside 1 to 5")
        elif kind == "ws":
            r["phase"] = "  " + r["phase"].lower() + " "
            log_defect("projects", r["project_id"], "whitespace / casing (silent fix expected)")


def inject_status_defects(rows):
    picks = random.sample(rows, int(len(rows) * DEFECT_RATE))
    for r in picks:
        kind = random.choice(["bad_health", "bad_date", "pct_range", "bad_fk", "ws"])
        if kind == "bad_health":
            r["health"] = "Amber"
            log_defect("status_updates", r["update_id"], "health outside allowed list")
        elif kind == "bad_date":
            r["update_date"] = "08/28/2026" if random.random() < 0.5 else "TBD"
            log_defect("status_updates", r["update_id"], "unreadable update_date")
        elif kind == "pct_range":
            r["pct_complete"] = 140
            log_defect("status_updates", r["update_id"], "pct_complete outside 0 to 100")
        elif kind == "bad_fk":
            r["project_id"] = "PRJ-777"
            log_defect("status_updates", r["update_id"], "unknown project_id")
        elif kind == "ws":
            r["health"] = " green"
            log_defect("status_updates", r["update_id"], "whitespace / casing (silent fix expected)")


def inject_budget_defects(rows):
    picks = random.sample(rows, int(len(rows) * DEFECT_RATE))
    for r in picks:
        kind = random.choice(["neg", "dup", "text", "no_plan"])
        key = f"{r['project_id']}|{iso(r['month'])}"
        if kind == "neg":
            r["actual"] = -abs(r["actual"] or 1000)
            log_defect("budget_lines", key, "negative actual")
        elif kind == "dup":
            rows.append(dict(r))
            log_defect("budget_lines", key, "duplicate (project_id, month)")
        elif kind == "text":
            r["planned"] = "n/a"
            log_defect("budget_lines", key, "non-numeric planned")
        elif kind == "no_plan":
            r["planned"] = 0
            r["actual"] = r["actual"] or 5000
            log_defect("budget_lines", key, "actual with no planned budget (warn)")


def inject_risk_defects(rows):
    picks = random.sample(rows, int(len(rows) * DEFECT_RATE))
    for r in picks:
        kind = random.choice(["prob", "status", "fk"])
        if kind == "prob":
            r["probability"] = 0
            log_defect("risks", r["risk_id"], "probability outside 1 to 5")
        elif kind == "status":
            r["status"] = "Pending"
            log_defect("risks", r["risk_id"], "status outside allowed list")
        elif kind == "fk":
            r["project_id"] = "PRJ-888"
            log_defect("risks", r["risk_id"], "unknown project_id")


def inject_capacity_defects(rows):
    picks = random.sample(rows, int(len(rows) * DEFECT_RATE))
    for r in picks:
        kind = random.choice(["neg", "bad_pm", "not_monday", "dup"])
        key = f"{r['pm_id']}|{r['project_id']}|{iso(r['week_start'])}"
        if kind == "neg":
            r["allocated_hours"] = -r["allocated_hours"]
            log_defect("capacity", key, "negative allocated_hours")
        elif kind == "bad_pm":
            r["pm_id"] = "PM-555"
            log_defect("capacity", key, "unknown pm_id")
        elif kind == "not_monday":
            r["week_start"] = r["week_start"] + timedelta(days=2)
            log_defect("capacity", key, "week_start is not a Monday (warn)")
        elif kind == "dup":
            rows.append(dict(r))
            log_defect("capacity", key, "duplicate (pm_id, project_id, week_start)")


def inject_milestone_defects(rows):
    picks = random.sample(rows, int(len(rows) * DEFECT_RATE))
    for r in picks:
        kind = random.choice(["status", "fk", "date"])
        if kind == "status":
            r["status"] = "Done"
            log_defect("milestones", r["milestone_id"], "status outside allowed list")
        elif kind == "fk":
            r["project_id"] = "PRJ-999"
            log_defect("milestones", r["milestone_id"], "unknown project_id")
        elif kind == "date":
            r["forecast_date"] = "2026-13-40"
            log_defect("milestones", r["milestone_id"], "unreadable forecast_date")


inject_project_defects(projects)
inject_status_defects(status_updates)
inject_budget_defects(budget_lines)
inject_risk_defects(risks)
inject_capacity_defects(capacity)
inject_milestone_defects(milestones)

# ---------------------------------------------------------------- Write
def write(name, rows, columns):
    path = OUT / name
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        for r in rows:
            w.writerow({k: (iso(v) if isinstance(v, date) else v) for k, v in r.items()})
    print(f"{name:<24} {len(rows):>6} rows")


write("project_managers.csv", pms, ["pm_id", "pm_name", "department", "level", "default_weekly_hours"])
write("projects.csv", projects, ["project_id", "project_name", "portfolio", "department", "pm_id", "sponsor", "phase",
                                 "baseline_start", "baseline_finish", "forecast_finish", "approved_budget",
                                 "score_alignment", "score_value", "score_urgency", "score_risk", "score_effort"])
write("status_updates.csv", status_updates, ["update_id", "project_id", "update_date", "health", "pct_complete", "summary"])
write("budget_lines.csv", budget_lines, ["project_id", "month", "planned", "actual"])
write("milestones.csv", milestones, ["milestone_id", "project_id", "milestone_name", "baseline_date", "forecast_date", "status"])
write("risks.csv", risks, ["risk_id", "project_id", "title", "probability", "impact", "status", "owner", "mitigation"])
write("capacity.csv", capacity, ["pm_id", "project_id", "week_start", "allocated_hours", "available_hours"])
write("_defect_log.csv", defects, ["file", "key", "rule", "note"])

print(f"\nActive projects: {len(active_projects)}   Stale (no update 4 wks): {sorted(STALE)}")
print(f"Overloaded PMs: {sorted(OVERLOADED)}   Underused PM: {sorted(UNDERUSED)}")
print(f"Deliberate defects: {len(defects)}")
