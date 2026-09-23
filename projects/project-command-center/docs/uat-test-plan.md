# Project Command Center: UAT Test Plan

**Version:** 1.0
**Date:** 2026-09-22
**Author:** Magaly Gonzalez
**Related documents:** `requirements.md`, `user-stories.md`, `traceability-matrix.md`, `stakeholders.md`

---

## 1. Purpose and scope

User acceptance testing confirms that the Project Command Center does what the
business asked for, in business terms, before it is relied on for portfolio
decisions.

**In scope:** every must-have and should-have requirement in `requirements.md`,
exercised through the user interface by business users.

**Out of scope:** unit tests of the metrics and validation modules (covered by the
automated test suite), load and performance testing beyond NFR-02, security
testing (v1 holds no real or personal data), and browser compatibility beyond
current Chrome and Edge.

---

## 2. Roles

| Role | Who | Responsibility |
|---|---|---|
| UAT Lead | ST-01 PMO Analyst | Executes the test suite, records results, decides pass or fail per case |
| Business Tester | ST-02 Program Manager | Executes the project detail and risk scenarios |
| Financial Reviewer | ST-06 Finance Business Partner | Confirms budget variance and EAC match how finance calculates them |
| Prioritization Reviewer | ST-04 RevOps Lead | Confirms the scoring model behaves as agreed |
| BA / Developer | Magaly | Supports testing, triages and fixes defects. Does not sign off on their own work |
| Accountable | ST-05 PMO Lead | Approves go-live based on exit criteria |

Testing is deliberately executed by the people who will depend on the numbers, not
by the person who built the tool. See the RACI in `stakeholders.md`.

---

## 3. Entry criteria

UAT does not begin until all of the following are true.

1. All must-have requirements are built and deployed to the test environment.
2. The automated unit test suite passes.
3. The seed dataset is loaded and contains at least 40 projects across at least
   three departments, with at least twelve months of budget data.
4. A deliberately corrupted copy of the dataset exists for the data quality scenarios.
5. `requirements.md`, `user-stories.md`, and this plan have been circulated to all testers.
6. Testers have access to the deployed application.

---

## 4. Exit criteria

UAT is complete and go-live is recommended when all of the following are true.

1. 100 percent of must-have test cases have been executed.
2. 100 percent of must-have test cases have passed.
3. No open Severity 1 or Severity 2 defects.
4. Any open Severity 3 or Severity 4 defects are documented with an agreed
   disposition (fix before launch, fix after launch, or accept).
5. The Financial Reviewer has confirmed in writing that K3 and K4 match finance's
   own calculations.
6. The PMO Lead has signed off.

---

## 5. Defect severity definitions

| Severity | Definition | Example | Response |
|---|---|---|---|
| S1 Critical | A KPI is wrong, or invalid data reaches a metric. Any decision made from the screen could be incorrect. | A rejected row is counted in the portfolio health mix | Stop testing. Fix immediately. Retest the affected area in full. |
| S2 Major | A must-have requirement does not work, but the error is visible rather than silent. | Filters do not carry across pages | Fix before go-live. |
| S3 Minor | A should-have requirement is incomplete, or a display issue that does not affect a number. | Empty state shows a blank table instead of a message | Fix before go-live if time allows, otherwise log for the next release. |
| S4 Cosmetic | Wording, spacing, or label issues. | A column header reads "Var %" instead of "Budget variance %" | Log and batch for a later release. |

**The S1 definition is the important one.** A wrong number that looks right is more
dangerous than a page that fails to load, and is treated accordingly.

---

## 6. Test scenarios

Test case IDs map to user stories in `user-stories.md` and to requirements in
`requirements.md`. The full mapping is in `traceability-matrix.md`.

### 6.1 Data quality and validation

| ID | Story | Scenario | Steps | Expected result | Priority |
|---|---|---|---|---|---|
| TC-01 | US-01 | Clean dataset loads | 1. Place all seven source files in `data/`. 2. Start the app. | App loads, no error, project count displayed and matches the source file row count. | M |
| TC-02 | US-01 | Missing source file | 1. Remove `risks.csv`. 2. Start the app. | Error names the missing file. No KPIs are displayed. | M |
| TC-03 | US-02 | Duplicate project ID | 1. Duplicate one `project_id` in the corrupted dataset. 2. Load. | Both duplicate rows rejected, reason states duplicate key. Neither appears in any KPI. | M |
| TC-04 | US-02 | Unknown PM reference | 1. Change one `pm_id` to a value not in `project_managers.csv`. 2. Load. | Row rejected. Reason names the unknown value. | M |
| TC-05 | US-02 | Invalid health value | 1. Set one project's health to "Amber". 2. Load. | Row rejected. Reason lists the allowed values. | M |
| TC-06 | US-02 | Negative budget | 1. Set one budget line to a negative figure. 2. Load. | Row rejected. | M |
| TC-07 | US-02 | Finish date before start date | 1. Set one project's finish date earlier than its start date. 2. Load. | Row rejected with a date-specific reason. | M |
| TC-08 | US-02 | Rejected rows excluded from KPIs | 1. Load the corrupted dataset. 2. Note the rejected count. 3. Compare the Overview project count to the loaded row count. | Overview count equals loaded rows minus rejected rows. | M |
| TC-09 | US-03 | Stale project flagged, not dropped | 1. Set one project's last status update to 20 days ago. 2. Load. | Project still appears in the portfolio. It is flagged stale and counted in K8. | M |
| TC-10 | US-03 | Over-allocated PM flagged | 1. Allocate one PM above 100 percent. 2. Load. | Allocation retained and flagged. PM appears in the capacity view. | M |
| TC-11 | US-03 | Actual spend with no plan | 1. Give one project actual spend and no planned budget. 2. Open Budget. | Variance shows as not calculable, not as a percentage. | M |
| TC-12 | US-04 | Data Quality panel content | 1. Load corrupted dataset. 2. Open Data Quality. | Counts of loaded, rejected, and flagged rows are shown. Each rejected row shows source file, identifier, and plain-language reason. | S |
| TC-13 | US-04 | Export rejected rows | 1. On Data Quality, click Download CSV. | CSV contains every rejected row with its reason. | S |
| TC-14 | US-04 | Clean data empty state | 1. Load the clean dataset. 2. Open Data Quality. | Panel states all rows passed. No empty unexplained table. | S |

### 6.2 Portfolio overview

| ID | Story | Scenario | Steps | Expected result | Priority |
|---|---|---|---|---|---|
| TC-15 | US-05 | KPI tiles present | 1. Open Overview. | Tiles K1 through K8 appear above any chart or table. | M |
| TC-16 | US-05 | Threshold coloring | 1. Note each KPI value. 2. Compare colors to the KPI table in `requirements.md`. | Every tile color matches its defined band. Only red, yellow, green appear. | M |
| TC-17 | US-05 | Uncalculable KPI | 1. Load a dataset with no capacity rows. 2. Open Overview. | K7 shows "not available" with a reason. It does not show zero. | M |
| TC-18 | US-06 | Health mix by department | 1. Open the health mix chart, grouped by department. | Each department shows Green, Yellow, Red counts. Chart total equals the active project count. | M |
| TC-19 | US-07 | Project table columns | 1. View the Overview project table. | All eight columns present: name, PM, health, phase, priority score, budget variance, slip days, last update. | M |
| TC-20 | US-07 | Sorting | 1. Click "Slip days". 2. Click again. | First click sorts ascending, second descending. | M |
| TC-21 | US-08 | Filter persistence | 1. On Overview, filter to one department. 2. Navigate to Budget, then Capacity, then Prioritization. | The department filter remains applied on every page. | M |
| TC-22 | US-08 | Active only | 1. Enable "active only". 2. Check K1. | Backlog, On Hold, Complete, and Cancelled projects are excluded from the count. | M |
| TC-23 | US-08 | No matching projects | 1. Apply a filter combination matching no projects. | An empty-state message explains that nothing matched. No blank page, no zero-value KPI tiles. | M |
| TC-24 | US-09 | Health change list | 1. Open "what changed this week". | Only projects whose health differs from the prior update are listed, showing prior and current health. | S |

### 6.3 Budget

| ID | Story | Scenario | Steps | Expected result | Priority |
|---|---|---|---|---|---|
| TC-25 | US-10 | Planned vs. actual chart | 1. Open Budget with no project filter. | Cumulative planned and cumulative actual are plotted for the filtered portfolio. | M |
| TC-26 | US-10 | Single project view | 1. Filter to one project. | Only that project's lines are plotted. | M |
| TC-27 | US-10 | Actuals end early | 1. Use a project whose actuals stop in month 8 of 12. | The actual line ends at month 8. It does not drop to zero for months 9 to 12. | M |
| TC-28 | US-11 | Variance calculation | 1. Pick one project. 2. Calculate (actual minus planned) / planned by hand. 3. Compare to K3 on screen. | The figures match. | M |
| TC-29 | US-11 | Variance coloring | 1. Find a project more than 20 percent over plan. | Its row is red. | M |
| TC-30 | US-11 | Cross-page consistency | 1. Note one project's variance on Overview. 2. Note the same project's variance on Budget. | The two figures are identical. | M |
| TC-31 | US-12 | EAC calculation | 1. Pick a project with actuals. 2. Calculate actual + (remaining planned × cost performance) by hand. 3. Compare to EAC on screen. | The figures match. | S |
| TC-32 | US-12 | Forecast overrun highlighted | 1. Find a project where EAC exceeds approved budget. | The row is highlighted and the overrun amount is shown. | S |
| TC-33 | US-12 | No actuals yet | 1. Pick a project with zero actual spend. | EAC equals the approved budget. Not zero, not an error. | S |

### 6.4 Prioritization

| ID | Story | Scenario | Steps | Expected result | Priority |
|---|---|---|---|---|---|
| TC-34 | US-13 | Five scored inputs | 1. Open a project's priority inputs. | Alignment, value, urgency, risk, and effort are all present on a 1 to 5 scale. | M |
| TC-35 | US-13 | Incomplete scoring | 1. Remove one input from a project. 2. Open Prioritization. | The project is flagged as incompletely scored. It does not silently score zero. | M |
| TC-36 | US-14 | Inversion of risk and effort | 1. Pick a project. 2. Calculate the weighted score by hand with risk and effort as (6 minus score). 3. Compare. | The figures match. | M |
| TC-37 | US-14 | Score range | 1. Review every project's score. | All scores fall between 0 and 100 inclusive. | M |
| TC-38 | US-14 | Formula visible | 1. Open Prioritization. | The formula is displayed on the page. | M |
| TC-39 | US-15 | Live re-ranking | 1. Move the "business value" weight from 30 to 50. | The ranked list re-orders without a page reload. | M |
| TC-40 | US-15 | Weight normalization | 1. Set weights totalling 120 percent. | Weights are normalized and the page states that normalization was applied. | M |
| TC-41 | US-15 | Reset to default | 1. Change several weights. 2. Click reset. | Default weights are restored: 30 / 30 / 20 / 10 / 10. | M |
| TC-42 | US-16 | Cumulative columns | 1. View the ranked list. | Each row shows cumulative PM hours and cumulative budget from the top down. | S |
| TC-43 | US-16 | Prioritization matrix | 1. View the matrix chart. | Value on x, effort on y, bubble size reflects approved budget, color reflects health. | S |

### 6.5 Capacity

| ID | Story | Scenario | Steps | Expected result | Priority |
|---|---|---|---|---|---|
| TC-44 | US-17 | Availability reduced by time off | 1. Give a PM 8 hours of planned time off in one week. | That week's available hours are 32, and utilization is calculated against 32. | M |
| TC-45 | US-17 | Multi-project utilization | 1. Pick a PM on three active projects. 2. Sum allocated hours by hand. 3. Divide by available. 4. Compare. | The figures match. | M |
| TC-46 | US-17 | Inactive projects excluded | 1. Set one of that PM's projects to On Hold. | Utilization drops by that project's allocation. | M |
| TC-47 | US-18 | Green band | 1. Find a PM at 75 percent. | The bar is green. | M |
| TC-48 | US-18 | Yellow band, both sides | 1. Find a PM at 92 percent. 2. Find a PM at 45 percent. | Both bars are yellow. | M |
| TC-49 | US-18 | Red band | 1. Find a PM above 100 percent. | The bar is red. | M |
| TC-50 | US-19 | Current-week overload flag | 1. Set a PM above 100 percent this week. | A burnout flag is shown. | M |
| TC-51 | US-19 | Four-week streak flag | 1. Set a PM to 93 percent for four consecutive weeks. | A burnout flag is shown, and the streak length is stated. | M |
| TC-52 | US-19 | Three-week streak, no flag | 1. Set a PM to 93 percent for exactly three consecutive weeks. | No burnout flag is shown. | M |
| TC-53 | US-20 | Per-PM breakdown | 1. Select a PM. | Their active projects are listed with allocated hours, largest first. | S |

### 6.6 Project detail

| ID | Story | Scenario | Steps | Expected result | Priority |
|---|---|---|---|---|---|
| TC-54 | US-21 | Detail header | 1. Select a project. | PM, sponsor, phase, health, baseline and forecast dates are shown. | M |
| TC-55 | US-21 | Risk table | 1. Select a project with open risks. | Probability, impact, exposure, owner, and mitigation are shown per risk. | M |
| TC-56 | US-21 | No risks empty state | 1. Select a project with no risks. | A message states that none are recorded. No empty table. | M |
| TC-57 | US-22 | Status history timeline | 1. Select a project with several updates. | Health over time is shown in date order with each narrative. | S |
| TC-58 | US-22 | Single update | 1. Select a project with exactly one update. | The single point renders without error. | S |
| TC-59 | US-23 | Milestone slip | 1. View a milestone table. | Slip equals forecast minus baseline in days. | M |
| TC-60 | US-23 | Negative slip | 1. Find a milestone forecast earlier than baseline. | Slip shows as a negative number, not zero. | M |

### 6.7 Export and performance

| ID | Story | Scenario | Steps | Expected result | Priority |
|---|---|---|---|---|---|
| TC-61 | US-24 | Filtered export | 1. Filter to one department. 2. Download the project table CSV. | The CSV contains only the filtered rows. | S |
| TC-62 | US-24 | Header match | 1. Open the downloaded CSV. | Column headers match the on-screen table. | S |
| TC-63 | NFR-02 | Load performance | 1. Load 60 projects with 12 months of budget data. 2. Time the Overview page load. | Page renders in under 3 seconds. | M |
| TC-64 | NFR-06 | No real identities in seed data | 1. Review `projects.csv` and `project_managers.csv`. | No real company, employee, or client names appear. | M |

---

## 7. Traceability summary

| Requirement group | Requirements | Test cases | Coverage |
|---|---|---|---|
| Data loading and validation | FR-01 to FR-05 | TC-01 to TC-14 | Complete |
| Portfolio overview | FR-10 to FR-14 | TC-15 to TC-24 | Complete |
| Budget | FR-20 to FR-23 | TC-25 to TC-33 | Complete |
| Prioritization | FR-30 to FR-34 | TC-34 to TC-43 | Complete |
| Capacity | FR-40 to FR-44 | TC-44 to TC-53 | Complete (FR-45 is could-have, deferred) |
| Project detail | FR-50 to FR-53 | TC-54 to TC-60 | Complete |
| Export | FR-60 | TC-61, TC-62 | Complete |
| Non-functional | NFR-02, NFR-06 | TC-63, TC-64 | Partial by design; NFR-01, 03, 04, 05 verified by code review rather than UAT |

Row-level traceability is in `traceability-matrix.md`.

---

## 8. Defect log template

| ID | Test case | Severity | Description | Steps to reproduce | Status | Disposition |
|---|---|---|---|---|---|---|
| DEF-001 | | | | | Open / In progress / Retest / Closed | Fix before launch / Fix after launch / Accept |

---

## 9. Sign-off

| Role | Name | Confirms | Date | Signature |
|---|---|---|---|---|
| UAT Lead | ST-01 PMO Analyst | All must-have cases executed and passed | | |
| Financial Reviewer | ST-06 Finance BP | K3 and K4 match finance calculations | | |
| Prioritization Reviewer | ST-04 RevOps Lead | Scoring model behaves as agreed | | |
| Accountable | ST-05 PMO Lead | Exit criteria met, go-live approved | | |
