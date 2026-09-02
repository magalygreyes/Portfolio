# Project Command Center - Build Log

Streamlit + pandas + Plotly portfolio project. Lives at `projects/project-command-center` in the Portfolio repo.
Serves: PMO Analyst, Program Manager, IT BA, Rev Ops.

Workflow per phase: explore, plan, code, commit.

## Phase plan
0. Requirements + data model (docs/requirements.md, docs/data-model.md) - DONE 2026-09-02
1. Seed data generator (make_seed_data.py) + 7 CSVs with ~8% deliberate defects - DONE 2026-09-02
2. Validation layer (validator.py) + metrics module (metrics.py) + config.py thresholds - DONE 2026-09-02
3. App shell: sidebar filters, Overview page with KPI tiles and project table - DONE 2026-09-02
4. Budget page + Prioritization page with weight sliders
5. Capacity page with burnout flags + Project Detail drill-down
6. Data Quality panel, CSV downloads, README, deploy to Streamlit Community Cloud

## Phase 0 result
Seven entities / CSVs: project_managers, projects, status_updates, budget_lines, milestones, risks, capacity (PM availability rides on capacity rows).
Nine KPIs (K1 to K9), traffic light only (red/yellow/green).
Priority score = weighted 1-5 inputs, risk and effort inverted, scaled 0-100. Defaults 30/30/20/10/10.
Burnout flag: >100% utilization this week or >90% for 4+ consecutive weeks.
Q2 decided: capacity in hours.

## Phase 1 result
`py -3.12 make_seed_data.py` writes data/ (seed 42, deterministic).
Rows: project_managers 10, projects 50, status_updates 902, budget_lines 308, milestones 200, risks 139, capacity 821.
Note: OneDrive blocked Python from creating data/ on the Lenovo; CSVs were generated in the Claude session and dropped in. Fix for next time: right-click the project folder > "Always keep on this device".
31 active projects. Stale projects (no update 4 wks): PRJ-014, PRJ-020, PRJ-037.
PM utilization by design: PM-002 ~106%, PM-007 ~109% (overloaded); PM-009 ~48% (underused); others 66 to 87%.
189 deliberate defects logged in data/_defect_log.csv (bad FKs, duplicates, negatives, bad dates, values outside lists, whitespace/casing).

## Phase 2 result
`validator.load_and_validate(data_dir)` returns `(clean, issues, summary)`.
On seed data: 314 findings (179 reject, 99 warn, 36 silent fix). Every one of the 189 planted defects is caught.
Rows out: projects 47, status_updates 836, budget_lines 280, milestones 179, risks 125, capacity 775.
`metrics.project_metrics(clean)` gives one row per project with health, slip, budget variance, burn, CPI, EAC, risk exposure, priority score, traffic lights, and suggested_health.
`metrics.pm_capacity(clean)` gives weekly utilization plus a per-PM summary with burnout flags.
`metrics.portfolio_kpis(...)` gives K1 to K9 with lights.
Seed-data story: 31 active, Green share 41.9% (Red), on-time 48.4% (Red), budget variance -5% (Green), 3 stale, PM-002 at 119% and PM-007 4 weeks over 90% (both burnout flags).
Run `py -3.12 validator.py` and `py -3.12 metrics.py` from the project folder to see the summaries.

## Phase 3 result
`py -3.12 -m streamlit run app.py` opens the dashboard at http://localhost:8501.
app.py: single file, page picked from sidebar radio. Sidebar filters (portfolio, department, PM, health, phase, active only) apply to every page. Priority weight sliders live in a sidebar expander and feed metrics.priority_score live.
Overview page: 8 KPI tiles with traffic-light left border, health-by-department stacked bar (Plotly, status colors, count labels), "what changed this week" list (prior health -> current health with the update narrative), stale warning, sortable project table with progress bars for priority and % done, CSV download.
Data Quality page built early (summary table + findings by severity + download).
Theme: .streamlit/config.toml, blue accent #2563EB, navy text #1E293B, Space Grotesk headings, Inter body. Yellow status is #D97706 (darker amber passes contrast against white; #F9A825 did not).
Budget, Prioritization, Capacity, Project Detail pages are placeholders until Phases 4 and 5.
