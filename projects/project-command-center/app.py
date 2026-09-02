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
    page_placeholder("Budget vs. Actual", 4)
elif page == "Prioritization":
    page_placeholder("Prioritization", 4)
elif page == "Capacity":
    page_placeholder("PM Capacity", 5)
elif page == "Project Detail":
    page_placeholder("Project Detail", 5)
elif page == "Data Quality":
    page_data_quality()
