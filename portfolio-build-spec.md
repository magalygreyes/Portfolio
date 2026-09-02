# Build Spec — Magaly Gonzalez Reyes, Portfolio Site

Hand this to a coding agent as-is. It contains everything needed to build the site: tokens, layout, content, and behavior. No design decisions are left open.

**Goal:** single-page responsive portfolio for a Business Analyst, targeting enterprise/corporate recruiters (legal, healthcare, financial services) plus freelance automation clients. Static site — no backend required.

---

## 1. Stack

- Static HTML + CSS, or Next.js / Astro / Vite if the agent prefers a framework. No CMS.
- No JS framework required. Total interactive JS is ~30 lines (see §7).
- Deploy target: Netlify (drag-and-drop or Git). Single route: `/`.
- Fonts via Google Fonts: **Archivo** (400, 500, 600, 700) and **IBM Plex Sans** (400, 500) and **IBM Plex Mono** (400, 500).

---

## 2. Design tokens

### Color

| Token | Hex | Use |
|---|---|---|
| `--ink` | `#1E293B` | Body text, dark section backgrounds, primary buttons |
| `--ink-strong` | `#0F172A` | Primary button hover |
| `--bg` | `#F8FAFC` | Page background, text on dark |
| `--surface` | `#FFFFFF` | Cards |
| `--surface-alt` | `#EEF2F7` | Image placeholder fill |
| `--border` | `#E2E8F0` | All 1px borders and grid dividers |
| `--border-strong` | `#CBD5E1` | Secondary button border |
| `--accent` | `#2563EB` | Cobalt: links, eyebrow labels, active nav, contact block, résumé CTA |
| `--accent-hover` | `#1D4ED8` | |
| `--accent-light` | `#60A5FA` | Accents on dark backgrounds |
| `--accent-pale` | `#BFDBFE` / `#DBEAFE` | Eyebrow + body text inside the cobalt contact block |
| `--muted` | `#64748B` | Meta text, mono labels |
| `--body` | `#475569` | Paragraph text |
| `--body-strong` | `#334155` | Lead paragraphs |
| `--success` | `#059669` | "Open to work" dot |
| `--success-bg` | `#ECFDF5` | "Open to work" pill background |
| `--success-border` | `#A7F3D0` | |
| `--success-text` | `#047857` | |
| `--metric` | `#6EE7B7` | Outcome numbers inside dark case-study panels |

Color rationale (keep it): slate + ice reads as enterprise-credible; cobalt is the single action color; green appears **only** on availability and outcome metrics so a recruiter's eye lands on results. Do not add a fourth hue.

### Type

| Role | Font | Size | Weight | Tracking | Line height |
|---|---|---|---|---|---|
| H1 | Archivo | `clamp(40px, 5vw, 72px)` | 700 | `-0.035em` | 1.02 |
| H2 (section) | Archivo | `clamp(32px, 3.6vw, 50px)` | 700 | `-0.03em` | 1.05 |
| H2 (contact) | Archivo | `clamp(34px, 5vw, 68px)` | 700 | `-0.035em` | 1.0 |
| H3 (card/job title) | Archivo | 21–25px | 600 | `-0.02em` | — |
| Case-study header | Archivo | `clamp(20px, 2.2vw, 28px)` | 600 | `-0.02em` | — |
| Lead paragraph | IBM Plex Sans | 19px | 400 | — | 1.65 |
| Body | IBM Plex Sans | 15–16.5px | 400 | — | 1.6–1.7 |
| Card body | IBM Plex Sans | 14.5px | 400 | — | 1.6 |
| Metric number | Archivo | 28–30px | 700 | `-0.03em` | — |
| Eyebrow / label / nav / button | IBM Plex Mono | 10.5–12.5px | 400 | `0.05em–0.12em`, uppercase | — |

Paragraphs use `text-wrap: pretty`. Max measure: `52ch` (lead), `58–62ch` (body).

### Spacing & shape

- Page max width `1400px`, horizontal padding `40px` (desktop), `20px` (mobile).
- Section vertical rhythm: `96px` top/bottom; hero `88px 40px 72px`.
- Radii: `6px` buttons/labels, `8px` metric tiles & stat cells, `10px` cards & case-study containers, `14px` contact block.
- Borders always `1px solid var(--border)`. No drop shadows except card hover.
- Card hover: `border-color: var(--accent)`, `box-shadow: 0 10px 28px rgba(30,41,59,0.1)`, `transform: translateY(-3px)`, `transition: .2s ease`.
- Striped image placeholders: `background-color: var(--surface-alt)` + `background-image: repeating-linear-gradient(135deg, rgba(37,99,235,0.1) 0 9px, transparent 9px 18px)`, with a mono caption chip bottom-left.

---

## 3. Page structure

Order top to bottom. Section ids are the nav anchor targets.

1. **Sticky header**
2. `#home` — hero
3. Dark credential ticker strip
4. `#about`
5. `#projects`
6. `#case-studies` (dark band)
7. `#work` — experience + certifications + education
8. `#contact` + footer

### Sticky header
`position: sticky; top: 0; z-index: 50`, background `rgba(248,250,252,0.9)` + `backdrop-filter: blur(12px)`, bottom border `--border`, padding `14px 40px`, three-part flex row:
- Left: "Magaly Gonzalez Reyes" (Archivo 700, 18px) + "BUSINESS ANALYST" (mono 11px, `--muted`), baseline-aligned, links to `#home`.
- Center: nav links — Home, About, Projects, Case studies, Experience, Contact. Mono 11.5px uppercase, `8px 13px` padding, `6px` radius. Active link: white text on `--accent`. Inactive: `--body`, transparent.
- Right: **Download résumé** button — cobalt fill, white mono text, `11px 18px`, `6px` radius, hover `--accent-hover`.

### `#home` — hero
Two-column grid `1.4fr 1fr`, gap `56px`, `align-items: start`.

Left column (stacked, gap `28px`):
1. Availability pill: green dot + "OPEN TO FULL-TIME, CONTRACT & FREELANCE", green-tinted background/border, `6px` radius, self-start.
2. H1 (see §4 for copy), max `20ch`, period at the end colored `--accent`.
3. Lead paragraph, max `58ch`.
4. Button row: "SEE CASE STUDIES" (slate fill) + "GET IN TOUCH" (outline, hover border/text cobalt).
5. Stat strip — 4 equal cells in a `1px` gap grid with `--border` as the gap color, `8px` radius, overflow hidden. Cells: `10+` / Years in BA work · `$80K` (cobalt) / Annual savings delivered · `70%` / Faster reporting turnaround · `CSM` / Certified ScrumMaster.

Right column (gap `14px`):
1. Headshot slot, `aspect-ratio: 4/5`, `10px` radius, striped placeholder until the real photo is dropped in.
2. "At a glance" card — white, `--border`, `8px` radius, `20px` padding. Mono eyebrow, then label/value rows (`justify-content: space-between`, 14.5px): Based in → Rodeo, CA · remote; Industries → Legal, healthcare, IT; Delivery → Agile & Waterfall; Languages → English, Spanish; then a divided row: Links → LinkedIn · GitHub.

### Ticker strip
Full-bleed `--ink` band, `14px 40px`, mono 12px uppercase `0.1em`, color `#E2E8F0`. Items separated by `◆` diamonds in `--accent-light`. **Must wrap** (`flex-wrap: wrap; gap: 12px 30px`) — never `overflow: hidden` with `nowrap`, or content gets clipped on narrow screens.
Items: Orrick, Herrington & Sutcliffe ◆ Kaiser Permanente ◆ Requirements & process mapping ◆ Power Platform automation.

### `#about`
Two-column grid `0.75fr 1.25fr`, gap `56px`. Left: mono eyebrow `01 / ABOUT` in cobalt + H2 "How I work". Right: two paragraphs, then a 3-cell capability grid (same `1px`-gap technique, white cells, `22px` padding): Business analysis / Data & reporting / Systems & tools.

### `#projects`
Header row: left eyebrow `02 / PROJECTS` + H2 "Selected work"; right, baseline-aligned, mono "2018 — 2026".
Below: 2×2 card grid, `20px` gap. Each card is an `<a href="#case-studies">` containing: 16:10 striped image slot with caption chip → mono meta line (`Company · Role`) → H3 title → one-line outcome sentence.

### `#case-studies`
Full-bleed `--ink` background, `--bg` text, `96px 40px`. Eyebrow `03 / CASE STUDIES` in `--accent-light`, H2 "The work in detail" (max `22ch`).
Two accordion items, `12px` apart. Each: container with `1px solid rgba(226,232,240,0.18)`, `10px` radius, `background: rgba(248,250,252,0.03)`.
- **Header** = full-width `<button>`, `26px 28px`, transparent, `cursor: pointer`, hover `rgba(248,250,252,0.05)`. Left: mono letter (`A`/`B`) in `--accent-light` + title. Right: mono `READ` / `CLOSE` in `--accent-light`.
- **Panel** = two-column grid `1fr 1fr`, gap `40px`, padding `0 28px 30px`. Left: Context / My role / Approach blocks (mono uppercase label in `#94A3B8`, then 15.5px body in `#E2E8F0`) followed by two metric tiles (`flex: 1; min-width: 150px`, `rgba(248,250,252,0.06)` fill, `8px` radius, Archivo 28px number in `--metric` + mono caption). Right: a 4:3 and a 16:9 striped image slot.
- Item A open by default; item B closed.

### `#work`
Two-column grid `0.75fr 1.25fr`, gap `56px`.
Left: eyebrow `04 / EXPERIENCE`, H2 "Where I've worked", cobalt **Download full résumé** button, then a divided block listing Certifications and Education (mono uppercase labels, 14.5px items).
Right: five timeline rows. Each row is a `120px 1fr` grid, `24px` gap, `26px` vertical padding, `border-top: 1px solid var(--border)` (last row also `border-bottom`). Left cell: mono date range in `--muted`. Right cell: H3 `Title · Company`, mono location line, then a 15px description capped at `62ch`.

### `#contact` + footer
Cobalt block, `14px` radius, padding `clamp(36px,5vw,72px)`, `--bg` text, stacked gap `30px`:
- Eyebrow `05 / CONTACT` in `--accent-pale`.
- H2 "Let's talk about the role." (max `18ch`).
- Paragraph in `#DBEAFE`, max `52ch`.
- Button row (wraps): email (white fill, `#1E3A8A` text) · phone (outline) · DOWNLOAD RÉSUMÉ (outline) · LINKEDIN (outline) · GITHUB (outline). Outline = `1px solid rgba(248,250,252,0.5)`, hover fill `rgba(248,250,252,0.12)`.
Footer below the block: mono 11px `--muted`, space-between — "© 2026 Magaly Gonzalez Reyes" / "Rodeo, CA · Available remote".

---

## 4. Content — use verbatim

### Hero
- H1: **I turn messy business processes into systems leadership can act on.**
- Lead: Business Analyst with 10+ years eliciting requirements, mapping current- and future-state processes, and translating business needs into technical specifications across healthcare, legal, and enterprise IT. I build the dashboards and automated reporting leadership relies on, and I have delivered $30,000 to $80,000 in annual savings through workflow standardization and automation.

### About — "How I work"
- P1: I start where the friction is. Workshops and stakeholder interviews first, then current- and future-state process maps, gap analysis, and requirements documented clearly enough that engineering, business, and leadership all work from the same source of truth through build, UAT, and adoption.
- P2: The part I care most about is what happens after launch. Standardized documentation, governance that holds, dashboards leadership actually opens, and training that gets people using the thing. Increasingly that also means building the automation myself — Power Platform, SharePoint, and AI agents that take recurring reporting off people's plates.
- Capability cells:
  - **Business analysis** — Requirements elicitation, BRDs, user stories and acceptance criteria, traceability, UAT planning
  - **Data & reporting** — Dashboard design, KPI and milestone tracking, executive summaries, SQL, advanced Excel
  - **Systems & tools** — Microsoft 365, SharePoint, Power Automate, Power Apps, Jira, Azure DevOps, ServiceNow, Visio

### Projects (4 cards)
1. `Orrick · IT Business Analyst II` — **Internal AI agent for workflow documentation** — Automated recurring reporting and workflow docs, cutting turnaround roughly 70% — from 6–8 hours to about 2.
2. `Kaiser Permanente · Business Analyst` — **Standardizing manual operational workflows** — Approval logic, status notifications, and task routing automated across departments: $30K–$80K saved annually.
3. `Kaiser Permanente · Senior Operations Specialist` — **Appointment fulfillment across five facilities** — Demand and utilization analysis surfaced the process gaps behind a 78% increase in appointment fulfillment.
4. `Independent · End-to-end` — **Multi-agent automation for a small ops team** — Replaced manual data entry, scheduling, and reporting handoffs: 50+ manual hours per week down to under 20.

### Case study A — Cutting documentation turnaround 70% with an internal AI agent
- **Context:** Orrick, Herrington & Sutcliffe · IT Business Analyst II · workflow documentation and recurring status reporting consumed 6 to 8 hours per cycle, pulled from people who should have been solving problems instead.
- **My role:** Requirements, solution design, build, and rollout. I documented the current-state process, defined what "good enough to ship" meant for each deliverable, then designed and deployed the agent myself.
- **Approach:** Mapped the repeatable structure hiding inside each document type, established the governance standards the output had to meet, wired the agent into the existing SharePoint and Power Platform stack, and trained business users on the review step that stayed human.
- **Metrics:** `~70%` Faster turnaround · `8 → 2 hrs` Per reporting cycle
- **Images:** before/after — manual doc vs. agent output (4:3); process map or Power Automate flow (16:9)

### Case study B — $30K–$80K in annual savings from workflow standardization
- **Context:** Kaiser Permanente · Business Analyst · operational workflows ran on manual approvals, ad-hoc email notifications, and task routing that depended on who happened to be watching.
- **My role:** Current- and future-state mapping, gap analysis, and requirements across clinical, operational, and IT stakeholders with competing priorities — then the build in Microsoft Forms, Teams, and SharePoint.
- **Approach:** Documented inefficiencies, risks, and dependencies to build the case for one standardized solution rather than department-by-department fixes. Automated approval logic, status notifications, and task routing, then shipped self-service dashboards so teams stopped requesting reports.
- **Metrics:** `$30–80K` Saved annually · `−50%` Operational errors
- **Images:** future-state process map (4:3); self-service dashboard screenshot (16:9)

### Experience timeline
| Dates | Title · Company | Location | Description |
|---|---|---|---|
| 2022 — 2026 | IT Business Analyst II · Orrick, Herrington & Sutcliffe LLP | San Francisco, CA — remote | Translated business requirements into technical specifications and user stories for globally distributed teams, ran requirements workshops, coordinated launch through UAT, and built Power Platform and SharePoint dashboards giving leadership real-time visibility. |
| 2020 — 2022 | Business Analyst · Kaiser Permanente | Oakland, CA | Mapped current- and future-state processes, performed gap analysis, and automated manual operational workflows for $30K–$80K in annual savings across departments. |
| 2018 — 2020 | Senior Operations Specialist · Kaiser Permanente | Oakland, CA | Analyzed demand and utilization across five East Bay facilities, driving a 78% increase in appointment fulfillment and a 50% reduction in operational errors. Designed a SharePoint schedule-change portal saving $30,000+ annually. |
| 2016 — 2018 | Operations Coordinator · Kaiser Permanente | Oakland, CA | Standardized departmental processes, delivered cross-functional training, and facilitated feedback loops between frontline staff and executive teams. |
| 2014 — 2016 | Earlier roles · Kaiser Permanente | — | Access Operations Coordinator, Senior Staff Assistant, Member Outreach Coordinator and Spanish Interpreter. |

### Certifications
- Certified ScrumMaster (CSM), Scrum Alliance
- Claude Certified Architect (CCA) Foundations, Anthropic
- Agile Product Owner · Agile Testing · Agile Foundations

### Education
- AS, Computer & Information Sciences — Diablo Valley College
- BA, Business Administration & Management — Kendall College
- BBA, Hospitality & Business Administration — Les Roches, Switzerland

### Contact
- H2: **Let's talk about the role.**
- Paragraph: Open to Business Analyst and Senior BA roles, contract engagements, and freelance automation work. I answer everything within a day.
- Email: `magaly.g.reyes@gmail.com` (`mailto:`)
- Phone: `201.597.1489` (`tel:2015971489`)
- LinkedIn: **TO FILL IN** — résumé currently reads `linkedin.com/in/YOUR-HANDLE`
- GitHub: **TO FILL IN**
- Résumé: link to a PDF at `/resume/Magaly-Gonzalez-Reyes-Business-Analyst.pdf` with the `download` attribute. Source file today is `.docx` — convert to PDF; recruiters open PDFs.

---

## 5. Assets still needed

| Slot | Ratio | What goes there |
|---|---|---|
| Hero headshot | 4:5 | Professional photo |
| Project card × 4 | 16:10 | Dashboard, flow diagram, utilization report, agent architecture map |
| Case study A | 4:3 + 16:9 | Before/after doc comparison; Power Automate flow |
| Case study B | 4:3 + 16:9 | Future-state process map; self-service dashboard |
| Résumé | — | PDF export |

Until real images exist, keep the striped placeholders with their mono captions — do not substitute stock photography or generated illustration. **Scrub client-identifying data from any screenshot** (names, matter numbers, patient data) before publishing.

---

## 6. Responsive rules

- **≥1100px:** as specified above.
- **760–1099px:** all two-column grids collapse to one column; hero image/at-a-glance moves below the text; project grid → 1 column; case-study panels → 1 column (metrics stay side by side); stat strip → 2×2.
- **<760px:** horizontal padding `20px`; H1 clamps to `40px`; center nav becomes a horizontally scrollable mono row (or a hamburger — designer's call, but the résumé button must stay visible in the header at all sizes); timeline rows stack date above title; contact buttons stack full-width.
- Minimum tap target `44px` on all buttons and nav items at mobile sizes.

## 7. Behavior

1. **Scroll-spy nav.** `IntersectionObserver` over the six section ids with `rootMargin: "-45% 0px -50% 0px"`; the intersecting section's nav link gets the cobalt active style. Nothing else changes on scroll — no scroll animations, no parallax.
2. **Smooth anchor scrolling.** `html { scroll-behavior: smooth }`. Header is sticky, so add `scroll-margin-top: 80px` to each section so headings aren't hidden under it.
3. **Case-study accordion.** Independent open/closed state per item (both can be open). Toggling swaps the panel between `display: grid` and `display: none` and flips the header label `READ` ⇄ `CLOSE`. A opens by default. Use a real `<button>` with `aria-expanded` and `aria-controls`; the panel gets an `id` and `role="region"`.
4. **Project cards** link to `#case-studies`. If per-project detail pages get built later, repoint them.
5. **No animation** beyond the card hover transform and button color transitions.

## 8. Accessibility & SEO

- Contrast: verify `--muted` `#64748B` on `#F8FAFC` (passes AA for the 11px+ mono use) and white on `--accent`. Do not lighten either.
- Every image slot needs real `alt` text describing the artifact, not "screenshot".
- Visible focus ring on all links and buttons: `2px solid var(--accent)`, `2px` offset (use `#F8FAFC` on the dark and cobalt sections).
- One `<h1>`; sections use `<h2>`; card and job titles `<h3>`. Wrap each in `<section aria-labelledby>`.
- `<title>`: Magaly Gonzalez Reyes — Business Analyst | Requirements, Process Mapping & Automation
- Meta description: Business Analyst with 10+ years in healthcare, legal, and enterprise IT. Requirements, process mapping, dashboards, and workflow automation delivering $30K–$80K in annual savings.
- Add Open Graph tags + a 1200×630 share image, `Person` JSON-LD, and a favicon from the initials `MG` in cobalt on ice.
- `prefers-reduced-motion`: disable the hover transform.
