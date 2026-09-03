"""
app.py
Project Command Center - Streamlit dashboard.

Run from the project folder:
    py -3.12 -m streamlit run app.py

Pages live in this one file and are selected from the sidebar.
All math comes from metrics.py; all rules from config.py. This file only displays.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import config as cfg
from metrics import pm_capacity, portfolio_kpis, project_metrics
from validator import load_and_validate

# ---------------------------------------------------------------- Page setup
st.set_page_config(page_title="Project Command Center", page_icon="📊", layout="wide")

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; color: {cfg.INK}; }}
    h1, h2, h3 {{ font-family: 'Space Grotesk', sans-serif; color: {cfg.INK}; }}
    .kpi {{
        background: white; border: 1px solid #E5E7EB; border-radius: 10px;
        padding: 14px 16px; border-left: 6px solid {cfg.ACCENT};
        min-height: 96px;
    }}
    .kpi .label {{ font-size: 12px; color: #64748B; text-transform: uppercase; letter-spacing: .04em; }}
    .kpi .value {{ font-family: 'Space Grotesk', sans-serif; font-size: 30px; font-weight: 700; line-height: 1.2; }}
    .kpi .sub {{ font-size: 12px; color: #64748B; }}
    .pill {{ display:inline-block; padding:2px 10px; border-radius:999px; color:white; font-size:12px; font-weight:600; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------- Data (cached)
@st.cache_data(show_spinner="Validating data...")
def load(data_dir):
    clean, issues, summary = load_and_validate(data_dir)
    return clean, issues, summary


clean, issues, dq_summary = load(cfg.DATA_DIR)


# ---------------------------------------------------------------- Sidebar
st.sidebar.title("Project Command Center")
page = st.sidebar.radio("Page", ["Overview", "Budget", "Prioritization", "Capacity", "Project Detail", "Data Quality"])

st.sidebar.markdown("---")
st.sidebar.subheader("Filters")
all_projects = clean["projects"]
pm_lookup = clean["project_managers"].set_index("pm_id")["pm_name"].to_dict()

f_portfolio = st.sidebar.multiselect("Portfolio", cfg.PORTFOLIOS, default=cfg.PORTFOLIOS)
f_department = st.sidebar.multiselect("Department", cfg.DEPARTMENTS, default=cfg.DEPARTMENTS)
pm_options = sorted(pm_lookup.items(), key=lambda kv: kv[1])
f_pm = st.sidebar.multiselect("Project manager", [k for k, _ in pm_options],
                              default=[k for k, _ in pm_options], format_func=lambda k: pm_lookup.get(k, k))
f_health = st.sidebar.multiselect("Health", cfg.HEALTH, default=cfg.HEALTH)
f_active = st.sidebar.checkbox("Active projects only", value=True)
f_phase = st.sidebar.multiselect("Phase", cfg.PHASES, default=cfg.ACTIVE_PHASES if f_active else cfg.PHASES)

st.sidebar.markdown("---")
with st.sidebar.expander("Priority weights", expanded=(page == "Prioritization")):
    w = {}
    for key, default in cfg.PRIORITY_WEIGHTS.items():
        w[key] = st.slider(key.capitalize(), 0.0, 1.0, float(default), 0.05, key=f"w_{key}")
    w_total = sum(w.values()) or 1
    weights = {k: v / w_total for k, v in w.items()}
    st.caption("Weights are normalized to 100%. Risk and effort are inverted (lower is better).")

# ---------------------------------------------------------------- Metrics on filtered data
proj_all = project_metrics(clean, weights=weights)
mask = (
    proj_all["portfolio"].isin(f_portfolio)
    & proj_all["department"].isin(f_department)
    & proj_all["pm_id"].isin(f_pm)
    & proj_all["phase"].isin(f_phase)
    & (proj_all["current_health"].isin(f_health) | proj_all["current_health"].isna())
)
proj = proj_all[mask].copy()

weekly_cap, pm_summary_all = pm_capacity(clean)
pm_summary = pm_summary_all[pm_summary_all["pm_id"].isin(f_pm) & pm_summary_all["department"].isin(f_department)]

kpis = portfolio_kpis(proj, pm_summary)


# ---------------------------------------------------------------- Display helpers
def pill(light):
    color = cfg.COLORS.get(light, cfg.COLORS["Grey"])
    return f'<span class="pill" style="background:{color}">{light}</span>'


def kpi_tile(col, label, value, light, sub=""):
    color = cfg.COLORS.get(light, cfg.COLORS["Grey"])
    col.markdown(
        f'<div class="kpi" style="border-left-color:{color}">'
        f'<div class="label">{label}</div>'
        f'<div class="value">{value}</div>'
        f'<div class="sub">{sub}</div></div>',
        unsafe_allow_html=True,
    )


def money(v):
    return f"${v:,.0f}"


def download(df, name):
    st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), file_name=name, mime="text/csv")


PLOT_LAYOUT = dict(
    font=dict(family="Inter, sans-serif", color=cfg.INK, size=13),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(showgrid=True, gridcolor="#E5E7EB", zeroline=False),
    yaxis=dict(showgrid=False, zeroline=False),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, traceorder="normal"),
)


# ================================================================ OVERVIEW
def page_overview():
    st.title("Portfolio Overview")
    st.caption(f"As of {cfg.AS_OF:%B %d, %Y}. {len(proj)} projects in view, {int(proj['is_active'].sum())} active.")

    # KPI tiles
    k = kpis
    c = st.columns(4)
    hm = k["K1_health_mix"]["detail"]
    kpi_tile(c[0], "Green share", f"{k['K1_health_mix']['value']}%", k["K1_health_mix"]["light"],
             f"G {hm['Green']} · Y {hm['Yellow']} · R {hm['Red']}")
    kpi_tile(c[1], "On-time rate", f"{k['K2_on_time']['value']}%", k["K2_on_time"]["light"], "forecast finish ≤ baseline")
    d = k["K3_budget_variance"]["detail"]
    kpi_tile(c[2], "Budget variance", f"{k['K3_budget_variance']['value']:+.1f}%", k["K3_budget_variance"]["light"],
             f"{money(d['actual'])} actual vs {money(d['planned'])} planned")
    kpi_tile(c[3], "Avg schedule slip", f"{k['K5_avg_slip']['value']:.0f} days", k["K5_avg_slip"]["light"], "forecast minus baseline")
    c = st.columns(4)
    kpi_tile(c[0], "Avg risk exposure", f"{k['K6_risk_exposure']['value']}", k["K6_risk_exposure"]["light"], "sum of probability × impact, open risks")
    kpi_tile(c[1], "Avg PM utilization", f"{k['K7_pm_utilization']['value']}%", k["K7_pm_utilization"]["light"],
             f"{k['K7_pm_utilization']['detail']['burnout_flags']} burnout flag(s)")
    kpi_tile(c[2], "Stale status reports", f"{k['K8_stale']['value']}", k["K8_stale"]["light"], f"no update in {cfg.STALE_DAYS}+ days")
    kpi_tile(c[3], "Active projects", f"{k['K9_active_count']['value']}", "Grey", f"of {len(all_projects)} in portfolio")

    st.markdown("")
    left, right = st.columns([3, 2])

    # Health mix by department (stacked horizontal bars, status colors + count labels)
    with left:
        st.subheader("Health by department")
        act = proj[proj["is_active"]]
        mix = (act.groupby(["department", "current_health"]).size()
                  .unstack(fill_value=0).reindex(columns=cfg.HEALTH, fill_value=0)
                  .reindex(cfg.DEPARTMENTS, fill_value=0))
        fig = go.Figure()
        for h in cfg.HEALTH:
            fig.add_bar(
                y=mix.index, x=mix[h], name=h, orientation="h",
                marker=dict(color=cfg.COLORS[h], line=dict(color="white", width=2)),
                text=[str(v) if v else "" for v in mix[h]], textposition="inside",
                textfont=dict(color="white", size=12),
                hovertemplate="%{y}<br>" + h + ": %{x}<extra></extra>",
            )
        fig.update_layout(barmode="stack", height=280, **PLOT_LAYOUT)
        fig.update_yaxes(autorange="reversed")
        fig.update_xaxes(title="Active projects", dtick=2)
        st.plotly_chart(fig, width="stretch")

    # What changed this week
    with right:
        st.subheader("What changed this week")
        changed = proj[proj["health_changed"] & proj["is_active"]].sort_values("last_update_date", ascending=False)
        if changed.empty:
            st.info("No health changes in the latest status updates.")
        else:
            for _, r in changed.head(8).iterrows():
                st.markdown(
                    f"{pill(r['prior_health'])} → {pill(r['current_health'])} &nbsp; "
                    f"**{r['project_name']}** · {r['pm_name']}<br>"
                    f"<span style='color:#64748B;font-size:12px'>{r['last_summary'] or ''}</span>",
                    unsafe_allow_html=True,
                )
        stale = proj[proj["is_stale"]]
        if not stale.empty:
            st.warning(f"Stale: {', '.join(stale['project_name'])} (no update in {cfg.STALE_DAYS}+ days)")

    # Project table
    st.subheader("Projects")
    cols = {
        "project_id": "ID", "project_name": "Project", "pm_name": "PM", "department": "Dept", "phase": "Phase",
        "current_health": "Health", "suggested_health": "Suggested", "priority_score": "Priority",
        "pct_complete": "% done", "budget_variance_pct": "Budget var %", "slip_days": "Slip (d)",
        "risk_exposure": "Risk exp.", "days_since_update": "Days since update",
    }
    table = proj.sort_values("priority_score", ascending=False)[list(cols)].rename(columns=cols)
    st.dataframe(
        table, width="stretch", hide_index=True, height=420,
        column_config={
            "Priority": st.column_config.ProgressColumn(format="%.0f", min_value=0, max_value=100),
            "% done": st.column_config.ProgressColumn(format="%d%%", min_value=0, max_value=100),
            "Budget var %": st.column_config.NumberColumn(format="%+.1f%%"),
        },
    )
    download(table, "projects_filtered.csv")


# ================================================================ BUDGET
def cumulative_budget(project_ids):
    """Monthly planned vs actual, cumulative, for a set of projects."""
    bl = clean["budget_lines"]
    bl = bl[bl["project_id"].isin(project_ids)]
    m = bl.groupby("month").agg(planned=("planned", "sum"), actual=("actual", "sum")).sort_index()
    m["cum_planned"] = m["planned"].cumsum()
    # Actual is only cumulative through months that have any actuals
    has_actual = bl.groupby("month")["actual"].apply(lambda s: s.notna().any())
    in_past = m["month"] <= pd.Timestamp(cfg.AS_OF).replace(day=1)
    m["cum_actual"] = m["actual"].cumsum().where(has_actual & in_past)
    return m.reset_index()


def budget_chart(m, title=""):
    fig = go.Figure()
    fig.add_scatter(x=m["month"], y=m["cum_planned"], name="Planned (cumulative)", mode="lines",
                    line=dict(color="#94A3B8", width=2, dash="dot"),
                    hovertemplate="%{x|%b %Y}<br>Planned: $%{y:,.0f}<extra></extra>")
    fig.add_scatter(x=m["month"], y=m["cum_actual"], name="Actual (cumulative)", mode="lines+markers",
                    line=dict(color=cfg.ACCENT, width=2), marker=dict(size=8, line=dict(color="white", width=2)),
                    hovertemplate="%{x|%b %Y}<br>Actual: $%{y:,.0f}<extra></extra>")
    fig.update_layout(height=320, hovermode="x unified", title=title, **PLOT_LAYOUT)
    fig.update_yaxes(tickprefix="$", tickformat=",.0f", showgrid=True, gridcolor="#E5E7EB")
    fig.update_xaxes(showgrid=False, dtick="M1", tickformat="%b")
    return fig


def page_budget():
    st.title("Budget vs. Actual")
    st.caption("Planned is the baseline by month. Actual fills in as months close. To-date figures run through the current month.")

    k = kpis
    d = k["K3_budget_variance"]["detail"]
    over = proj[proj["is_active"] & proj["over_budget_forecast"]]
    c = st.columns(4)
    kpi_tile(c[0], "Planned to date", money(d["planned"]), "Grey", "sum of monthly plan through this month")
    kpi_tile(c[1], "Actual to date", money(d["actual"]), "Grey", "sum of recorded spend")
    kpi_tile(c[2], "Variance", f"{k['K3_budget_variance']['value']:+.1f}%", k["K3_budget_variance"]["light"],
             "(actual - planned) / planned")
    kpi_tile(c[3], "Forecast over budget", f"{len(over)}", "Red" if len(over) else "Green",
             f"of {int(proj['is_active'].sum())} active, EAC above approved")

    st.markdown("")
    st.subheader("Cumulative spend, filtered portfolio")
    m = cumulative_budget(proj["project_id"])
    if m.empty:
        st.info("No budget lines for the current filter.")
    else:
        st.plotly_chart(budget_chart(m), width="stretch")

    st.subheader("Variance by project")
    cols = {
        "project_id": "ID", "project_name": "Project", "pm_name": "PM", "phase": "Phase",
        "approved_budget": "Approved", "planned_to_date": "Planned to date", "actual_to_date": "Actual to date",
        "budget_variance_pct": "Variance %", "light_budget": "Variance light",
        "pct_complete": "% done", "burn_pct": "Burn %", "burn_vs_progress": "Burn vs progress",
        "cpi": "CPI", "eac": "EAC", "over_budget_forecast": "Over budget?",
    }
    t = proj.sort_values("budget_variance_pct", ascending=False)[list(cols)].rename(columns=cols)
    st.dataframe(
        t, width="stretch", hide_index=True, height=420,
        column_config={
            "Approved": st.column_config.NumberColumn(format="$%,.0f"),
            "Planned to date": st.column_config.NumberColumn(format="$%,.0f"),
            "Actual to date": st.column_config.NumberColumn(format="$%,.0f"),
            "EAC": st.column_config.NumberColumn(format="$%,.0f"),
            "Variance %": st.column_config.NumberColumn(format="%+.1f%%"),
            "Burn %": st.column_config.NumberColumn(format="%.0f%%"),
            "Burn vs progress": st.column_config.NumberColumn(format="%+.0f pts"),
            "% done": st.column_config.ProgressColumn(format="%d%%", min_value=0, max_value=100),
        },
    )
    download(t, "budget_variance.csv")

    st.subheader("One project")
    pick = st.selectbox("Project", proj["project_id"] + " · " + proj["project_name"], key="budget_pick")
    pid = pick.split(" · ")[0]
    row = proj[proj["project_id"] == pid].iloc[0]
    c = st.columns(4)
    kpi_tile(c[0], "Approved", money(row["approved_budget"]), "Grey")
    kpi_tile(c[1], "Actual to date", money(row["actual_to_date"]), row["light_budget"], f"{row['budget_variance_pct']:+.1f}% vs plan")
    kpi_tile(c[2], "EAC", money(row["eac"]), "Red" if row["over_budget_forecast"] else "Green", f"CPI {row['cpi']}")
    kpi_tile(c[3], "Burn vs progress", f"{row['burn_vs_progress']:+.0f} pts", row["light_burn"],
             f"{row['burn_pct']:.0f}% spent, {int(row['pct_complete'])}% done")
    st.plotly_chart(budget_chart(cumulative_budget([pid])), width="stretch")


# ================================================================ PRIORITIZATION
def page_prioritization():
    st.title("Prioritization")
    wtxt = " + ".join(f"{v:.0%} {k}" for k, v in weights.items())
    st.caption(f"Score = {wtxt}, with risk and effort inverted (6 - score), scaled to 0 to 100. "
               "Change the weights in the sidebar and the ranking updates.")

    act = proj[proj["is_active"]].copy()
    # Current-week PM hours per project
    cap = clean["capacity"]
    as_of = pd.Timestamp(cfg.AS_OF)
    cur_week = as_of - pd.Timedelta(days=as_of.weekday())
    hrs = cap[cap["week_start"] == cur_week].groupby("project_id")["allocated_hours"].sum()
    act["pm_hours_week"] = act["project_id"].map(hrs).fillna(0)
    act = act.sort_values("priority_score", ascending=False).reset_index(drop=True)
    act["rank"] = act.index + 1
    act["cum_budget"] = act["approved_budget"].cumsum()
    act["cum_pm_hours"] = act["pm_hours_week"].cumsum()

    left, right = st.columns([3, 2])
    with left:
        st.subheader("Value vs. effort")
        st.caption("Bubble size = approved budget. Color = reported health. Top-left is the sweet spot.")
        fig = go.Figure()
        for h in cfg.HEALTH:
            sub = act[act["current_health"] == h]
            if sub.empty:
                continue
            fig.add_scatter(
                x=sub["score_value"] + (sub["rank"] % 3 - 1) * 0.22,      # jitter so bubbles on the same cell spread out
                y=sub["score_effort"] + (sub["rank"] % 4 - 1.5) * 0.14,
                mode="markers+text", name=h,
                marker=dict(size=sub["approved_budget"] / 25000 + 8, color=cfg.COLORS[h],
                            line=dict(color="white", width=2), opacity=0.85),
                text=sub["project_id"].str.replace("PRJ-", ""), textposition="middle center",
                textfont=dict(color="white", size=10),
                customdata=sub[["project_name", "priority_score", "approved_budget"]],
                hovertemplate="<b>%{customdata[0]}</b><br>Priority %{customdata[1]}<br>"
                              "Budget $%{customdata[2]:,.0f}<br>Value %{x:.0f} · Effort %{y:.0f}<extra></extra>",
            )
        fig.update_layout(height=420, **PLOT_LAYOUT)
        fig.update_xaxes(title="Business value (1 to 5)", range=[0.5, 5.5], dtick=1, showgrid=True, gridcolor="#E5E7EB")
        fig.update_yaxes(title="Effort (1 to 5)", range=[5.5, 0.5], dtick=1, showgrid=True, gridcolor="#E5E7EB")
        st.plotly_chart(fig, width="stretch")

    with right:
        st.subheader("Funding line")
        total_k = int(act["approved_budget"].sum() // 1000)
        cap_k = st.slider("Budget available ($K)", 0, total_k, int(total_k * 0.6), step=50, format="$%dK")
        cap_budget = cap_k * 1000
        funded = act[act["cum_budget"] <= cap_budget]
        unfunded = act[act["cum_budget"] > cap_budget]
        kpi_tile(st, "Projects above the line", f"{len(funded)} of {len(act)}", "Grey",
                 f"{money(funded['approved_budget'].sum())} committed, {money(cap_budget - funded['approved_budget'].sum())} left")
        st.markdown("")
        kpi_tile(st, "PM hours above the line", f"{funded['pm_hours_week'].sum():.0f} h/week", "Grey",
                 f"{unfunded['pm_hours_week'].sum():.0f} h/week freed if the rest pauses")
        if not unfunded.empty:
            st.markdown("")
            st.markdown("**First projects below the line**")
            for _, r in unfunded.head(4).iterrows():
                st.markdown(f"{r['rank']}. {r['project_name']} · {money(r['approved_budget'])} · score {r['priority_score']}")

    st.subheader("Ranked list")
    act["funded"] = act["cum_budget"] <= cap_budget
    cols = {
        "rank": "#", "project_id": "ID", "project_name": "Project", "pm_name": "PM", "portfolio": "Portfolio",
        "priority_score": "Score", "score_alignment": "Align", "score_value": "Value", "score_urgency": "Urgency",
        "score_risk": "Risk", "score_effort": "Effort", "current_health": "Health",
        "approved_budget": "Budget", "cum_budget": "Cum. budget", "pm_hours_week": "PM h/wk", "cum_pm_hours": "Cum. PM h/wk",
        "funded": "Above line",
    }
    t = act[list(cols)].rename(columns=cols)
    st.dataframe(
        t, width="stretch", hide_index=True, height=480,
        column_config={
            "Score": st.column_config.ProgressColumn(format="%.0f", min_value=0, max_value=100),
            "Budget": st.column_config.NumberColumn(format="$%,.0f"),
            "Cum. budget": st.column_config.NumberColumn(format="$%,.0f"),
            "PM h/wk": st.column_config.NumberColumn(format="%.0f"),
            "Cum. PM h/wk": st.column_config.NumberColumn(format="%.0f"),
        },
    )
    download(t, "priority_ranking.csv")


# ================================================================ Placeholders (built in later phases)
def page_placeholder(name, phase):
    st.title(name)
    st.info(f"Coming in Phase {phase}.")


def page_data_quality():
    st.title("Data Quality")
    st.caption("What the validator did before any number was calculated.")
    st.dataframe(dq_summary, width="stretch", hide_index=True)
    sev = st.radio("Show", ["reject", "warn", "fix"], horizontal=True)
    sub = issues[issues["severity"] == sev]
    st.write(f"{len(sub)} findings")
    st.dataframe(sub, width="stretch", hide_index=True, height=400)
    download(sub, f"data_quality_{sev}.csv")


# ---------------------------------------------------------------- Router
if page == "Overview":
    page_overview()
elif page == "Budget":
    page_budget()
elif page == "Prioritization":
    page_prioritization()
elif page == "Capacity":
    page_placeholder("PM Capacity", 5)
elif page == "Project Detail":
    page_placeholder("Project Detail", 5)
elif page == "Data Quality":
    page_data_quality()
