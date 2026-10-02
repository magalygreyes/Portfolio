# Breezio Service Hub: Stakeholder Analysis and RACI

**Version:** 1.0
**Date:** 2026-09-22
**Author:** Magaly Gonzalez
**Phase:** Slice 1, Phase 1 (Discovery)
**Related documents:** `discovery.md`, `process-maps.md`

---

## 1. Purpose

This document identifies who is affected by the Service Hub, how much influence
each party holds over its adoption, and how each one is engaged during the build.
It feeds the prioritization of requirements in Phase 2.

Stakeholders are fictional roles at Breezio, a fictional company. No real
organization or person is represented.

---

## 2. Stakeholder register

| ID | Stakeholder | Role at Breezio | What they need | Interest | Influence |
|---|---|---|---|---|---|
| ST-01 | Chief Operating Officer | Sponsor. Owns internal service delivery across IT, HR, Facilities, and Finance | Evidence that requests are handled faster and more consistently, and a live view instead of a month-end count | High | High |
| ST-02 | IT Service Desk Lead | Runs the team that receives 45% of all requests | Requests that arrive in the right queue with the asset, system, and urgency already captured | High | High |
| ST-03 | HR Operations Manager | Owns HR requests, including the most sensitive ones | Confidence that personal information is handled with care, and fewer "where is my letter" emails | High | Medium |
| ST-04 | Facilities Manager | Owns maintenance, moves, and building access | Location and urgency on every request, and fewer walk-ups interrupting planned work | Medium | Medium |
| ST-05 | Finance Manager | Owns expense and purchase requests, and the spend approval policy | Approvals that are tracked and auditable, with the right threshold applied every time | Medium | High |
| ST-06 | Request Coordinators | Four people who monitor the shared inboxes and triage requests today | Less forwarding and chasing, and clarity that AI assists their work rather than replacing their judgment | High | Low |
| ST-07 | Department Managers (approvers) | About 25 managers who approve access, purchases, leave, and moves | Approvals that take one click, not an inbox search | Medium | Medium |
| ST-08 | Employees (requesters) | 300 people who submit requests | One place to ask, a request ID, and status without having to chase | Medium | Low |
| ST-09 | IT Security and Privacy | Reviews any tool that stores or processes employee data | Confirmation of what data leaves the company, where it is stored, and who can see it | Low | High |

---

## 3. Influence and interest grid

```
High  │  ST-05 Finance Manager         │  ST-01 COO (sponsor)
I     │  ST-09 IT Security & Privacy   │  ST-02 IT Service Desk Lead
N     │                                │
F     ├────────────────────────────────┼────────────────────────────────
L     │  ST-07 Department Managers     │  ST-03 HR Operations Manager
U     │  ST-08 Employees               │  ST-04 Facilities Manager
E     │                                │  ST-06 Request Coordinators
N     │                                │
C     │
E Low └──────────── Low ─────────── INTEREST ─────────── High ──────────
```

**Manage closely** (high influence, high interest): ST-01, ST-02.
The COO is the sponsor and makes every scope decision. The IT Service Desk Lead
owns the largest share of volume, so the design has to work for IT first.

**Keep satisfied** (high influence, lower interest): ST-05, ST-09.
Finance controls the approval policy. Security can stop the AI component outright.
Both are briefed at defined gates, not pulled into day-to-day design.

**Keep informed** (lower influence, high interest): ST-03, ST-04, ST-06.
These are the daily users. They shape the taxonomy and the intake fields.

**Monitor** (lower influence, lower interest): ST-07, ST-08.
Individually low influence, but the whole solution fails if employees keep
emailing and managers ignore approval notifications. Adoption is the real risk.

---

## 4. Engagement strategy

| Stakeholder | Engagement approach | Frequency | Channel |
|---|---|---|---|
| ST-01 COO | Sponsor check-in: scope decisions, open questions from `discovery.md` §11, demo at the end of each phase | Weekly | 30-minute working session |
| ST-02 IT Service Desk Lead | Design partner for the IT taxonomy, intake fields, and routing rules | Twice weekly during Phases 1 and 2 | Working session |
| ST-03 HR Operations Manager | Reviews sensitive-category handling and HR intake fields. Consulted on Q1 | At Phase 2 and at UAT | Review meeting |
| ST-04 Facilities Manager | Validates Facilities categories and location fields | At Phase 2 | One working session |
| ST-05 Finance Manager | Confirms approval thresholds and audit needs. Closes Q4 | At Phase 2 | Written sign-off on approval rules |
| ST-06 Request Coordinators | Walk through the current-state map for accuracy. Review how the human triage queue will work | At Phase 1 and at UAT | Working session plus written feedback |
| ST-07 Department Managers | Informed of the approval step and what it asks of them | At launch | Announcement plus a one-page guide |
| ST-08 Employees | Informed of the new front door, with a short guide and the request ID explained | At launch | All-staff announcement |
| ST-09 IT Security and Privacy | Informed that Slice 1 uses synthetic data only. Formal review required before real data or an external AI API is used. Closes Q6 | Before any real data | Written note, then review gate |

---

## 5. RACI by phase

R = Responsible (does the work), A = Accountable (owns the outcome, one per row),
C = Consulted (two-way input), I = Informed (one-way update).

| Phase / deliverable | BA (Magaly) | ST-01 COO | ST-02 IT Lead | ST-03 HR Ops | ST-05 Finance | ST-06 Coordinators | ST-09 Security |
|---|---|---|---|---|---|---|---|
| Discovery and problem statement | R | A | C | C | I | C | - |
| Current-state process map | R | A | C | C | I | C | - |
| KPI definitions | R | A | C | C | C | C | - |
| Request taxonomy | R | A | C | C | C | C | - |
| Requirements and user stories | R | A | C | C | C | C | I |
| Approval and business rules | R | A | C | C | C | I | I |
| Data model and synthetic data | R | A | I | I | I | I | C |
| AI classification design | R | A | C | C | I | C | C |
| Dashboard build and deployment | R | A | I | I | I | I | I |
| UAT execution | C | A | R | R | C | R | I |
| Labeled accuracy evaluation (Slice 2) | R | A | C | C | I | R | I |
| Go-live and launch communication | R | A | C | C | C | C | C |

Notes on the RACI:

- The BA is Responsible for the artifacts and the build, but never Accountable.
  Accountability sits with the sponsor, which is what makes scope decisions stick.
- UAT flips the pattern on purpose. Team leads and coordinators run the tests
  because they have to trust the routing afterward. A pass is not self-certified.
- Coordinators are Responsible for hand-labeling the accuracy set in Slice 2.
  The people who triage today are the right judges of what a correct label is.
- Security moves from Informed to Consulted on the data model and AI design,
  because those two deliverables decide what data exists and where it is sent.

---

## 6. Stakeholder-driven risks

| ID | Risk | Source | Likelihood | Impact | Mitigation |
|---|---|---|---|---|---|
| SR-01 | Employees keep emailing people directly, so requests bypass the hub and volume looks lower than it is | ST-08 | High | High | Form must be faster than email. Shared inboxes auto-reply with the form link during transition (Q3). K1 and K8 reported by channel |
| SR-02 | Coordinators see AI routing as a threat to their roles and work around it | ST-06 | Medium | High | Coordinators own the human triage queue and label the accuracy set. Framed as removing forwarding and chasing, not judgment |
| SR-03 | Security blocks the AI component because HR requests may contain personal information | ST-09, ST-03 | Medium | High | Synthetic data only in Slice 1. Sensitive-category handling decided early (Q1). Data processing terms settled before real data (Q6) |
| SR-04 | Early misclassifications destroy trust before accuracy is measured | ST-02, ST-06 | Medium | High | Three-band thresholds (D3). Every AI decision shows its confidence. Auto-route band only enabled after K9 is met |
| SR-05 | Managers ignore approval notifications, so approvals stall in a new place | ST-07 | Medium | Medium | K6 made visible per approver. Reminder and escalation designed in Slice 3 |
| SR-06 | Team leads disagree on who owns ambiguous categories, such as onboarding (HR and IT) | ST-02, ST-03 | High | Medium | Taxonomy ownership settled by the sponsor (Q2). Each category has exactly one owning team, with a documented handoff where two teams contribute |
| SR-07 | Finance approval thresholds are applied inconsistently by the rules engine and by people | ST-05 | Low | High | Threshold defined once in the rules layer and signed off in writing (Q4) |

---

## 7. Decision log

Decisions made at kickoff are recorded in `discovery.md` §10 (D1 to D5).
Decisions made with stakeholders from Phase 2 onward are added here, starting at D6.

_No stakeholder decisions recorded yet. First entries expected when Q1 to Q7 close in Phase 2._
