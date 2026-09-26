# MCEnvstore — Agent Training Environment Platform

English | [简体中文](README.zh-CN.md)

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Single file](https://img.shields.io/badge/build-none%20(plain%20HTML)-brightgreen.svg)](index.html)
[![Bilingual](https://img.shields.io/badge/i18n-EN%20%7C%20ZH-6ee7d1.svg)](#internationalization)

> A model's ceiling is set by its training environments.
> MCEnvstore is a landing page for a platform where anyone who knows *what tasks are worth training*
> can contribute them — and the platform turns them into trainable, verifiable, anti-cheating,
> gradable environments.

This repository contains the **landing page / interactive prototype**, not the platform backend.
See [Status & known limitations](#status--known-limitations) for exactly what is and is not real.

---

## What this is

A single-file, buildless, dependency-free dark-theme landing page. Eleven sections, an embedded
EN/ZH dictionary, scroll-reveal animations, and a working environment-store filter — all inside
one `index.html` plus four self-hosted font files.

The page argues one thesis: **the long tail of agent capability is limited by who gets to decide
what is worth training.** If a handful of model companies pick the tasks, agent ability is locked
inside those companies' horizon. So the page proposes making environment contribution as easy as
posting a video — and shows the pieces that would make it work.

## The idea

### The core contradiction

Today training environments come from two sources: synthesized in-house by engineers, or procured
from data vendors. Both are bottlenecked by the same thing — a small group deciding, on everyone
else's behalf, which tasks matter. Coverage is limited by team size and domain knowledge, and no
data vendor knows what is genuinely worth training inside every industry, every company, and every
niche software product.

> Chasing an infinite distribution of tasks with finite labor — that's the fundamental contradiction.

### Why it can work like TikTok

TikTok does not produce content, yet it has more content than any TV station. The page applies the
same logic to environments: an accountant knows the pitfalls of reconciliation, a lawyer knows the
critical clauses in contract review, an SRE knows the incident investigation playbook. None of them
needs to understand RL or write a verifier — they only need to know that this is a task an agent
should learn.

## What the platform does

Four capabilities the page claims should be platform-level infrastructure rather than wheels every
model company reinvents:

### 1. Automated verifier generation

Upload a task and describe what counts as done. The platform generates a verifier by task type:
code tasks become tests derived from a reference implementation; rule-based tasks become executable
checks; document tasks become a rubric from expected output; open-ended tasks become a grouped
rubric built from multiple reference solutions. Contributors confirm or fine-tune — no coding from
scratch.

### 2. Anti-cheating audit

Once an environment is public, models will try every trick to cheat — it is an arms race. Every
environment runs through a "Hack Agent" before launch to detect answer leakage, irrelevant-action
bypass, and plausible-but-wrong constructions. Fix what can be fixed, delist what cannot.
Trajectories are audited continuously during training, and cheating rewards are zeroed.

### 3. Grader as a Service

Binary pass/fail is not enough. Two grading modes: **GRS** with task-specific rubrics for offline
synthesis, and **GAR** with online pairwise comparison and advantage redistribution. Model
companies call a unified API instead of implementing graders themselves.

### 4. Isolation and standardization

Every environment runs in its own container behind a unified Gym interface — resettable,
reproducible, versioned. Network isolation, file isolation, and resource quotas are defaults.

## The MCP collector

The lighter contribution path: put the collector inside the agent product you already use. Add one
line of MCP config to Codex, Cursor, Claude Code, MiMo Code, or similar, then work as usual.

The collector listens quietly and only flags high-value fragments — many back-and-forths, you
correcting the agent, you finally saying "that's it, looks good." It packages the workflow into a
**local environment draft**, then runs **local anonymization**: company names, project names,
person names, emails, API keys, and real financial figures are all replaced with placeholders while
structure is preserved. Nothing leaves the device until you click "Confirm contribution."

## The environment store

GitHub-style browsing and collaboration, App Store-style ratings and consumption. Six example
environments span finance, legal, DevOps, education, customer support, and code — with a working
category filter across all seven categories.

> A single financial reconciliation environment contributed by an accountant may be more valuable
> than a hundred generic finance tasks synthesized by a model company.

## Incentives

Revenue sharing (tokens paid by model companies are distributed proportionally to contributors),
reputation points (community ratings, early review rights, beta access), and access rewards
(contributing environments earns access to others or priority testing of new models).

The page's argument for why this compounds better than video: video traffic decays, but a validated
environment can be reused, iterated on, and composed — and may keep appreciating as more models
consume it.

## Tech notes

### Architecture

Plain HTML, CSS, and vanilla JavaScript in one file. No bundler, no framework, no runtime
dependency, no network calls at load time.

### Internationalization

Three attribute-driven hooks drive the EN/ZH switch, so adding a language is a dictionary edit
rather than a markup edit:

| Attribute | Applies to |
|---|---|
| `data-i18n` | Element `innerHTML` (allows inline `<br>` and gradient spans) |
| `data-i18n-placeholder` | Input `placeholder` |
| `data-i18n-label` | `data-label`, consumed by CSS `::before` content |

The chosen language is persisted to `localStorage` and re-applied before first paint.

### Self-hosted fonts

Inter (400/500/600) and JetBrains Mono (400) are served as local `woff2` files from
`assets/fonts/` — about 100 KB total, no third-party CDN. This keeps the page fully self-contained
and avoids depending on any vendor font host.

### Verified responsive

Layout was checked by measuring `getBoundingClientRect()` against the viewport at three widths,
rather than by eyeballing screenshots:

| Viewport | Overflowing elements |
|---|---|
| 390 px | 0 |
| 768 px | 0 |
| 1440 px | 0 |

## Run locally

No install step. Any static server works:

```bash
git clone https://github.com/possibleme2026-lang/mcenvstore.git
cd mcenvstore
```

```bash
python -m http.server 8000
# then open http://localhost:8000
```

Opening `index.html` directly via `file://` also works, since there are no module imports.

## Repo layout

```text
.
├── index.html                 # the entire landing page
├── assets/fonts/              # self-hosted woff2 (Inter, JetBrains Mono)
├── thumbnail.png              # social preview image
├── LICENSE                    # Apache-2.0
├── README.md                  # English (this file)
├── README.zh-CN.md            # 简体中文
└── tools/check_readme_i18n.py # bilingual structure guard
```

## Status & known limitations

This is a **design prototype**, and the page is honest about which parts are illustrative:

- The waitlist form does **not** submit anywhere. It validates the email and swaps the button label.
  There is no backend in this repository.
- The six store environments, their ratings, prices, and author handles are **sample data** for
  layout purposes.
- The MCP config block and the anonymization preview card are **mock UI**, not a working collector.
- Partner logos (Codex, Cursor, Claude Code, MiMo Code) are placeholders in a "first partners are
  joining" slot and do not imply any endorsement or affiliation.
- Nav links and footer links to Docs / API / Team / Blog point to `#` — those pages do not exist yet.

## Contributing

Issues and pull requests are welcome. If you change user-visible copy, update **both**
`README.md` and `README.zh-CN.md` and run the structure guard:

```bash
python tools/check_readme_i18n.py
```

The same change should be mirrored in the `en` and `zh` dictionaries inside `index.html`.

## License

[Apache License 2.0](LICENSE). See the file for the full text.
