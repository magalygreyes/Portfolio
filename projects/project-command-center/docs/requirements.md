# Project Command Center: Requirements

**Version:** 0.1 (draft)
**Date:** 2026-09-02
**Author:** Magaly Gonzalez
**Status:** In review

---

## 1. Purpose

PMO teams track projects in spreadsheets that answer "what is the status" but not "what should we do next."
The Project Command Center treats the project portfolio the way a sales team treats a CRM: every project is a record with a health score, a budget position, a priority rank, and an owner whose workload is visible.

The dashboard answers four questions on one screen:

1. Which projects are at risk, and why?
2. Where is the budget off plan?
3. If we can only fund or staff some projects, which ones come first?
4. Which project managers are overloaded before it becomes a problem?

## 2. Audience and personas

| Persona | What they need from the dashboard | Primary view |
|---|---|---|
| PMO Analyst | Weekly portfolio roll-up, data quality checks, exportable tables for the steering committee deck | Portfolio Overview, Data Quality |
| Program Manager | Health of the programs they own, blockers, budget burn, upcoming milestones | Project Detail, Risks |
| IT Business Analyst | Requirements-to-delivery visibility: which projects are slipping, what changed since last week | Project Detail, Status History |
| Revenue Operations | Which projects unlock revenue, expected value vs. spend, prioritization inputs | Prioritization, Budget |
| PMO Lead / Steering Committee (secondary) | Capacity and burnout risk across PMs, portfolio-level KPIs | Capacity, Portfolio Overview |

## 3. Scope

### In scope (v1)

- Load a portfolio of 40 to 60 fictional IT projects from CSV files.
- Validate and clean the data before any metric is calculated (reuse the validator pattern from the Tower Activation project).
- Portfolio KPIs: health distribution, on-time rate, budget variance, risk exposure, PM utilization.
- Budget vs. actual by project and by month, with variance thresholds.
- Priority score per project using a transparent weighted formula the user can tune with sliders.
- PM capacity view: allocation vs. available hours, with burnout flags.
- Project detail drill-down: status history, milestones, risks, budget lines.
- Filters: portfolio, department, PM, health, phase, date range.
- Downloadable CSV of any filtered table.

### Out of scope (v1)

- Editing records inside the app (read-only dashboard; data lives in CSV).
- Authentication and role-based access.
- Integration with Jira, Asana, Workfront, or ServiceNow.
- Resource management below the PM level (developers, testers).
- Gantt scheduling.

### Candidates for v2

- AI-generated weekly status summary per project (Claude API).
- What-if mode: drop or delay a project and watch capacity and budget recalculate.
- Import from a live source (Google Sheets, SharePoint list).

## 4. Key performance indicators

Every KPI below is defined once here and calculated the same way everywhere in the app.

| # | KPI | Definition | Target | Traffic light |
|---|---|---|---|---|
| K1 | Portfolio health mix | Count of active projects by health (Green / Yellow / Red) | 70%+ Green | Green >= 70% Green; Yellow 50 to 69%; Red < 50% |
| K2 | On-time rate | Active projects whose forecast finish is on or before the baseline finish, divided by active projects | >= 80% | Green >= 80; Yellow 60 to 79; Red < 60 |
| K3 | Budget variance % | (Actual to date minus Planned to date) / Planned to date, portfolio and per project | Within +/- 10% | Green within 10%; Yellow 10 to 20% over; Red > 20% over |
| K4 | Budget burn rate | Actual to date / Total approved budget, compared against schedule % complete | Burn within 10 pts of % complete | Green within 10 pts; Yellow 10 to 20; Red > 20 |
| K5 | Schedule slip (days) | Forecast finish minus baseline finish | <= 0 | Green <= 0; Yellow 1 to 14; Red > 14 |
| K6 | Risk exposure | Sum of (probability x impact) for open risks per project | Trend down | Green < 8; Yellow 8 to 15; Red > 15 |
| K7 | PM utilization % | Sum of allocation hours across a PM's active projects / PM available hours | 70 to 85% | Green 60 to 85; Yellow 85 to 100 or < 60; Red > 100 |
| K8 | Stale status count | Active projects with no status update in 14+ days | 0 | Green 0; Yellow 1 to 3; Red > 3 |
| K9 | Priority coverage | Share of total PM capacity going to top-quartile priority projects | >= 50% | Informational |

Status colors are limited to red, yellow, and green everywhere in the app.

## 5. Functional requirements

Priority uses MoSCoW: **M** must have, **S** should have, **C** could have.

### 5.1 Data loading and validation

| ID | Requirement | Priority |
|---|---|---|
| FR-01 | The app loads projects, project managers, status updates, budget lines, milestones, risks, and capacity from the seven CSV files in `data/`. | M |
| FR-02 | A validation layer runs before any calculation and returns clean rows, rejected rows with a reason, and a summary count. | M |
| FR-03 | Rejection rules: missing or duplicate `project_id`, unknown `pm_id`, unknown health or phase value, negative budget or hours, unreadable dates, finish date before start date. | M |
| FR-04 | Warning rules (kept but flagged): missing sponsor, no status update in 14+ days, allocation over 100% for a PM, actual spend with no planned budget. | M |
| FR-05 | A Data Quality panel shows counts and the rejected rows table with reasons, downloadable as CSV. | S |

### 5.2 Portfolio overview

| ID | Requirement | Priority |
|---|---|---|
| FR-10 | KPI tiles for K1 to K8 at the top of the Overview page, each with traffic-light color. | M |
| FR-11 | Health mix chart by portfolio and by department. | M |
| FR-12 | Sortable project table: name, PM, health, phase, priority score, budget variance %, slip days, last update. | M |
| FR-13 | Global filters in the sidebar: portfolio, department, PM, health, phase, active only. Filters apply to every page. | M |
| FR-14 | "What changed this week" list: projects whose health changed since the prior status update. | S |

### 5.3 Budget vs. actual

| ID | Requirement | Priority |
|---|---|---|
| FR-20 | Planned vs. actual by month, cumulative, per project and for the filtered portfolio. | M |
| FR-21 | Variance table per project with K3 and K4 and traffic-light color. | M |
| FR-22 | Estimate at completion (EAC) = actual to date + (remaining planned x cost performance to date). Shown next to approved budget. | S |
| FR-23 | Highlight projects forecast to exceed approved budget. | S |

### 5.4 Priority scoring

| ID | Requirement | Priority |
|---|---|---|
| FR-30 | Each project has five scored inputs on a 1 to 5 scale: strategic alignment, business value, urgency, risk (higher = riskier), effort (higher = more effort). | M |
| FR-31 | Priority score (0 to 100) = weighted sum where risk and effort are inverted (6 minus score). Default weights: alignment 30%, value 30%, urgency 20%, risk 10%, effort 10%. | M |
| FR-32 | Weights are adjustable with sidebar sliders; the ranked list updates live and the formula is shown on screen. | M |
| FR-33 | Prioritization matrix chart: value (x) vs. effort (y), bubble size = approved budget, color = health. | S |
| FR-34 | Ranked list shows cumulative PM hours and cumulative budget so the user can see where a funding line would fall. | S |

### 5.5 Capacity and burnout

| ID | Requirement | Priority |
|---|---|---|
| FR-40 | Each PM has weekly available hours (default 40, adjustable per person, reduced by planned time off). | M |
| FR-41 | Each project assignment has weekly allocated hours to a PM. Utilization = allocated / available. | M |
| FR-42 | Capacity page: bar per PM with allocated vs. available hours, traffic-light color per K7. | M |
| FR-43 | Burnout flag when a PM is over 100% for the current week or over 90% for 4+ consecutive weeks. | M |
| FR-44 | Per-PM breakdown: which projects consume their hours, sorted by hours. | S |
| FR-45 | Suggested rebalancing: list PMs under 60% who could absorb work in the same department. | C |

### 5.6 Project detail

| ID | Requirement | Priority |
|---|---|---|
| FR-50 | Select a project to see header (PM, sponsor, phase, health, dates), KPIs, status history, milestones, risks, and budget lines. | M |
| FR-51 | Status history shows health over time as a timeline with the update narrative. | S |
| FR-52 | Milestone table with baseline date, forecast date, and slip. | M |
| FR-53 | Open risks table with probability, impact, exposure, owner, mitigation. | M |

### 5.7 Export

| ID | Requirement | Priority |
|---|---|---|
| FR-60 | Every table has a "Download CSV" button reflecting current filters. | S |

## 6. Non-functional requirements

| ID | Requirement |
|---|---|
| NFR-01 | Built with Python 3.12, Streamlit, pandas, Plotly. No database required for v1. |
| NFR-02 | Page loads in under 3 seconds with 60 projects and 12 months of budget data (use `st.cache_data`). |
| NFR-03 | All metric definitions live in one module (`metrics.py`) so every page uses the same math. |
| NFR-04 | Traffic-light thresholds live in one config (`config.py`) and are documented in this file. |
| NFR-05 | Deployable to Streamlit Community Cloud from the Portfolio repo subfolder. |
| NFR-06 | Seed data is fictional. No real company, employee, or client names. |

## 7. Assumptions and constraints

- One PM per project (project owner). Multiple PMs on one project is out of scope for v1.
- Budget is tracked monthly. Weekly capacity is tracked per PM per week.
- "Active" means phase is Planning, Executing, or Closing. Backlog, On Hold, Complete, and Cancelled projects are excluded from KPIs unless the user turns off "active only."
- Health is reported by the PM in the status update. The app does not override it, but it shows a computed "suggested health" next to it when the two disagree (based on K3, K5, K6).
- Planned to date is the sum of planned budget lines through the current month.

## 8. Open questions

| # | Question | Owner | Due |
|---|---|---|---|
| Q1 | Should priority weights be saved between sessions (needs a settings file) or reset each load? | Magaly | Phase 3 |
| Q2 | Should the capacity view use hours or percent allocation? (Docs assume hours; percent is simpler to enter.) | Magaly | Phase 1 |
| Q3 | Is the "suggested health" comparison useful or confusing for a portfolio reviewer? | Magaly | Phase 4 |

## 9. Glossary

- **Baseline:** the approved plan (dates, budget) that actuals are measured against.
- **Forecast:** the current expected date or cost, updated in each status report.
- **EAC:** estimate at completion, the projected total cost.
- **Exposure:** probability times impact, a single number for how much a risk matters.
- **Utilization:** hours committed divided by hours available.
- **RAG / traffic light:** Red, Amber (Yellow), Green health status.
