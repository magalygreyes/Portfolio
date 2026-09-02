"""
config.py
Single source of truth for allowed values, thresholds, and defaults.
Every page and module imports from here so the math and colors match everywhere.
See docs/requirements.md section 4 and docs/data-model.md section 5.
"""

from datetime import date

# "Today" for the dashboard. Fixed so the seed data tells the same story every run.
# Set to None to use the real current date.
AS_OF = date(2026, 9, 2)

DATA_DIR = "data"

# ---------------------------------------------------------------- Allowed values
DEPARTMENTS = ["IT Infrastructure", "Applications", "Data & Analytics", "Security", "Business Systems"]
PORTFOLIOS = ["Run", "Grow", "Transform"]
PHASES = ["Backlog", "Planning", "Executing", "Closing", "On Hold", "Complete", "Cancelled"]
ACTIVE_PHASES = ["Planning", "Executing", "Closing"]
HEALTH = ["Green", "Yellow", "Red"]
PM_LEVELS = ["Associate PM", "PM", "Senior PM", "Program Manager"]
MILESTONE_STATUS = ["Not Started", "In Progress", "Complete", "Missed"]
RISK_STATUS = ["Open", "Mitigating", "Closed"]

# ---------------------------------------------------------------- Priority score
# Weights must sum to 1.0. Risk and effort are inverted inside metrics.priority_score.
PRIORITY_WEIGHTS = {
    "alignment": 0.30,
    "value": 0.30,
    "urgency": 0.20,
    "risk": 0.10,
    "effort": 0.10,
}

# ---------------------------------------------------------------- Rules
STALE_DAYS = 14                 # no status update in this many days = stale
BURNOUT_WEEK_PCT = 100          # over this in the current week = burnout flag
BURNOUT_STREAK_PCT = 90         # over this for BURNOUT_STREAK_WEEKS in a row = burnout flag
BURNOUT_STREAK_WEEKS = 4

# ---------------------------------------------------------------- Traffic lights
# Each entry: (green_test, yellow_test). Anything else is Red.
# Tests are written as lambdas so metrics.traffic_light() can apply them uniformly.
THRESHOLDS = {
    "budget_variance_pct": {
        "green": lambda v: -10 <= v <= 10,
        "yellow": lambda v: 10 < v <= 20 or v < -10,
    },
    "burn_vs_progress": {
        "green": lambda v: abs(v) <= 10,
        "yellow": lambda v: 10 < abs(v) <= 20,
    },
    "slip_days": {
        "green": lambda v: v <= 0,
        "yellow": lambda v: 0 < v <= 14,
    },
    "risk_exposure": {
        "green": lambda v: v < 8,
        "yellow": lambda v: 8 <= v <= 15,
    },
    "pm_utilization_pct": {
        "green": lambda v: 60 <= v <= 85,
        "yellow": lambda v: (85 < v <= 100) or (v < 60),
    },
    "days_since_update": {
        "green": lambda v: v <= 14,
        "yellow": lambda v: 14 < v <= 21,
    },
    # Portfolio-level KPIs
    "green_share_pct": {
        "green": lambda v: v >= 70,
        "yellow": lambda v: 50 <= v < 70,
    },
    "on_time_pct": {
        "green": lambda v: v >= 80,
        "yellow": lambda v: 60 <= v < 80,
    },
    "stale_count": {
        "green": lambda v: v == 0,
        "yellow": lambda v: 1 <= v <= 3,
    },
}

# Colors (traffic light only, per design rule)
COLORS = {"Green": "#2E7D32", "Yellow": "#D97706", "Red": "#C62828", "Grey": "#9E9E9E"}
ACCENT = "#2563EB"          # blue accent for non-status marks
INK = "#1E293B"             # navy text
SURFACE = "#F8FAF8"         # warm white background
