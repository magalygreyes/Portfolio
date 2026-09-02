"""Tower Activation Readiness Dashboard.

Run:  streamlit run app.py
"""

from __future__ import annotations

import sys
from io import BytesIO
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import metrics as m          # noqa: E402
import validate as v         # noqa: E402

DATA_DIR = ROOT / "data"
TABLES = ["rooms", "owners", "equipment", "checklist_items"]

# ---- palette ---------------------------------------------------------------
BLUE = "#2a78d6"
BLUE_RAMP = ["#dbe8f9", "#a9c8f0", "#6fa3e5", "#2a78d6", "#1a4f9c"]
INK = "#1f2937"
MUTED = "#6b7280"
GRID = "#e5e7eb"
STATUS = {"good": "#0ca30c", "warning": "#fab219", "critical": "#d03b3b"}
STATE_COLORS = {"Ready": STATUS["good"], "Nearly ready": STATUS["warning"],
                "Not ready": "#a9c8f0", "Blocked": STATUS["critical"]}
ITEM_STATUS_COLORS = {"Verified": "#1a4f9c", "Complete": BLUE, "In Progress": "#a9c8f0",
                      "Not Started": "#dbe8f9", "Blocked": STATUS["critical"]}
AGE_COLORS = dict(zip(m.AGE_LABELS, BLUE_RAMP))

st.set_page_config(page_title="Tower Activation Readiness", page_icon="🏥",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
  .block-container {padding-top: 1.6rem; padding-bottom: 2rem; max-width: 1400px;}
  h1 {font-size: 1.75rem !important; letter-spacing: -0.01em;}
  [data-testid="stMetric"] {background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 10px;
                            padding: 12px 16px;}
  [data-testid="stMetricLabel"] p {color: #6b7280; font-size: 0.8rem; text-transform: uppercase;
                                   letter-spacing: 0.04em;}
  [data-testid="stMetricValue"] {font-size: 1.7rem;}
  .eyebrow {font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.72rem;
            color: #2a78d6; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 2px;}
  .muted {color: #6b7280; font-size: 0.9rem;}
</style>
""", unsafe_allow_html=True)


# ---- helpers ---------------------------------------------------------------

def style_fig(fig: go.Figure, height: int = 320) -> go.Figure:
    fig.update_layout(
        height=height, margin=dict(l=10, r=10, t=36, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK, size=13), title_font=dict(size=15, color=INK),
        legend=dict(orientation="h", y=-0.18, x=0, title=None, font=dict(size=12)),
        hoverlabel=dict(bgcolor="white", font_size=12),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=GRID, tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED))
    return fig


def pct_bar(df: pd.DataFrame, x: str, title: str, height=320) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=df[x].astype(str), y=df["readiness_pct"], marker_color=BLUE, marker_line_width=0,
        text=df["readiness_pct"].map(lambda p: f"{p:.0f}%"), textposition="outside",
        customdata=df[["done", "total", "blocked", "overdue"]].values,
        hovertemplate="<b>%{x}</b><br>%{y:.1f}% complete<br>%{customdata[0]} of %{customdata[1]} items"
                      "<br>%{customdata[2]} blocked · %{customdata[3]} overdue<extra></extra>",
    ))
    fig.update_layout(title=title, bargap=0.35)
    fig.update_yaxes(range=[0, 112], ticksuffix="%")
    fig.update_traces(marker=dict(cornerradius=4))
    return style_fig(fig, height)


@st.cache_data(show_spinner=False)
def read_bundled() -> dict[str, pd.DataFrame]:
    return {t: pd.read_csv(DATA_DIR / f"{t}.csv", dtype=str) for t in TABLES}


def read_uploads(files: dict) -> dict[str, pd.DataFrame]:
    return {t: pd.read_csv(f, dtype=str) for t, f in files.items() if f is not None}


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    buf = BytesIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()


def findings_table(rep: v.ValidationReport) -> None:
    df = rep.to_frame()
    df["_o"] = (df["level"] != "ERROR").astype(int)
    df = df.sort_values(["_o", "table", "check"]).drop(columns="_o")
    st.dataframe(
        df, use_container_width=True, hide_index=True, height=min(60 + 36 * len(df), 520),
        column_config={"level": "Level", "table": "Table", "check": "Check",
                       "rows_affected": st.column_config.NumberColumn("Rows", format="%d"),
                       "message": st.column_config.TextColumn("Message", width="large"),
                       "examples": st.column_config.TextColumn("Example IDs", width="medium")})


# ---- sidebar: data source ---------------------------------------------------

with st.sidebar:
    st.markdown('<div class="eyebrow">Data source</div>', unsafe_allow_html=True)
    source = st.radio("Data source", ["Bundled sample dataset", "Upload my own CSVs"],
                      label_visibility="collapsed")
    raw: dict[str, pd.DataFrame] = {}
    if source == "Bundled sample dataset":
        raw = read_bundled()
        demo_dirty = st.toggle("Swap in the dirty sample (see validation fail)", value=False,
                               help="Replaces checklist_items with data/samples/checklist_items_dirty.csv")
        if demo_dirty:
            raw = dict(raw)
            raw["checklist_items"] = pd.read_csv(DATA_DIR / "samples" / "checklist_items_dirty.csv", dtype=str)
    else:
        ups = {t: st.file_uploader(f"{t}.csv", type="csv", key=f"up_{t}") for t in TABLES}
        raw = read_uploads(ups)
        if len(raw) < len(TABLES):
            st.info("Upload all four CSVs to run the dashboard. Column specs are on the Validation tab.")

    st.markdown('<div class="eyebrow" style="margin-top:14px">As-of date</div>', unsafe_allow_html=True)
    default_asof = pd.Timestamp("2026-09-01").date()
    if "checklist_items" in raw and "last_updated" in [c.strip().lower() for c in raw["checklist_items"].columns]:
        lu = pd.to_datetime(raw["checklist_items"]["last_updated"], errors="coerce")
        if lu.notna().any():
            default_asof = lu.max().date()
    as_of = pd.Timestamp(st.date_input("As-of date", value=default_asof, label_visibility="collapsed",
                                       help="Aging and overdue calculations are relative to this date."))

# ---- validate --------------------------------------------------------------

st.markdown('<div class="eyebrow">Tower Activation · Facility Readiness</div>', unsafe_allow_html=True)
st.title("Tower Activation Readiness Dashboard")

if len(raw) < len(TABLES):
    st.stop()

report = v.validate(raw, as_of=as_of)
t = report.tables

if not report.ok:
    st.error(f"Validation failed with {len(report.errors)} error type(s). "
             "Readiness cannot be calculated until the data is fixed. See the Validation tab.")
    tab_val, tab_data = st.tabs(["Validation", "Data"])
    with tab_val:
        findings_table(report)
    with tab_data:
        for name, df in t.items():
            st.markdown(f"**{name}** · {len(df):,} rows")
            st.dataframe(df, use_container_width=True, hide_index=True, height=240)
    st.stop()

# ---- enrich + filters -------------------------------------------------------

items_all = m.enrich_items(t["checklist_items"], t["rooms"], t["owners"], as_of)
equip_all = m.enrich_equipment(t["equipment"], t["rooms"], t["owners"])
rooms_all = t["rooms"]

with st.sidebar:
    st.markdown('<div class="eyebrow" style="margin-top:14px">Filters</div>', unsafe_allow_html=True)
    floors = sorted(rooms_all["floor"].dropna().unique().tolist())
    f_floor = st.multiselect("Floor", floors, default=floors)
    units = sorted(rooms_all["unit"].dropna().unique().tolist())
    f_unit = st.multiselect("Unit", units, default=units)
    depts = sorted(t["owners"]["department"].dropna().unique().tolist())
    f_dept = st.multiselect("Owning department", depts, default=depts)
    cats = sorted(items_all["category"].dropna().unique().tolist())
    f_cat = st.multiselect("Checklist category", cats, default=cats)
    st.caption("Synthetic data. No real facility, vendor, or patient information.")

room_mask = rooms_all["floor"].isin(f_floor) & rooms_all["unit"].isin(f_unit)
rooms = rooms_all[room_mask]
items = items_all[items_all["room_id"].isin(rooms["room_id"]) & items_all["department"].isin(f_dept)
                  & items_all["category"].isin(f_cat)]
equip = equip_all[equip_all["room_id"].isin(rooms["room_id"]) & equip_all["department"].isin(f_dept)]

if items.empty:
    st.warning("No checklist items match the current filters.")
    st.stop()

rr = m.room_readiness(items, equip, rooms)
s = m.summary(items, equip, rr)
activation = pd.to_datetime(rooms["target_activation_date"]).min()
days_left = (activation - as_of).days if pd.notna(activation) else None

# ---- header strip ------------------------------------------------------------

sub = f"As of <b>{as_of.date():%b %d, %Y}</b>"
if days_left is not None:
    sub += f" · first activation <b>{activation:%b %d, %Y}</b> ({days_left} days out)"
sub += f" · {len(rooms)} rooms · {s['items_total']:,} checklist items · {s['equip_total']:,} equipment assets"
st.markdown(f'<p class="muted">{sub}</p>', unsafe_allow_html=True)

if report.warnings:
    st.info(f"Data passed validation with {sum(w.count for w in report.warnings)} warning(s). "
            "Details on the Validation tab.", icon="ℹ️")

tab_over, tab_block, tab_age, tab_val, tab_data = st.tabs(
    ["Overview", "Blockers", "Aging", "Validation", "Data"])

# ---- OVERVIEW ----------------------------------------------------------------
with tab_over:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Checklist readiness", f"{s['readiness_pct']:.1f}%",
              f"{s['items_done']:,} of {s['items_total']:,} done", delta_color="off")
    c2.metric("Rooms fully ready", f"{s['rooms_ready']} / {s['rooms_total']}",
              f"{s['rooms_blocked']} rooms blocked", delta_color="inverse" if s['rooms_blocked'] else "off")
    c3.metric("Open blockers", s["blockers"], f"{s['high_priority_open']} high-priority open",
              delta_color="inverse")
    c4.metric("Overdue items", s["overdue"], f"median age {s['median_open_age']:.0f} days",
              delta_color="inverse" if s["overdue"] else "off")
    c5.metric("Equipment accepted", f"{s['equip_pct']:.0f}%",
              f"{s['equip_accepted']:,} of {s['equip_total']:,}", delta_color="off")

    st.write("")
    left, right = st.columns([3, 2])
    with left:
        st.plotly_chart(pct_bar(m.readiness_by(items, "floor").sort_values("floor"), "floor",
                                "Checklist readiness by floor"), use_container_width=True)
    with right:
        counts = rr["state"].value_counts().reindex(["Ready", "Nearly ready", "Not ready", "Blocked"], fill_value=0)
        fig = go.Figure(go.Bar(
            x=counts.values, y=counts.index, orientation="h",
            marker_color=[STATE_COLORS[k] for k in counts.index], marker_line_width=0,
            text=counts.values, textposition="outside",
            hovertemplate="<b>%{y}</b>: %{x} rooms<extra></extra>"))
        fig.update_layout(title="Rooms by readiness state", bargap=0.35)
        fig.update_traces(marker=dict(cornerradius=4))
        fig.update_yaxes(autorange="reversed", showgrid=False)
        fig.update_xaxes(showgrid=True, gridcolor=GRID)
        st.plotly_chart(style_fig(fig), use_container_width=True)
        st.caption("Ready = every item complete and every asset accepted. "
                   "Nearly ready = 80%+ with no blocker. Blocked = at least one blocked item.")

    left, right = st.columns([3, 2])
    with left:
        by_cat = m.readiness_by(items, "category").sort_values("readiness_pct", ascending=False)
        fig = go.Figure(go.Bar(
            y=by_cat["category"], x=by_cat["readiness_pct"], orientation="h", marker_color=BLUE,
            text=by_cat["readiness_pct"].map(lambda p: f"{p:.0f}%"), textposition="outside",
            customdata=by_cat[["done", "total", "blocked", "overdue"]].values,
            hovertemplate="<b>%{y}</b><br>%{x:.1f}% complete<br>%{customdata[0]} of %{customdata[1]} items"
                          "<br>%{customdata[2]} blocked · %{customdata[3]} overdue<extra></extra>"))
        fig.update_layout(title="Checklist readiness by category", bargap=0.3)
        fig.update_traces(marker=dict(cornerradius=4))
        fig.update_yaxes(autorange="reversed", showgrid=False)
        fig.update_xaxes(range=[0, 112], ticksuffix="%", showgrid=True, gridcolor=GRID)
        st.plotly_chart(style_fig(fig, 360), use_container_width=True)
    with right:
        st.markdown("**Rooms furthest from ready**")
        worst = rr.sort_values(["readiness_pct", "items_blocked"], ascending=[True, False]).head(10)
        show = worst[["room_id", "unit", "readiness_pct", "items_blocked", "state"]]
        st.dataframe(
            show, use_container_width=True, hide_index=True, height=360,
            column_config={
                "room_id": "Room", "unit": "Unit",
                "readiness_pct": st.column_config.ProgressColumn("Readiness", format="%.0f%%",
                                                                 min_value=0, max_value=100),
                "items_blocked": "Blocked", "state": "State",
            })

    grid = rr.copy()
    grid["col"] = grid.groupby("floor").cumcount() + 1
    grid["label"] = grid["room_id"]
    grid["color_val"] = grid["readiness_pct"]
    grid.loc[grid["items_blocked"] > 0, "color_val"] = -1
    fig = go.Figure(go.Heatmap(
        x=grid["col"], y=grid["floor"].astype(str), z=grid["color_val"],
        zmin=-1, zmax=100,
        colorscale=[[0, STATUS["critical"]], [0.0099, STATUS["critical"]], [0.01, "#f1f5f9"],
                    [0.5, "#a9c8f0"], [1, "#1a4f9c"]],
        showscale=False, xgap=3, ygap=3,
        customdata=grid[["room_id", "unit", "room_type", "readiness_pct", "items_done", "items_total",
                         "equip_accepted", "equip_total", "items_blocked", "state"]].values,
        hovertemplate="<b>%{customdata[0]}</b> · %{customdata[1]} · %{customdata[2]}"
                      "<br>%{customdata[3]:.0f}% ready · %{customdata[9]}"
                      "<br>Items %{customdata[4]}/%{customdata[5]} · Equipment %{customdata[6]}/%{customdata[7]}"
                      "<br>%{customdata[8]} blocked<extra></extra>"))
    fig.update_layout(height=280, title="Room-by-room readiness")
    fig.update_xaxes(visible=False)
    fig.update_yaxes(title="Floor", showgrid=False, type="category")
    st.plotly_chart(style_fig(fig, 280), use_container_width=True)
    st.caption("Each cell is one room. Hover for detail. Darker blue = closer to ready; red = has a blocker.")

# ---- BLOCKERS --------------------------------------------------------------
with tab_block:
    b = m.blockers(items)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Blocked items", len(b))
    k2.metric("High priority", int((b["priority"] == "High").sum()))
    k3.metric("Rooms affected", b["room_id"].nunique())
    k4.metric("Oldest blocker", f"{int(b['age_days'].max()) if len(b) else 0} days")
    st.write("")

    if len(b):
        left, right = st.columns(2)
        with left:
            reasons = b["blocker_reason"].fillna("(no reason given)").value_counts().reset_index()
            reasons.columns = ["reason", "count"]
            fig = go.Figure(go.Bar(x=reasons["count"], y=reasons["reason"], orientation="h",
                                   marker_color=BLUE, text=reasons["count"], textposition="outside",
                                   hovertemplate="<b>%{y}</b>: %{x} items<extra></extra>"))
            fig.update_layout(title="Blockers by reason", bargap=0.35)
            fig.update_traces(marker=dict(cornerradius=4))
            fig.update_yaxes(autorange="reversed", showgrid=False)
            fig.update_xaxes(showgrid=True, gridcolor=GRID)
            st.plotly_chart(style_fig(fig), use_container_width=True)
        with right:
            by_dept = b.groupby("department").size().sort_values().reset_index(name="count")
            fig = go.Figure(go.Bar(x=by_dept["count"], y=by_dept["department"], orientation="h",
                                   marker_color=BLUE, text=by_dept["count"], textposition="outside",
                                   hovertemplate="<b>%{y}</b>: %{x} items<extra></extra>"))
            fig.update_layout(title="Blockers by owning department", bargap=0.35)
            fig.update_traces(marker=dict(cornerradius=4))
            fig.update_yaxes(showgrid=False)
            fig.update_xaxes(showgrid=True, gridcolor=GRID)
            st.plotly_chart(style_fig(fig), use_container_width=True)

        st.markdown("**Blocked items** · sorted by priority, then age")
        show = b.copy()
        show["due_date"] = show["due_date"].dt.date
        st.dataframe(
            show, use_container_width=True, hide_index=True, height=420,
            column_config={
                "item_id": "Item", "room_id": "Room", "floor": "Floor", "unit": "Unit",
                "category": "Category", "description": "Description", "priority": "Priority",
                "owner_name": "Owner", "department": "Department", "blocker_reason": "Blocker reason",
                "age_days": st.column_config.NumberColumn("Age (days)", format="%d"),
                "days_since_update": st.column_config.NumberColumn("Since update", format="%d"),
                "due_date": "Due", "is_overdue": st.column_config.CheckboxColumn("Overdue"),
            })
        st.download_button("Download blockers CSV", to_csv_bytes(show), "blockers.csv", "text/csv")
    else:
        st.success("No blocked items in the current selection.")

# ---- AGING -------------------------------------------------------------------
with tab_age:
    open_items = items[items["is_open"]]
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Open items", len(open_items))
    a2.metric("Median age", f"{s['median_open_age']:.0f} days")
    a3.metric("Older than 30 days", int((open_items["age_days"] > 30).sum()))
    a4.metric("Stale (no update 14+ days)", s["stale_open"])
    st.write("")

    left, right = st.columns([2, 3])
    with left:
        ag = m.aging(items)
        fig = go.Figure(go.Bar(x=ag["age_bucket"].astype(str), y=ag["open_items"],
                               marker_color=[AGE_COLORS[k] for k in ag["age_bucket"].astype(str)],
                               text=ag["open_items"], textposition="outside",
                               hovertemplate="<b>%{x}</b>: %{y} open items<extra></extra>"))
        fig.update_layout(title="Open items by age", bargap=0.3)
        fig.update_traces(marker=dict(cornerradius=4))
        st.plotly_chart(style_fig(fig), use_container_width=True)
    with right:
        piv = m.aging_by(items, "department")
        fig = go.Figure()
        for i, col in enumerate(m.AGE_LABELS):
            fig.add_bar(name=col, y=piv.index, x=piv[col], orientation="h", marker_color=BLUE_RAMP[i],
                        marker_line=dict(color="white", width=2),
                        hovertemplate="<b>%{y}</b><br>" + col + ": %{x} items<extra></extra>")
        fig.update_layout(barmode="stack", title="Open items by department and age", bargap=0.3)
        fig.update_yaxes(showgrid=False)
        fig.update_xaxes(showgrid=True, gridcolor=GRID)
        st.plotly_chart(style_fig(fig, 340), use_container_width=True)

    st.markdown("**Owner workload** · open items per owner")
    wl = m.owner_workload(items)
    st.dataframe(
        wl, use_container_width=True, hide_index=True, height=380,
        column_config={
            "owner_name": "Owner", "department": "Department",
            "open_items": st.column_config.NumberColumn("Open", format="%d"),
            "blocked": st.column_config.NumberColumn("Blocked", format="%d"),
            "overdue": st.column_config.NumberColumn("Overdue", format="%d"),
            "high_priority": st.column_config.NumberColumn("High priority", format="%d"),
            "oldest_days": st.column_config.NumberColumn("Oldest (days)", format="%d"),
            "median_age": st.column_config.NumberColumn("Median age", format="%d"),
        })

    st.markdown("**Overdue items**")
    od = items[items["is_overdue"]].sort_values("days_overdue", ascending=False)
    if len(od):
        show = od[["item_id", "room_id", "unit", "category", "description", "priority", "owner_name",
                   "status", "due_date", "days_overdue"]].copy()
        show["due_date"] = show["due_date"].dt.date
        st.dataframe(show, use_container_width=True, hide_index=True, height=300,
                     column_config={"item_id": "Item", "room_id": "Room", "unit": "Unit",
                                    "category": "Category", "description": "Description",
                                    "priority": "Priority", "owner_name": "Owner", "status": "Status",
                                    "due_date": "Due",
                                    "days_overdue": st.column_config.NumberColumn("Days overdue", format="%d")})
    else:
        st.success("Nothing overdue in the current selection.")

# ---- VALIDATION --------------------------------------------------------------
with tab_val:
    n_err, n_warn = len(report.errors), len(report.warnings)
    if report.ok and not report.warnings:
        st.success("All four tables passed validation with no findings.")
    elif report.ok:
        st.success(f"Passed. {n_warn} warning type(s), {sum(w.count for w in report.warnings)} rows flagged.")
    st.markdown("**Row counts** · " + " · ".join(f"{k}: {n:,}" for k, n in report.row_counts.items()))
    if report.findings:
        findings_table(report)
    with st.expander("What gets checked"):
        st.markdown("""
| Check | Level | Rule |
|---|---|---|
| `missing_columns` | Error | Required columns must exist |
| `missing_value` | Error | Required fields cannot be blank |
| `duplicate_id` | Error | Primary keys must be unique |
| `invalid_value` | Error | `status` / `priority` must use the allowed vocabulary (case and whitespace are normalised first) |
| `unparseable_date` | Error | Date columns must parse |
| `orphan_room` / `orphan_owner` | Error | Every `room_id` / `owner_id` must exist in the reference table |
| `done_without_date` | Error | Complete or Verified items need a `completed_date` |
| `created_after_due` | Error | `created_date` cannot be later than `due_date` |
| `open_with_completed_date` | Warning | Open item carries a completion date |
| `future_completion` | Warning | `completed_date` is after the as-of date |
| `blocked_without_reason` | Warning | Blocked items should say why |
| `stale_open_item` | Warning | Open item not updated in 14+ days |

**Expected columns**

- `rooms.csv`: room_id, floor, unit, room_type, square_feet, target_activation_date
- `owners.csv`: owner_id, owner_name, department, email
- `equipment.csv`: equipment_id, room_id, category, status, owner_id, ordered_date, delivered_date, installed_date
- `checklist_items.csv`: item_id, room_id, category, description, owner_id, status, priority, created_date, due_date, completed_date, last_updated, blocker_reason
""")

# ---- DATA --------------------------------------------------------------------
with tab_data:
    st.markdown("Cleaned tables after validation, filtered to the current selection.")
    d1, d2 = st.columns(2)
    with d1:
        st.markdown(f"**Room readiness** · {len(rr):,} rows")
        st.dataframe(rr, use_container_width=True, hide_index=True, height=300)
        st.download_button("Download room readiness CSV", to_csv_bytes(rr), "room_readiness.csv", "text/csv")
    with d2:
        st.markdown(f"**Checklist items** · {len(items):,} rows")
        st.dataframe(items.drop(columns=["age_bucket"]), use_container_width=True, hide_index=True, height=300)
        st.download_button("Download checklist CSV", to_csv_bytes(items.drop(columns=["age_bucket"])),
                           "checklist_items_enriched.csv", "text/csv")
    st.markdown(f"**Equipment** · {len(equip):,} rows")
    st.dataframe(equip, use_container_width=True, hide_index=True, height=260)
