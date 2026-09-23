# Project Command Center: Stakeholder Analysis and RACI

**Version:** 1.0
**Date:** 2026-09-22
**Author:** Magaly Gonzalez
**Related documents:** `requirements.md`, `process-maps.md`, `user-stories.md`

---

## 1. Purpose

This document identifies who is affected by the Project Command Center, how much
influence each party holds over its adoption, and how each one is engaged during
the build. It is the input to the communication plan and to the prioritization of
requirements in `requirements.md`.

Stakeholders are fictional roles in a fictional organization. No real company,
employee, or client is represented.

---

## 2. Stakeholder register

| ID | Stakeholder | Role in the organization | What they need | Interest | Influence |
|---|---|---|---|---|---|
| ST-01 | PMO Analyst | Compiles the weekly portfolio roll-up and the steering committee deck | One screen that replaces four hours of spreadsheet consolidation, and a data quality view that tells them what is wrong before the meeting | High | Medium |
| ST-02 | Program Manager | Owns delivery for a group of related projects | Health, blockers, budget burn, and upcoming milestones for the projects they own, without asking the PMO for a report | High | Medium |
| ST-03 | IT Business Analyst | Bridges requirements and delivery on individual projects | Visibility into which projects are slipping and what changed since last week | Medium | Low |
| ST-04 | Revenue Operations Lead | Ties project spend to revenue outcomes | A defensible ranking of which projects unlock revenue relative to their cost | Medium | Medium |
| ST-05 | PMO Lead | Accountable for portfolio performance and for PM workload | Portfolio KPIs, and an early warning when a project manager is overloaded | High | High |
| ST-06 | Finance Business Partner | Approves budget and tracks variance | Budget vs. actual by project and month, and a forecast of overruns before they land | Medium | High |
| ST-07 | Project Managers (as data providers) | Submit the weekly status update that feeds the dashboard | The update to take minutes, not an hour, and to not be used punitively | Low | Medium |
| ST-08 | Steering Committee | Funds and cancels projects | A single portfolio view they trust, with consistent definitions | Low | High |
| ST-09 | IT Security and Data Governance | Reviews any new internal tool | Confirmation that no personal or confidential data is stored, and that access is controlled | Low | Medium |

---

## 3. Influence and interest grid

```
High  │  ST-06 Finance BP          │  ST-05 PMO Lead
I     │  ST-08 Steering Committee  │
N     │                            │
F     ├────────────────────────────┼────────────────────────────
L     │  ST-09 Security/Governance │  ST-01 PMO Analyst
U     │  ST-07 Project Managers    │  ST-02 Program Manager
E     │                            │  ST-04 RevOps Lead
N     │                            │  ST-03 IT BA
C     │
E Low └────────── Low ─────────── INTEREST ─────────── High ──────
```

**Keep satisfied** (high influence, lower interest): ST-06, ST-08, ST-09.
Brief them at milestones. Do not involve them in day-to-day design decisions.

**Manage closely** (high influence, high interest): ST-05.
The PMO Lead is the sponsor. Every scope decision goes through this person.

**Keep informed** (lower influence, high interest): ST-01, ST-02, ST-03, ST-04.
These are the daily users. They drive the requirements but do not decide scope.

**Monitor** (lower influence, lower interest): ST-07.
Project managers are not primary users, but the dashboard is worthless if their
status updates stop arriving. Their cost of participation is a real project risk.

---

## 4. Engagement strategy

| Stakeholder | Engagement approach | Frequency | Channel |
|---|---|---|---|
| ST-05 PMO Lead | Sponsor check-in: scope decisions, open questions from `requirements.md` §8, demo of each phase | Weekly | 30-minute working session |
| ST-01 PMO Analyst | Primary design partner. Validates KPI definitions and reviews every page before build | Twice weekly during design, weekly after | Working session plus written feedback |
| ST-02 Program Manager | Reviews the Project Detail and Risk views. Provides real-world edge cases | At design and at UAT | Review meeting |
| ST-04 RevOps Lead | Validates the priority scoring inputs and default weights | At design of the prioritization model | One working session, then written sign-off |
| ST-06 Finance BP | Confirms budget variance and EAC definitions match how finance already calculates them | Once at design, once at UAT | Written review of the KPI table |
| ST-03 IT BA | Consulted on the "what changed this week" view | Once | Email or written comment |
| ST-07 Project Managers | Informed of what the dashboard shows about their projects, and that health remains their call | At launch | Announcement plus a one-page guide |
| ST-08 Steering Committee | Informed at launch with a walkthrough of the definitions behind each KPI | At launch | Standing agenda item |
| ST-09 Security / Governance | Informed that v1 uses fictional seed data with no personal data and no authentication, and that a production version would require a security review | Before any real data is loaded | Written note |

---

## 5. RACI by project phase

R = Responsible (does the work), A = Accountable (owns the outcome, one per row),
C = Consulted (two-way input), I = Informed (one-way update).

| Phase / deliverable | BA (Magaly) | ST-05 PMO Lead | ST-01 PMO Analyst | ST-04 RevOps | ST-06 Finance BP | ST-02 Program Mgr | ST-09 Security |
|---|---|---|---|---|---|---|---|
| Discovery and problem statement | R | A | C | C | I | C | - |
| Current-state process map | R | A | C | I | I | C | - |
| KPI definitions | R | A | C | C | C | I | - |
| Requirements document | R | A | C | C | C | C | I |
| Priority scoring model | R | A | C | C | I | I | - |
| Data model and validation rules | R | A | C | I | C | I | I |
| Build and deployment | R | A | I | I | I | I | I |
| UAT execution | C | A | R | C | C | R | I |
| Go-live and launch communication | R | A | C | I | I | I | I |
| Post-launch review | R | A | C | C | C | C | - |

Notes on the RACI:

- The BA is Responsible for the artifacts and the build, but never Accountable.
  Accountability sits with the sponsor, which is what makes scope decisions stick.
- UAT flips the pattern deliberately. The PMO Analyst and Program Manager execute
  the tests because they are the ones who have to trust the numbers afterward.
  The BA supports rather than runs the test, so that a pass is not self-certified.
- Security and Governance is Informed only in v1 because the data is fictional.
  Loading real portfolio data would move them to Consulted with a formal review gate.

---

## 6. Stakeholder-driven risks

| ID | Risk | Source | Likelihood | Impact | Mitigation |
|---|---|---|---|---|---|
| SR-01 | Project managers stop submitting weekly status updates, so the dashboard shows stale data | ST-07 | Medium | High | KPI K8 makes staleness visible rather than hiding it. Status update kept under five minutes. Health stays the PM's call, never overridden by the tool. |
| SR-02 | Finance calculates budget variance differently, so two numbers circulate and neither is trusted | ST-06 | Medium | High | Variance and EAC definitions reviewed and signed off by Finance before build. Formula shown on screen next to the number. |
| SR-03 | Priority weights become political, with each department lobbying for its own projects | ST-04, ST-08 | High | Medium | Weights are adjustable and visible rather than hidden. The conversation moves from "why is my project ranked low" to "which weighting do we agree on." |
| SR-04 | The dashboard gets used to evaluate individual project managers rather than the portfolio | ST-05, ST-07 | Medium | High | Capacity view is framed around burnout prevention. Raised explicitly with the sponsor as a usage norm at launch. |
| SR-05 | Steering committee asks for a KPI that v1 does not calculate, during the launch meeting | ST-08 | Medium | Low | KPI definitions circulated a week before launch, with the out-of-scope list attached. |

---

## 7. Decision log

| # | Decision | Made by | Date | Rationale |
|---|---|---|---|---|
| D1 | Capacity is tracked in hours, not percent allocation | ST-05 with BA | 2026-09-02 | Hours make over-allocation arithmetically obvious and comparable across part-time PMs. Closes open question Q2 in `requirements.md`. |
| D2 | The tool does not override PM-reported health | ST-05 | 2026-09-02 | Preserves trust with ST-07. A computed "suggested health" is shown alongside instead, so disagreement is visible without being punitive. |
| D3 | v1 is read-only, with data in CSV and no authentication | BA with ST-05 | 2026-09-02 | Keeps Security and Governance out of the critical path for a proof of value. Revisited before any real data is loaded. |
| D4 | Priority weights are adjustable by the user at runtime | ST-05 with ST-04 | 2026-09-02 | Turns a contested fixed formula into a transparent, testable model. |
