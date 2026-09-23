# Project Command Center: Requirements Traceability Matrix

**Version:** 1.0
**Date:** 2026-09-22
**Author:** Magaly Gonzalez
**Related documents:** `requirements.md`, `process-maps.md`, `user-stories.md`, `uat-test-plan.md`

---

## 1. Purpose

This matrix connects every requirement backward to the business problem that
justified it, and forward to the user story that describes it and the test case
that proves it works.

It answers three questions that come up in every delivery:

1. Why does this requirement exist, and who asked for it?
2. Has every requirement been built and tested?
3. If we cut this requirement, what business problem goes unsolved?

Traceability runs in both directions. Every requirement traces back to a pain
point. Every pain point traces forward to at least one requirement.

---

## 2. Legend

| Column | Meaning |
|---|---|
| Pain point | Current-state problem from `process-maps.md` §2.3 |
| Stakeholder | Requesting stakeholder from `stakeholders.md` §2 |
| KPI | Measure affected, from `requirements.md` §4 |
| Requirement | FR or NFR ID from `requirements.md` |
| Priority | MoSCoW: M must, S should, C could |
| Story | User story ID from `user-stories.md` |
| Test case | Test case ID from `uat-test-plan.md` |
| Status | Built / Deferred / Not started |

---

## 3. Forward traceability: requirement to test

### 3.1 Data loading and validation

| Pain point | Stakeholder | KPI | Requirement | Priority | Story | Test case | Status |
|---|---|---|---|---|---|---|---|
| PP-01, PP-02 | ST-01 | - | FR-01 Load seven source files | M | US-01 | TC-01, TC-02 | Built |
| PP-03 | ST-01 | - | FR-02 Validation runs before calculation | M | US-02 | TC-03 to TC-08 | Built |
| PP-03 | ST-01 | - | FR-03 Hard rejection rules | M | US-02 | TC-03, TC-04, TC-05, TC-06, TC-07 | Built |
| PP-10 | ST-01, ST-05 | K8 | FR-04 Soft warning rules | M | US-03 | TC-09, TC-10, TC-11 | Built |
| PP-03, PP-08 | ST-01 | - | FR-05 Data Quality panel | S | US-04 | TC-12, TC-13, TC-14 | Built |

### 3.2 Portfolio overview

| Pain point | Stakeholder | KPI | Requirement | Priority | Story | Test case | Status |
|---|---|---|---|---|---|---|---|
| PP-08 | ST-05 | K1 to K8 | FR-10 KPI tiles | M | US-05 | TC-15, TC-16, TC-17 | Built |
| PP-04 | ST-05 | K1 | FR-11 Health mix by portfolio and department | M | US-06 | TC-18 | Built |
| PP-08 | ST-01, ST-05 | K1, K3, K5 | FR-12 Sortable project table | M | US-07 | TC-19, TC-20 | Built |
| PP-09 | ST-02 | - | FR-13 Global sidebar filters | M | US-08 | TC-21, TC-22, TC-23 | Built |
| PP-10 | ST-03 | K1 | FR-14 What changed this week | S | US-09 | TC-24 | Built |

### 3.3 Budget vs. actual

| Pain point | Stakeholder | KPI | Requirement | Priority | Story | Test case | Status |
|---|---|---|---|---|---|---|---|
| PP-05 | ST-06 | K3, K4 | FR-20 Planned vs. actual by month | M | US-10 | TC-25, TC-26, TC-27 | Built |
| PP-05 | ST-06 | K3, K4 | FR-21 Variance table with traffic light | M | US-11 | TC-28, TC-29, TC-30 | Built |
| PP-05 | ST-06 | K4 | FR-22 Estimate at completion | S | US-12 | TC-31, TC-33 | Built |
| PP-05 | ST-06, ST-08 | K3 | FR-23 Highlight forecast overruns | S | US-12 | TC-32 | Built |

### 3.4 Priority scoring

| Pain point | Stakeholder | KPI | Requirement | Priority | Story | Test case | Status |
|---|---|---|---|---|---|---|---|
| PP-06 | ST-04 | K9 | FR-30 Five scored inputs | M | US-13 | TC-34, TC-35 | Built |
| PP-06 | ST-04, ST-08 | K9 | FR-31 Weighted score with inversion | M | US-14 | TC-36, TC-37, TC-38 | Built |
| PP-06, PP-09 | ST-05, ST-04 | K9 | FR-32 Adjustable weights, live update | M | US-15 | TC-39, TC-40, TC-41 | Built |
| PP-06 | ST-04 | K9 | FR-33 Prioritization matrix chart | S | US-16 | TC-43 | Built |
| PP-06, PP-07 | ST-05 | K9 | FR-34 Cumulative hours and budget | S | US-16 | TC-42 | Built |

### 3.5 Capacity and burnout

| Pain point | Stakeholder | KPI | Requirement | Priority | Story | Test case | Status |
|---|---|---|---|---|---|---|---|
| PP-07 | ST-05 | K7 | FR-40 PM available hours | M | US-17 | TC-44 | Built |
| PP-07 | ST-05 | K7 | FR-41 Allocation and utilization | M | US-17 | TC-45, TC-46 | Built |
| PP-07 | ST-05 | K7 | FR-42 Capacity bars with traffic light | M | US-18 | TC-47, TC-48, TC-49 | Built |
| PP-07 | ST-05, ST-07 | K7 | FR-43 Burnout flag rules | M | US-19 | TC-50, TC-51, TC-52 | Built |
| PP-07 | ST-05 | K7 | FR-44 Per-PM project breakdown | S | US-20 | TC-53 | Built |
| PP-07 | ST-05 | K7 | FR-45 Rebalancing suggestions | C | US-20 | Not tested | Deferred to v2 |

### 3.6 Project detail

| Pain point | Stakeholder | KPI | Requirement | Priority | Story | Test case | Status |
|---|---|---|---|---|---|---|---|
| PP-09 | ST-02 | - | FR-50 Project detail view | M | US-21 | TC-54, TC-55, TC-56 | Built |
| PP-04, PP-10 | ST-02, ST-03 | K1 | FR-51 Status history timeline | S | US-22 | TC-57, TC-58 | Built |
| PP-09 | ST-02 | K5 | FR-52 Milestone table with slip | M | US-23 | TC-59, TC-60 | Built |
| PP-09 | ST-02 | K6 | FR-53 Open risks table | M | US-21 | TC-55, TC-56 | Built |

### 3.7 Export

| Pain point | Stakeholder | KPI | Requirement | Priority | Story | Test case | Status |
|---|---|---|---|---|---|---|---|
| PP-08 | ST-01 | - | FR-60 Download CSV per table | S | US-24 | TC-61, TC-62 | Built |

### 3.8 Non-functional

| Driver | Stakeholder | Requirement | Priority | Verified by | Status |
|---|---|---|---|---|---|
| Maintainability | BA | NFR-01 Python 3.12, Streamlit, pandas, Plotly, no database in v1 | M | Code review | Built |
| Usability in a live meeting | ST-05, ST-08 | NFR-02 Page load under 3 seconds at 60 projects | M | TC-63 | Built |
| PP-05, consistency of numbers | ST-06 | NFR-03 All metric definitions in one module | M | Code review, TC-30 | Built |
| PP-04, consistency of thresholds | ST-01 | NFR-04 Thresholds in one config file | M | Code review, TC-16 | Built |
| Accessibility of the demo | ST-05 | NFR-05 Deployable to Streamlit Community Cloud | M | Deployment check | Built |
| Data governance | ST-09 | NFR-06 Fictional seed data only | M | TC-64 | Built |

---

## 4. Backward traceability: pain point to requirement

Every current-state pain point in `process-maps.md` is accounted for. No pain point
is left without a requirement, and no requirement exists without a pain point.

| Pain point | Description | Covered by | Fully resolved? |
|---|---|---|---|
| PP-01 | Inconsistent status update formats | FR-01 | Partly. The dashboard requires a schema, but enforcing submission format is a process change outside the tool. |
| PP-02 | Data re-keyed by hand | FR-01 | Yes |
| PP-03 | Project names do not match across sources | FR-02, FR-03, FR-05 | Yes. Unknown keys are rejected with a reason instead of investigated. |
| PP-04 | Health self-reported with no consistency check | FR-11, K1, suggested health comparison | Partly. Disagreement is surfaced but not resolved, by decision D2. |
| PP-05 | Formulas drift between spreadsheet versions | NFR-03, FR-21 | Yes |
| PP-06 | Prioritization is quarterly and stored separately | FR-30 to FR-34 | Yes |
| PP-07 | No capacity data exists | FR-40 to FR-44 | Yes |
| PP-08 | Steering deck assembled by hand | FR-10 to FR-13, FR-60 | Partly. Assembly time drops but does not reach zero, per the modeled figures. |
| PP-09 | Unanticipated questions deferred a cycle | FR-13, FR-50 | Yes |
| PP-10 | Staleness invisible | FR-04, K8, FR-14 | Yes |

---

## 5. Coverage summary

| Measure | Count |
|---|---|
| Functional requirements | 30 |
| Must-have requirements | 20 |
| Should-have requirements | 9 |
| Could-have requirements | 1 (FR-45, deferred) |
| Non-functional requirements | 6 |
| User stories | 24 |
| UAT test cases | 64 |
| Must-have requirements with at least one test case | 20 of 20 (100 percent) |
| Should-have requirements with at least one test case | 9 of 9 (100 percent) |
| Requirements with no linked story | 0 |
| Stories with no linked requirement | 0 |
| Pain points with no linked requirement | 0 |

---

## 6. Open items carried from requirements

| # | Question | Source | Status |
|---|---|---|---|
| Q1 | Should priority weights persist between sessions? | `requirements.md` §8 | Open. Deferred to v2. Current behavior resets on load, tested by TC-41. |
| Q2 | Hours or percent for capacity? | `requirements.md` §8 | Closed. Decision D1: hours. |
| Q3 | Is "suggested health" useful or confusing? | `requirements.md` §8 | Open. To be answered by post-launch review with ST-01 and ST-02. |

---

## 7. How this matrix is maintained

- A new requirement is not accepted into scope until it has a pain point, a
  stakeholder, and an owner in this matrix.
- A requirement cannot move to Built until it has at least one test case.
- A requirement that is cut is marked Deferred with a reason, not deleted, so the
  history of the decision survives.
- The matrix is reviewed at the end of each phase with the sponsor (ST-05).
