# Project Command Center - Build Log

Streamlit + pandas + Plotly portfolio project. Lives at `projects/project-command-center` in the Portfolio repo.
Serves: PMO Analyst, Program Manager, IT BA, Rev Ops.

Workflow per phase: explore, plan, code, commit.

## Phase plan
0. Requirements + data model (docs/requirements.md, docs/data-model.md) - DONE 2026-09-02
1. Seed data generator (make_seed_data.py) + 7 CSVs with ~8% deliberate defects
2. Validation layer (validator.py) + metrics module (metrics.py) + config.py thresholds
3. App shell: sidebar filters, Overview page with KPI tiles and project table
4. Budget page + Prioritization page with weight sliders
5. Capacity page with burnout flags + Project Detail drill-down
6. Data Quality panel, CSV downloads, README, deploy to Streamlit Community Cloud

## Phase 0 result
Seven entities / CSVs: project_managers, projects, status_updates, budget_lines, milestones, risks, capacity (PM availability rides on capacity rows).
Nine KPIs (K1 to K9), traffic light only (red/yellow/green).
Priority score = weighted 1-5 inputs, risk and effort inverted, scaled 0-100. Defaults 30/30/20/10/10.
Burnout flag: >100% utilization this week or >90% for 4+ consecutive weeks.
Open questions: Q2 (hours vs percent for capacity) must be decided before Phase 1.
