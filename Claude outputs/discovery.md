# Breezio Service Hub: Discovery and Problem Definition

**Version:** 1.0
**Date:** 2026-09-22
**Author:** Magaly Gonzalez
**Phase:** Slice 1, Phase 1 (Discovery)
**Related documents:** `stakeholders.md`, `process-maps.md`

---

## 1. Purpose

This document defines the business problem the Service Hub is meant to solve,
the objectives it has to meet, and the KPIs that will show whether it met them.

It is the anchor for every later artifact. Requirements (FR/NFR), user stories,
test cases, and dashboard metrics all trace back to a business objective (BO) and
a KPI (K) defined here.

Breezio is a fictional company. No real organization, employee, or request is
represented. All baseline figures are modeled assumptions, labeled as such.

---

## 2. Organization profile

| Attribute | Value |
|---|---|
| Company | Breezio (fictional) |
| Size | 300 employees, single country, hybrid workforce |
| Service teams in scope | IT, HR, Facilities, Finance |
| Request volume | Roughly 600 service requests per month |
| Current intake | Four shared email inboxes, direct email to individuals, chat messages, walk-ups |
| Current tracking | Per-team spreadsheets, kept inconsistently, or no record at all |
| Service levels | None defined |

### Modeled request mix

| Team | Share | Requests per month |
|---|---|---|
| IT | 45% | 270 |
| HR | 25% | 150 |
| Facilities | 15% | 90 |
| Finance | 15% | 90 |
| **Total** | **100%** | **600** |

---

## 3. Problem statement

| | |
|---|---|
| **The problem of** | employee service requests arriving by email, chat, and walk-up, with no single intake point, no request ID, no routing logic, and no service levels |
| **affects** | 300 employees who need something done, the coordinators who triage four shared inboxes, the specialists who do the work, and the managers who approve it |
| **the impact of which is** | requests sent to the wrong team, work that cannot start because information is missing, approvals lost in inboxes, employees chasing status by email, and leaders who cannot see volume or delays until someone counts by hand at month end. Modeled triage overhead is about **2,772 hours a year, roughly $124,740** (see `process-maps.md` §2.4) |
| **a successful solution would** | give every request one front door and one ID, classify and route it on arrival, catch missing information at intake, move approvals into a tracked step, show status without anyone asking, and put volume, speed, and service-level performance on a live dashboard. AI handles classification only where its accuracy has been measured, and a person decides whenever the model is not confident |

---

## 4. Business objectives

| ID | Objective | Measured by |
|---|---|---|
| BO-01 | One front door: every request enters through one intake point and receives one request ID | K1, K8 |
| BO-02 | Route right the first time: a request reaches the owning team without being forwarded | K1, K4 |
| BO-03 | Complete at intake: the information a team needs is captured before the request is submitted | K5 |
| BO-04 | Status without asking: requesters can see where their request is without emailing anyone | K7, K8 |
| BO-05 | Measurable service: every category has a service-level target, and performance against it is tracked | K2, K3, K6 |
| BO-06 | Accountable AI: AI classifies only within measured accuracy, and a person stays in the loop below the confidence threshold | K9, K10 |
| BO-07 | Live operational view: leaders see volume, backlog, and performance without a manual month-end count | K11 |

---

## 5. Key performance indicators

Every KPI is defined once here and calculated the same way everywhere in the
solution. Status colors are limited to red, yellow, and green.

Business hours are Monday to Friday, 8:00 to 17:00, local time.

| # | KPI | Definition | Modeled baseline | Target | Traffic light |
|---|---|---|---|---|---|
| K1 | Time to assignment | Median business hours from submission until the request sits in the owning team's queue | 9.0 hrs | 1.0 hr or less | Green 1 or less; Yellow over 1 to 4; Red over 4 |
| K2 | Resolution time | Median business days from submission to resolved, by category | 3.5 days (all categories) | Within each category's SLA | Green within SLA; Yellow up to 1.25x SLA; Red over 1.25x SLA |
| K3 | SLA attainment | Resolved requests that met their category SLA, divided by resolved requests | Not measurable today, no SLAs exist | 90% or more | Green 90%+; Yellow 80 to 89%; Red under 80% |
| K4 | Misroute rate | Requests reassigned to a different team at least once, divided by all requests | 18% | 5% or less | Green 5% or less; Yellow over 5 to 10%; Red over 10% |
| K5 | Missing-information rate | Requests that needed a follow-up for information before work could start, divided by all requests | 30% | 10% or less | Green 10% or less; Yellow over 10 to 20%; Red over 20% |
| K6 | Approval cycle time | Median business days from approval requested to approval decided | 2.5 days | 1.0 day or less | Green 1 or less; Yellow over 1 to 2; Red over 2 |
| K7 | Status inquiry rate | "Any update?" contacts from the requester, divided by requests | 0.6 per request | 0.15 or less | Green 0.15 or less; Yellow over 0.15 to 0.30; Red over 0.30 |
| K8 | Stale open requests | Open requests with no status change in 3 or more business days | Not measurable today, no request IDs exist | 5 or fewer | Green 0 to 5; Yellow 6 to 15; Red over 15 |
| K9 | Classification quality | Macro F1 of AI category prediction on a hand-labeled holdout set of about 150 requests, plus precision within the auto-route band | Not applicable, measured in Slice 2 | Macro F1 0.85 or more, and auto-route precision 0.95 or more | Green meets both; Yellow F1 0.75 to 0.84; Red F1 under 0.75 |
| K10 | Confidence band mix | Share of requests in each band: auto-route (90%+), route and flag (70 to 89%), human triage (under 70%) | Not applicable | No target set until measured | Informational |
| K11 | Triage effort | Coordinator hours per month spent on triage, forwarding, chasing, logging, and reporting | 231 hrs per month (modeled) | Set after the future-state model in Phase 2 | Informational until target set |

### How baselines are established

- Baselines are modeled assumptions for a fictional company. They size the
  opportunity. They are not measured results.
- In a real engagement they would come from a four-week sample of shared-inbox
  threads, with timestamps recorded for arrival, first forward, first reply,
  approval, and closure.
- The synthetic data generator (Phase 3) will be built to reproduce these
  baseline distributions, so current-state KPIs can be computed from data rather
  than stated. That shows the calculation works. It does not validate the
  assumptions.
- K3 and K8 have no baseline because the current process has no SLAs and no
  request IDs. That gap is itself a finding.

---

## 6. Scope

### In scope for Slice 1

- Full business analysis package: discovery, stakeholders, process maps,
  requirements, user stories, UAT plan, traceability matrix.
- Synthetic request data generator for Breezio.
- Postgres schema in Supabase, with SQL queries behind every KPI.
- AI classification of category, team, priority, and missing information, with a
  confidence score and the three-band routing rule.
- Business rules layer: approval required, sensitive category handling, SLA
  assignment.
- Streamlit operations dashboard, deployed to a live URL.

### Planned for later slices

- **Slice 2:** webhook API for form submissions, n8n orchestration, approval
  routing and notifications, and a labeled accuracy evaluation (about 150
  hand-labeled requests, published precision, recall, and confusion matrix).
- **Slice 3:** knowledge-base deflection using retrieval (RAG), a weekly AI
  summary for managers, and SLA escalation.

### Out of scope

- Power Automate integration (decision D4).
- Replacing a full IT service management platform. This is a lightweight intake
  and routing layer, not a ServiceNow or Jira Service Management replacement.
- Real employee data of any kind.
- Authentication and role-based access in Slice 1.
- Asset management, change management, and incident problem management.

---

## 7. Draft request taxonomy (v0.1)

This draft gives the classifier a closed set of labels. It is finalized with the
team leads in Phase 2. "Sensitive" marks categories likely to contain personal
information, which drives open question Q1.

| Team | Category | Approval likely | Sensitive |
|---|---|---|---|
| IT | Access request | Yes, manager | No |
| IT | Hardware request | Yes, manager | No |
| IT | Software request | Yes, manager | No |
| IT | Password or account lockout | No | No |
| IT | Something is broken (incident) | No | No |
| IT | How-to question | No | No |
| HR | Benefits question | No | Yes |
| HR | Payroll question | No | Yes |
| HR | Leave request | Yes, manager | Yes |
| HR | Onboarding or offboarding | No | Yes |
| HR | Employment letter | No | Yes |
| HR | Policy question | No | No |
| Facilities | Maintenance or repair | No | No |
| Facilities | Workspace or move | Yes, manager | No |
| Facilities | Badge or building access | Yes, manager | No |
| Finance | Expense reimbursement | Yes, manager | No |
| Finance | Purchase request | Yes, manager, and Finance above threshold | No |
| Finance | Vendor or invoice question | No | No |

---

## 8. Assumptions and constraints

### Assumptions

- A-01. Request volume stays near 600 per month during the build.
- A-02. Each request belongs to exactly one owning team.
- A-03. Team leads are willing to agree on one shared taxonomy.
- A-04. Employees will use a web form if it is faster than email and shows status.

### Constraints

- C-01. Slice 1 uses synthetic data only. No real names, emails, or request text.
- C-02. Hosting stays on free tiers: Supabase for Postgres, Streamlit Community
  Cloud for the dashboard.
- C-03. No n8n or workflow automation in Slice 1. Routing is simulated in the
  data and the rules layer.
- C-04. AI accuracy is never stated without a labeled evaluation behind it.

---

## 9. What this project does not claim

- It does not claim the baseline figures describe any real company.
- It does not claim a measured return on investment. All savings are modeled,
  with the assumptions shown.
- It does not claim AI accuracy until the labeled evaluation in Slice 2 is
  published.
- It does not claim the synthetic data behaves like real employee requests. Real
  requests are messier, and the Slice 2 labeled set is where that gap is tested.
- It does not claim to replace an enterprise service management platform.

---

## 10. Decisions made at kickoff

| # | Decision | Date | Rationale |
|---|---|---|---|
| D1 | Standalone repo `ai-service-operations-hub` | 2026-09-22 | Can be pinned and reviewed on its own |
| D2 | Delivery in three slices, Slice 1 first, no n8n in Slice 1 | 2026-09-22 | A working, deployed slice beats ten half-built phases |
| D3 | Confidence thresholds: auto-route 90%+, route and flag 70 to 89%, human triage under 70% | 2026-09-22 | Keeps a person in the loop where the model is least certain |
| D4 | Power Automate leg out of scope | 2026-09-22 | Focus on the core Postgres, AI, and dashboard path |
| D5 | ROI labeled "modeled", AI accuracy measured on a labeled set | 2026-09-22 | Honesty rule for the whole build |

---

## 11. Open questions for the sponsor

| # | Question | Owner | Needed by |
|---|---|---|---|
| Q1 | Should sensitive HR categories always go to human triage, regardless of AI confidence? | COO with HR Ops Manager | Phase 2 |
| Q2 | Who owns the taxonomy, and who approves adding or changing a category? | COO | Phase 2 |
| Q3 | Will the shared inboxes be retired, or run in parallel with the form? For how long? | COO with team leads | Phase 2 |
| Q4 | What purchase amount requires Finance approval in addition to the manager? | Finance Manager | Phase 2 |
| Q5 | Who sets the SLA target for each category? | COO with team leads | Phase 2 |
| Q6 | May request text be sent to an external AI API, and under what data processing terms? | IT Security and Privacy | Before any real data |
| Q7 | Are chat messages and walk-ups captured in the new process, or redirected to the form? | Team leads | Phase 2 |

---

## 12. Next phase

Slice 1, Phase 2: requirements and future state. Functional and non-functional
requirements with IDs, user stories with acceptance criteria, the future-state
process map, SLA targets by category, and the finalized taxonomy.
