# AI Service Operations Hub

**An AI-assisted intake, routing, and operations hub for employee service requests at a fictional 300-person company.**

`Business Analysis` · `Process Mapping` · `Requirements Engineering` · `PostgreSQL` · `Supabase` · `AI Classification` · `Streamlit`

> **Status:** Slice 1, Phase 1 (Discovery) complete. This case study is built in
> public, one phase at a time. Sections marked _Planned_ fill in as each phase ships.

---

## 01. Executive summary

Breezio, a fictional 300-person company, handles roughly 600 employee service
requests a month across IT, HR, Facilities, and Finance. Every one of them arrives
by email, chat, or walk-up. There is no single front door, no request ID, no
routing logic, and no service levels.

This project designs and builds a service hub that gives every request one entry
point and one ID, classifies and routes it with AI where the model is confident,
sends it to a person where it is not, and puts volume, speed, and service-level
performance on a live dashboard.

**Modeled current-state cost:** 2,772 coordinator hours a year, roughly $124,740,
spent moving requests around rather than resolving them. This is a modeled figure
with the assumptions shown in [`docs/process-maps.md`](docs/process-maps.md). It is not a measured result.

## 02. Business case

| Activity | Annual hours (modeled) |
|---|---|
| Initial triage and forwarding | 720 |
| Misroute rework | 216 |
| Missing-information follow-up | 540 |
| Approval chasing | 288 |
| Status inquiry handling | 360 |
| Manual logging | 360 |
| Month-end reporting | 288 |
| **Total** | **2,772** |

At $45 per hour, about $124,740 a year. Employee waiting time and the cost of
delay are excluded because they cannot be defended without real data.

## 03. Current-state process

Requests arrive through five channels. Coordinators read, forward, ask for
missing details, chase approvals, and answer "any update?" emails by hand.
Full narrative and swimlane map: [`docs/process-maps.md`](docs/process-maps.md).

## 04. Pain points

Eleven pain points, PP-01 to PP-11, each mapped to a KPI or an open question.
The largest: 18% of requests misrouted, 30% missing information at intake, and
no way to measure service levels because none exist.

## 05. Requirements

_Planned: Phase 2._

## 06. Future-state process

_Planned: Phase 2._

## 07. Solution architecture

_Planned: Phase 3._

## 08. Data model

_Planned: Phase 3._

## 09. AI design

Confidence thresholds are set: auto-route at 90% or higher, route and flag for
review at 70 to 89%, human triage below 70%. Full design _planned: Phase 4._

## 10. Automation

_Planned: Slice 2._

## 11. API integration

_Planned: Slice 2._

## 12. Testing

_Planned: Phase 6 (UAT) and Slice 2 (labeled accuracy evaluation)._

## 13. Dashboard

_Planned: Phase 5._

## 14. Results

_Planned. Results will separate modeled figures from measured ones._

## 15. Lessons learned

_Planned._

---

## Build plan

| Slice | Phase | Scope | Status |
|---|---|---|---|
| 1 | 1 | Discovery: problem, KPIs, stakeholders, current state | 🟢 Done |
| 1 | 2 | Requirements, user stories, future state, taxonomy, SLAs | 🟡 Next |
| 1 | 3 | Data model, Supabase schema, synthetic data generator | 🔴 Not started |
| 1 | 4 | AI classification and business rules | 🔴 Not started |
| 1 | 5 | SQL KPI queries and Streamlit dashboard, live URL | 🔴 Not started |
| 1 | 6 | UAT plan, traceability matrix, case study complete | 🔴 Not started |
| 2 | | Webhook API, n8n orchestration, approvals, labeled accuracy evaluation | 🔴 Not started |
| 3 | | Knowledge deflection (RAG), weekly AI summary, SLA escalation | 🔴 Not started |

## Artifact index

| Document | Contents |
|---|---|
| [`docs/discovery.md`](docs/discovery.md) | Problem statement, objectives BO-01 to BO-07, KPIs K1 to K11, scope, taxonomy draft, open questions |
| [`docs/stakeholders.md`](docs/stakeholders.md) | Register ST-01 to ST-09, influence grid, engagement, RACI, risks |
| [`docs/process-maps.md`](docs/process-maps.md) | Current-state map, pain points PP-01 to PP-11, modeled effort |
| [`docs/build-log.md`](docs/build-log.md) | Dated record of each phase |

## What this project does not claim

- The baselines are modeled for a fictional company, not measured anywhere.
- ROI is modeled, with every assumption shown.
- AI accuracy is not stated until a hand-labeled evaluation is published in Slice 2.
- This is not a replacement for an enterprise service management platform.

## A note on the data

Breezio, its employees, and its requests are fictional. No real organization,
person, or request is represented.
