"""
metrics.py
Every derived number in the dashboard is calculated here, once, from the
clean tables that validator.py returns. Pages only display; they never do math.

Main entry points:
    project_metrics(clean, weights=None, as_of=None) -> DataFrame, one row per project
    pm_capacity(clean, as_of=None)                    -> (weekly DataFrame, per-PM summary DataFrame)
    portfolio_kpis(projects_df, pm_summary_df)        -> dict of KPI name -> {"value", "light"}
    priority_score(row_or_df, weights)                -> Series of 0..100 scores
    traffic_light(metric_name, value)                 -> "Green" | "Yellow" | "Red"

Definitions: docs/data-model.md sections 3 to 5.
"""

import pandas as pd

import config as cfg


# ---------------------------------------------------------------- Helpers
def _as_of(as_of):
    if as_of is not None:
        return pd.Timestamp(as_of)
    return pd.Timestamp(cfg.AS_OF) if cfg.AS_OF else pd.Timestamp.today().normalize()


def traffic_light(metric, value):
    """Map a metric value to Green / Yellow / Red using config.THRESHOLDS."""
    if value is None or pd.isna(value):
        return "Grey"
    rules = cfg.THRESHOLDS[metric]
    if rules["green"](value):
        return "Green"
    if rules["yellow"](value):
        return "Yellow"
    return "Red"


def _worst(*lights):
    order = {"Red": 3, "Yellow": 2, "Green": 1, "Grey": 0}
    return max(lights, key=lambda x: order.get(x, 0))


# ---------------------------------------------------------------- Priority
def priority_score(df, weights=None):
    """
    Weighted 1..5 inputs, risk and effort inverted, scaled to 0..100.
    weights: dict with keys alignment, value, urgency, risk, effort (must sum to 1).
    """
    w = weights or cfg.PRIORITY_WEIGHTS
    total = sum(w.values())
    if abs(total - 1.0) > 1e-6:
        w = {k: v / total for k, v in w.items()}          # normalize defensively
    weighted = (
        w["alignment"] * df["score_alignment"]
        + w["value"] * df["score_value"]
        + w["urgency"] * df["score_urgency"]
        + w["risk"] * (6 - df["score_risk"])
        + w["effort"] * (6 - df["score_effort"])
    )
    return ((weighted - 1) / 4 * 100).round(1)


# ---------------------------------------------------------------- Project level
def project_metrics(clean, weights=None, as_of=None):
    today = _as_of(as_of)
    month_start = today.replace(day=1)
    p = clean["projects"].copy()
    su = clean["status_updates"]
    bl = clean["budget_lines"]
    rk = clean["risks"]
    pm = clean["project_managers"][["pm_id", "pm_name"]]

    p = p.merge(pm, on="pm_id", how="left")
    p["is_active"] = p["phase"].isin(cfg.ACTIVE_PHASES)

    # Current status = latest update per project
    latest = (su.sort_values("update_date").groupby("project_id").tail(1)
                .set_index("project_id")[["update_date", "health", "pct_complete", "summary"]])
    p = p.merge(latest.rename(columns={"update_date": "last_update_date", "health": "current_health",
                                       "summary": "last_summary"}),
                left_on="project_id", right_index=True, how="left")
    p["days_since_update"] = (today - p["last_update_date"]).dt.days
    p["is_stale"] = p["is_active"] & (p["days_since_update"].isna() | (p["days_since_update"] > cfg.STALE_DAYS))

    # Health change vs prior update
    prior = (su.sort_values("update_date").groupby("project_id").nth(-2)
               .set_index("project_id")["health"].rename("prior_health"))
    p = p.merge(prior, left_on="project_id", right_index=True, how="left")
    p["health_changed"] = p["prior_health"].notna() & (p["prior_health"] != p["current_health"])

    # Schedule
    p["slip_days"] = (p["forecast_finish"] - p["baseline_finish"]).dt.days
    p["on_time"] = p["slip_days"] <= 0

    # Budget
    to_date = bl[bl["month"] <= month_start].groupby("project_id").agg(
        planned_to_date=("planned", "sum"), actual_to_date=("actual", "sum"))
    p = p.merge(to_date, left_on="project_id", right_index=True, how="left")
    p[["planned_to_date", "actual_to_date"]] = p[["planned_to_date", "actual_to_date"]].fillna(0)
    p["budget_variance_pct"] = ((p["actual_to_date"] - p["planned_to_date"])
                                / p["planned_to_date"].replace(0, float("nan")) * 100).astype(float).round(1)
    p["burn_pct"] = (p["actual_to_date"] / p["approved_budget"].replace(0, float("nan")) * 100).astype(float).round(1)
    p["burn_vs_progress"] = (p["burn_pct"] - p["pct_complete"]).round(1)
    p["cpi"] = (p["planned_to_date"] / p["actual_to_date"].replace(0, float("nan"))).astype(float).round(2)
    remaining = p["approved_budget"] - p["planned_to_date"]
    p["eac"] = (p["actual_to_date"] + remaining / p["cpi"]).round(0)
    p.loc[p["cpi"].isna(), "eac"] = p["approved_budget"]
    p["over_budget_forecast"] = p["eac"] > p["approved_budget"]

    # Risk
    open_risks = rk[rk["status"] != "Closed"].copy()
    open_risks["exposure"] = open_risks["probability"] * open_risks["impact"]
    exp = open_risks.groupby("project_id").agg(risk_exposure=("exposure", "sum"), open_risks=("risk_id", "count"))
    p = p.merge(exp, left_on="project_id", right_index=True, how="left")
    p[["risk_exposure", "open_risks"]] = p[["risk_exposure", "open_risks"]].fillna(0)

    # Priority
    p["priority_score"] = priority_score(p, weights)

    # Lights
    p["light_budget"] = p["budget_variance_pct"].map(lambda v: traffic_light("budget_variance_pct", v))
    p["light_burn"] = p["burn_vs_progress"].map(lambda v: traffic_light("burn_vs_progress", v))
    p["light_schedule"] = p["slip_days"].map(lambda v: traffic_light("slip_days", v))
    p["light_risk"] = p["risk_exposure"].map(lambda v: traffic_light("risk_exposure", v))
    p["light_update"] = p["days_since_update"].map(lambda v: traffic_light("days_since_update", v))
    p["suggested_health"] = [
        _worst(a, b, c) for a, b, c in zip(p["light_budget"], p["light_schedule"], p["light_risk"])
    ]
    p["health_disagrees"] = p["current_health"].notna() & (p["suggested_health"] != p["current_health"])

    return p


# ---------------------------------------------------------------- Capacity
def pm_capacity(clean, as_of=None):
    """
    Returns
      weekly : one row per PM per week (allocated, available, utilization_pct, light)
      summary: one row per PM (current week utilization, streak, burnout flag, active project count)
    """
    today = _as_of(as_of)
    current_week = today - pd.Timedelta(days=today.weekday())
    cap = clean["capacity"]
    pms = clean["project_managers"]

    weekly = (cap.groupby(["pm_id", "week_start"])
                .agg(allocated_hours=("allocated_hours", "sum"),
                     available_hours=("available_hours", "first"),
                     project_count=("project_id", "nunique"))
                .reset_index())
    weekly["utilization_pct"] = (weekly["allocated_hours"] / weekly["available_hours"].replace(0, float("nan"))
                                 * 100).astype(float).round(1)
    weekly["light"] = weekly["utilization_pct"].map(lambda v: traffic_light("pm_utilization_pct", v))
    weekly = weekly.sort_values(["pm_id", "week_start"])

    # Streak of consecutive weeks above BURNOUT_STREAK_PCT, ending at the latest week
    def streak(s):
        n = 0
        for v in reversed(s.tolist()):
            if pd.notna(v) and v > cfg.BURNOUT_STREAK_PCT:
                n += 1
            else:
                break
        return n

    rows = []
    for pm_id, g in weekly.groupby("pm_id"):
        latest = g[g["week_start"] <= current_week].tail(1)
        cur_util = float(latest["utilization_pct"].iloc[0]) if len(latest) else float("nan")
        cur_alloc = float(latest["allocated_hours"].iloc[0]) if len(latest) else 0.0
        cur_avail = float(latest["available_hours"].iloc[0]) if len(latest) else 0.0
        st = streak(g["utilization_pct"])
        rows.append({
            "pm_id": pm_id,
            "current_week": latest["week_start"].iloc[0] if len(latest) else pd.NaT,
            "allocated_hours": cur_alloc,
            "available_hours": cur_avail,
            "utilization_pct": cur_util,
            "avg_utilization_pct": round(g["utilization_pct"].mean(), 1),
            "weeks_over_90": st,
            "active_projects": int(latest["project_count"].iloc[0]) if len(latest) else 0,
            "burnout_flag": (pd.notna(cur_util) and cur_util > cfg.BURNOUT_WEEK_PCT)
                            or st >= cfg.BURNOUT_STREAK_WEEKS,
        })
    summary = pd.DataFrame(rows).merge(pms[["pm_id", "pm_name", "department", "level"]], on="pm_id", how="right")
    summary["utilization_pct"] = summary["utilization_pct"].fillna(0)
    summary["light"] = summary["utilization_pct"].map(lambda v: traffic_light("pm_utilization_pct", v))
    summary["burnout_flag"] = summary["burnout_flag"].fillna(False).astype(bool)
    return weekly, summary


# ---------------------------------------------------------------- Portfolio KPIs
def portfolio_kpis(projects, pm_summary):
    """
    projects  : output of project_metrics (already filtered by the page if needed)
    pm_summary: second output of pm_capacity
    Returns dict: kpi -> {"value": number, "light": color, "label": text}
    """
    act = projects[projects["is_active"]]
    n = len(act)
    k = {}

    green_share = (act["current_health"] == "Green").sum() / n * 100 if n else 0
    k["K1_health_mix"] = {
        "label": "Green share of active projects",
        "value": round(green_share, 1),
        "light": traffic_light("green_share_pct", green_share),
        "detail": act["current_health"].value_counts().reindex(cfg.HEALTH, fill_value=0).to_dict(),
    }
    on_time = act["on_time"].mean() * 100 if n else 0
    k["K2_on_time"] = {"label": "On-time rate", "value": round(on_time, 1),
                       "light": traffic_light("on_time_pct", on_time)}

    planned = act["planned_to_date"].sum()
    actual = act["actual_to_date"].sum()
    var = (actual - planned) / planned * 100 if planned else 0
    k["K3_budget_variance"] = {"label": "Budget variance to date", "value": round(var, 1),
                               "light": traffic_light("budget_variance_pct", var),
                               "detail": {"planned": planned, "actual": actual}}

    burn = act["burn_vs_progress"].mean() if n else 0
    k["K4_burn_vs_progress"] = {"label": "Avg burn vs progress (pts)", "value": round(burn, 1),
                                "light": traffic_light("burn_vs_progress", burn)}

    slip = act["slip_days"].mean() if n else 0
    k["K5_avg_slip"] = {"label": "Avg schedule slip (days)", "value": round(slip, 1),
                        "light": traffic_light("slip_days", slip)}

    exposure = act["risk_exposure"].mean() if n else 0
    k["K6_risk_exposure"] = {"label": "Avg risk exposure", "value": round(exposure, 1),
                             "light": traffic_light("risk_exposure", exposure)}

    util = pm_summary["utilization_pct"].mean() if len(pm_summary) else 0
    k["K7_pm_utilization"] = {"label": "Avg PM utilization", "value": round(util, 1),
                              "light": traffic_light("pm_utilization_pct", util),
                              "detail": {"burnout_flags": int(pm_summary["burnout_flag"].sum())}}

    stale = int(act["is_stale"].sum())
    k["K8_stale"] = {"label": "Stale status reports", "value": stale,
                     "light": traffic_light("stale_count", stale)}

    k["K9_active_count"] = {"label": "Active projects", "value": n, "light": "Grey"}
    return k


if __name__ == "__main__":
    import warnings
    warnings.simplefilter("ignore")
    from validator import load_and_validate

    clean, issues, summary = load_and_validate()
    proj = project_metrics(clean)
    weekly, pms = pm_capacity(clean)
    kpis = portfolio_kpis(proj, pms)

    print("Portfolio KPIs")
    for key, v in kpis.items():
        print(f"  {key:<22} {v['value']:>8}  {v['light']}")
    print("\nTop 5 by priority")
    cols = ["project_id", "project_name", "pm_name", "current_health", "priority_score", "budget_variance_pct", "slip_days"]
    print(proj[proj.is_active].sort_values("priority_score", ascending=False)[cols].head(5).to_string(index=False))
    print("\nPM capacity (current week)")
    print(pms[["pm_id", "pm_name", "allocated_hours", "available_hours", "utilization_pct", "weeks_over_90", "burnout_flag", "light"]]
          .to_string(index=False))
