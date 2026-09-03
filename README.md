# Magaly Gonzalez Reyes | Portfolio

My portfolio site and the projects behind it. The site is a single static page, no build step, no framework. Each project lives in its own folder under `projects/` with its own README, docs, and code.

Site: https://magalygonzalezreyes.netlify.app

## Projects

| Project | What it is | Live |
|---|---|---|
| [Project Command Center](projects/project-command-center) | Portfolio-management dashboard that tracks projects like a CRM: KPIs, budget vs. actual, priority scoring with a funding-line slider, and PM capacity with burnout flags. Streamlit + pandas + Plotly, with a validation layer that catches every planted defect in the seed data. | [Open](https://project-command-center-mg.streamlit.app) |
| [Tower Activation Readiness](projects/tower-activation-readiness) | Cutover readiness dashboard for a building activation: assets by floor and unit, phase funnel, blockers, days-to-cutover flags. Streamlit + pandas, with a CSV validation step up front. | [Open](https://tower-activation-readiness.streamlit.app) |

Each project folder includes a requirements doc, a data model, and a build log, because the thinking is as much the work as the code.

## Repo layout

```
index.html                  the site (HTML + CSS + about 30 lines of JS)
assets/                     favicon, share image, screenshots
resume/                     résumé PDF
netlify.toml                publish config and security headers
portfolio-build-spec.md     the spec the site was built from
projects/
  project-command-center/   Streamlit app, docs, seed data
  tower-activation-readiness/
```

## Notes

All project data is fictional. Case studies from client work are described without client-identifying details.

The site's design tokens, layout, copy, and behavior follow `portfolio-build-spec.md`.
