# Project Command Center: User Stories and Acceptance Criteria

**Version:** 1.0
**Date:** 2026-09-22
**Author:** Magaly Gonzalez
**Related documents:** `requirements.md`, `stakeholders.md`, `process-maps.md`, `traceability-matrix.md`

---

## 1. How to read this document

Each story follows the standard form: as a **role**, I want **capability**, so that
**outcome**. Acceptance criteria are written in Given / When / Then so they can be
executed as test cases without translation.

Personas are the stakeholders defined in `stakeholders.md`. Requirement IDs refer to
`requirements.md`. Priority uses MoSCoW: **M** must have, **S** should have, **C** could have.

Story IDs are stable. If a story is dropped, its ID is retired rather than reused.

---

## 2. Epic index

| Epic | Title | Requirements covered | Stories |
|---|---|---|---|
| E1 | Trustworthy data | FR-01 to FR-05 | US-01 to US-04 |
| E2 | Portfolio visibility | FR-10 to FR-14 | US-05 to US-09 |
| E3 | Budget control | FR-20 to FR-23 | US-10 to US-12 |
| E4 | Transparent prioritization | FR-30 to FR-34 | US-13 to US-16 |
| E5 | Capacity and burnout prevention | FR-40 to FR-45 | US-17 to US-20 |
| E6 | Project drill-down | FR-50 to FR-53 | US-21 to US-23 |
| E7 | Export and reuse | FR-60 | US-24 |

---

## 3. Epic E1: Trustworthy data

> Nobody acts on a number they do not trust. Validation comes before every metric,
> and its results are visible rather than hidden.

### US-01: Load the portfolio from a single dataset

**As a** PMO Analyst
**I want** the dashboard to load projects, project managers, status updates, budget
lines, milestones, risks, and capacity from one dataset
**So that** I stop re-keying status updates into a master workbook every week.

**Requirements:** FR-01 · **Priority:** M · **Addresses:** PP-01, PP-02

**Acceptance criteria**

- Given the seven source files are present in `data/`
  When the app starts
  Then all seven load without error and the project count is displayed.

- Given a source file is missing
  When the app starts
  Then a clear error names the missing file, and the app does not display partial
  metrics calculated from incomplete data.

---

### US-02: Reject bad rows before anything is calculated

**As a** PMO Analyst
**I want** validation to run before any KPI is computed
**So that** a typo in one row cannot quietly distort a portfolio number.

**Requirements:** FR-02, FR-03 · **Priority:** M · **Addresses:** PP-03

**Acceptance criteria**

- Given a row has a missing or duplicate `project_id`
  When validation runs
  Then the row is rejected and the reason recorded as a duplicate or missing key.

- Given a row references a `pm_id` that does not exist in the project managers file
  When validation runs
  Then the row is rejected with the reason "unknown pm_id", including the offending value.

- Given a row has a health or phase value outside the allowed list
  When validation runs
  Then the row is rejected and the allowed values are named in the reason.

- Given a row has a negative budget or negative hours
  When validation runs
  Then the row is rejected.

- Given a row has a finish date earlier than its start date, or a date that cannot be parsed
  When validation runs
  Then the row is rejected with a date-specific reason.

- Given any row is rejected
  When KPIs are calculated
  Then no rejected row contributes to any KPI.

---

### US-03: Keep and flag rows that are suspicious but usable

**As a** PMO Analyst
**I want** soft-rule violations flagged rather than discarded
**So that** I can see a problem without losing the project from the portfolio view.

**Requirements:** FR-04 · **Priority:** M · **Addresses:** PP-10

**Acceptance criteria**

- Given an active project has no status update in 14 or more days
  When validation runs
  Then the project is retained, flagged as stale, and counted in KPI K8.

- Given a project manager's total allocation exceeds 100 percent
  When validation runs
  Then the allocation is retained and flagged, and the PM appears in the burnout view.

- Given a project has actual spend but no planned budget
  When validation runs
  Then the row is retained and flagged, and budget variance for that project is
  reported as not calculable rather than as a misleading percentage.

- Given a project has a missing sponsor
  When validation runs
  Then the row is retained and flagged.

---

### US-04: See exactly what was wrong with the data

**As a** PMO Analyst
**I want** a Data Quality panel listing rejected rows with reasons, downloadable as CSV
**So that** I can fix the source data before the steering committee meeting instead
of discovering the problem during it.

**Requirements:** FR-05 · **Priority:** S · **Addresses:** PP-03, PP-08

**Acceptance criteria**

- Given validation has run
  When I open the Data Quality panel
  Then I see counts of rows loaded, rejected, and flagged.

- Given one or more rows were rejected
  When I view the rejected rows table
  Then each row shows its source file, its identifier, and a plain-language reason.

- Given the rejected rows table is displayed
  When I click Download CSV
  Then a CSV downloads containing every rejected row and its reason.

- Given no rows were rejected
  When I open the Data Quality panel
  Then it states that all rows passed, rather than showing an empty table with no explanation.

---

## 4. Epic E2: Portfolio visibility

### US-05: See portfolio health on one screen

**As a** PMO Lead
**I want** KPI tiles for K1 through K8 at the top of the Overview page
**So that** I can assess the portfolio without opening a spreadsheet.

**Requirements:** FR-10 · **Priority:** M · **Addresses:** PP-08

**Acceptance criteria**

- Given the dataset has loaded and validated
  When I open the Overview page
  Then tiles for K1 through K8 are displayed above any chart or table.

- Given a KPI value falls in a defined threshold band
  When the tile renders
  Then its color matches the band in the `requirements.md` KPI table, using only
  red, yellow, or green.

- Given a KPI cannot be calculated because of missing data
  When the tile renders
  Then it shows "not available" with a reason, rather than zero.

---

### US-06: Compare health across portfolios and departments

**As a** PMO Lead
**I want** a health mix chart broken down by portfolio and by department
**So that** I can see whether a problem is isolated or systemic.

**Requirements:** FR-11 · **Priority:** M

**Acceptance criteria**

- Given active projects exist across multiple departments
  When I view the health mix chart
  Then each department shows its Green, Yellow, and Red counts.

- Given I switch the breakdown from department to portfolio
  When the chart re-renders
  Then totals across the chart still equal the active project count.

---

### US-07: Scan every project in one sortable table

**As a** PMO Analyst
**I want** a sortable table of name, PM, health, phase, priority score, budget
variance, slip days, and last update
**So that** I can find the projects that need attention without reading a deck.

**Requirements:** FR-12 · **Priority:** M

**Acceptance criteria**

- Given the Overview page is open
  When I view the project table
  Then all eight columns are present.

- Given I click a column header
  When the table re-sorts
  Then rows order by that column, and clicking again reverses the order.

- Given a project has a Red health value
  When the table renders
  Then the health cell is colored red.

---

### US-08: Filter once and have it apply everywhere

**As a** Program Manager
**I want** sidebar filters for portfolio, department, PM, health, phase, and active
only, applying to every page
**So that** I can look at just my programs without re-filtering on each screen.

**Requirements:** FR-13 · **Priority:** M · **Addresses:** PP-09

**Acceptance criteria**

- Given I set a filter on the Overview page
  When I navigate to Budget, Prioritization, Capacity, or Project Detail
  Then the same filter is still applied.

- Given "active only" is selected
  When any KPI is calculated
  Then projects in Backlog, On Hold, Complete, or Cancelled are excluded.

- Given a filter combination matches no projects
  When any page renders
  Then an empty-state message explains that no projects match, rather than showing
  a blank page or a zero-value KPI.

---

### US-09: See what changed since last week

**As an** IT Business Analyst
**I want** a list of projects whose health changed since the prior status update
**So that** I can focus on movement rather than re-reading the whole portfolio.

**Requirements:** FR-14 · **Priority:** S

**Acceptance criteria**

- Given a project's health differs from its previous status update
  When I view the "what changed this week" list
  Then the project appears with its prior and current health.

- Given a project's health is unchanged
  When the list renders
  Then the project does not appear.

- Given no project changed health
  When the list renders
  Then it states that no health changes occurred.

---

## 5. Epic E3: Budget control

### US-10: Compare planned against actual spend over time

**As a** Finance Business Partner
**I want** cumulative planned vs. actual by month, per project and for the filtered portfolio
**So that** I can see whether a variance is a one-month blip or a trend.

**Requirements:** FR-20 · **Priority:** M · **Addresses:** PP-05

**Acceptance criteria**

- Given budget lines exist for twelve months
  When I view the budget chart
  Then cumulative planned and cumulative actual are plotted on the same axis.

- Given I select a single project
  When the chart re-renders
  Then it shows that project's lines only, and the portfolio total is no longer plotted.

- Given actual data ends before the end of the plan
  When the chart renders
  Then the actual line stops at the last month with data rather than dropping to zero.

---

### US-11: See variance per project with a consistent threshold

**As a** Finance Business Partner
**I want** a variance table using K3 and K4 with traffic-light coloring
**So that** finance and the PMO stop reporting two different variance numbers.

**Requirements:** FR-21 · **Priority:** M · **Addresses:** PP-05

**Acceptance criteria**

- Given a project has planned and actual spend to date
  When the variance table renders
  Then K3 is calculated as (actual minus planned) divided by planned, expressed as a percentage.

- Given K3 exceeds 20 percent over plan
  When the row renders
  Then it is colored red.

- Given the same project appears on the Overview table and the Budget table
  When I compare the two variance figures
  Then they are identical.

---

### US-12: Know which projects will overrun before they do

**As a** Finance Business Partner
**I want** estimate at completion shown next to approved budget, with forecast
overruns highlighted
**So that** I can intervene while the project still has decisions left to make.

**Requirements:** FR-22, FR-23 · **Priority:** S

**Acceptance criteria**

- Given a project has actual spend and remaining planned budget
  When EAC is calculated
  Then EAC equals actual to date plus (remaining planned multiplied by cost performance to date).

- Given EAC exceeds the approved budget
  When the row renders
  Then it is highlighted and the overrun amount is shown.

- Given a project has no actual spend yet
  When EAC is calculated
  Then EAC equals the approved budget rather than zero or an error.

---

## 6. Epic E4: Transparent prioritization

### US-13: Score every project on the same five inputs

**As a** Revenue Operations Lead
**I want** each project scored on strategic alignment, business value, urgency,
risk, and effort
**So that** ranking rests on stated criteria rather than on who argues hardest.

**Requirements:** FR-30 · **Priority:** M · **Addresses:** PP-06

**Acceptance criteria**

- Given a project record
  When I view its priority inputs
  Then all five inputs are present, each on a 1 to 5 scale.

- Given an input is missing for a project
  When the priority score is calculated
  Then the project is flagged as incompletely scored rather than silently defaulting to zero.

---

### US-14: Understand how the score was produced

**As a** Revenue Operations Lead
**I want** the priority score formula displayed on screen
**So that** I can explain a project's rank to the person who owns it.

**Requirements:** FR-31 · **Priority:** M · **Addresses:** SR-03

**Acceptance criteria**

- Given default weights of alignment 30, value 30, urgency 20, risk 10, effort 10
  When a priority score is calculated
  Then risk and effort are inverted as (6 minus score) before weighting.

- Given a calculated score
  When it is displayed
  Then it falls between 0 and 100 inclusive.

- Given the Prioritization page is open
  When I look for the formula
  Then it is visible on the page without opening documentation.

---

### US-15: Test a different weighting in the meeting

**As a** PMO Lead
**I want** to adjust the weights with sliders and see the ranking update live
**So that** a disagreement about priorities becomes a disagreement about weights,
which we can settle in the room.

**Requirements:** FR-32 · **Priority:** M · **Addresses:** PP-09, SR-03

**Acceptance criteria**

- Given I move a weight slider
  When the page updates
  Then the ranked list re-orders without requiring a page reload.

- Given I set weights that do not total 100 percent
  When scores are calculated
  Then weights are normalized, and the page states that normalization was applied.

- Given I reset the weights
  When the page updates
  Then the default weighting is restored.

---

### US-16: See where a funding line would fall

**As a** PMO Lead
**I want** cumulative PM hours and cumulative budget alongside the ranked list
**So that** I can draw a line at the point where capacity or money runs out.

**Requirements:** FR-33, FR-34 · **Priority:** S

**Acceptance criteria**

- Given projects are ranked by priority score
  When the ranked list renders
  Then each row shows cumulative hours and cumulative budget from the top of the list down.

- Given the prioritization matrix is displayed
  When it renders
  Then value is on the x axis, effort on the y axis, bubble size reflects approved
  budget, and color reflects health.

---

## 7. Epic E5: Capacity and burnout prevention

### US-17: Track what each project manager is actually carrying

**As a** PMO Lead
**I want** allocated hours compared against available hours per PM per week
**So that** I stop discovering overload by asking people how they are doing.

**Requirements:** FR-40, FR-41 · **Priority:** M · **Addresses:** PP-07

**Acceptance criteria**

- Given a PM has a weekly availability, defaulting to 40 hours
  When availability is reduced by planned time off
  Then utilization is calculated against the reduced figure.

- Given a PM is assigned to multiple active projects
  When utilization is calculated
  Then it equals total allocated hours divided by available hours.

- Given a project is not active
  When utilization is calculated
  Then its allocation is excluded.

---

### US-18: See utilization at a glance

**As a** PMO Lead
**I want** a bar per PM showing allocated vs. available hours with traffic-light color
**So that** I can see the whole team's load in one view.

**Requirements:** FR-42 · **Priority:** M

**Acceptance criteria**

- Given a PM's utilization is between 60 and 85 percent
  When the bar renders
  Then it is green.

- Given utilization is between 85 and 100 percent, or below 60 percent
  When the bar renders
  Then it is yellow.

- Given utilization is above 100 percent
  When the bar renders
  Then it is red.

---

### US-19: Catch sustained overload, not just one bad week

**As a** PMO Lead
**I want** a burnout flag for PMs over 100 percent now or over 90 percent for four
or more consecutive weeks
**So that** a chronic problem is not hidden by a single quiet week.

**Requirements:** FR-43 · **Priority:** M · **Addresses:** SR-04

**Acceptance criteria**

- Given a PM is above 100 percent for the current week
  When the capacity page renders
  Then a burnout flag is shown for that PM.

- Given a PM has been between 90 and 100 percent for four consecutive weeks
  When the capacity page renders
  Then a burnout flag is shown, with the streak length stated.

- Given a PM has been above 90 percent for three consecutive weeks
  When the capacity page renders
  Then no burnout flag is shown.

---

### US-20: See what is consuming a person's time

**As a** PMO Lead
**I want** a per-PM breakdown of which projects consume their hours, sorted by hours
**So that** I know what to move when someone is overloaded.

**Requirements:** FR-44, FR-45 · **Priority:** S / C

**Acceptance criteria**

- Given I select a PM
  When the breakdown renders
  Then their active projects are listed with allocated hours, largest first.

- Given a PM is flagged for burnout
  When I view rebalancing suggestions
  Then PMs in the same department below 60 percent utilization are listed as candidates. *(FR-45, could-have)*

---

## 8. Epic E6: Project drill-down

### US-21: Answer a question about one project in the meeting

**As a** Program Manager
**I want** a project detail view with header, KPIs, status history, milestones,
risks, and budget lines
**So that** a question raised in the steering committee is answered on the spot.

**Requirements:** FR-50 · **Priority:** M · **Addresses:** PP-09

**Acceptance criteria**

- Given I select a project
  When the detail view renders
  Then PM, sponsor, phase, health, and baseline and forecast dates are shown in the header.

- Given a project has open risks
  When the detail view renders
  Then risks appear with probability, impact, exposure, owner, and mitigation.

- Given a project has no risks recorded
  When the detail view renders
  Then the risk section states that none are recorded, rather than showing an empty table.

---

### US-22: See how a project's health moved over time

**As a** Program Manager
**I want** health plotted over time with the status narrative
**So that** I can tell a slow decline from a sudden problem.

**Requirements:** FR-51 · **Priority:** S

**Acceptance criteria**

- Given a project has multiple status updates
  When the status history renders
  Then health is shown over time in date order with the narrative for each update.

- Given a project has exactly one status update
  When the status history renders
  Then that single point is shown without an error.

---

### US-23: See milestone slip explicitly

**As a** Program Manager
**I want** a milestone table with baseline date, forecast date, and slip in days
**So that** I do not have to subtract dates myself.

**Requirements:** FR-52, FR-53 · **Priority:** M

**Acceptance criteria**

- Given a milestone has a baseline and a forecast date
  When the table renders
  Then slip is shown as forecast minus baseline in days.

- Given a milestone is forecast earlier than baseline
  When the table renders
  Then slip is shown as a negative number rather than zero.

---

## 9. Epic E7: Export and reuse

### US-24: Take any table out of the dashboard

**As a** PMO Analyst
**I want** a Download CSV button on every table, reflecting current filters
**So that** I can build the narrative summary without rebuilding the data.

**Requirements:** FR-60 · **Priority:** S · **Addresses:** PP-08

**Acceptance criteria**

- Given a table is displayed with filters applied
  When I click Download CSV
  Then the downloaded file contains exactly the filtered rows, not the unfiltered set.

- Given the downloaded file
  When I open it
  Then the column headers match the on-screen table.

---

## 10. Stories deliberately not in v1

| Story | Reason | Revisit |
|---|---|---|
| Edit project records inside the app | v1 is read-only; corrections happen at source. Decision D3. | v2 |
| Log in with a role-based account | No authentication in v1, no real data. Decision D3. | Before real data is loaded |
| Import from Jira, Asana, Workfront, or ServiceNow | Integration effort exceeds the value of proving the model | v2 |
| AI-generated weekly status summary per project | Depends on the portfolio being trusted first | v2 |
| What-if mode: drop or delay a project and recalculate | High value, high effort. Wanted by ST-05. | v2 |
| Resource management below PM level | Different problem, different data model | Not planned |
| Gantt scheduling | Adequately served by existing tools | Not planned |
