---
name: technology-implementation-pre-implementation-qualification
description: >
  Qualify a PRE-IMPLEMENTATION engagement — advisory work BEFORE a build is committed: digital/ERP
  strategy, readiness assessment, software evaluation and selection, business-case and roadmap work.
  Use when the scope describes choosing a platform, assessing readiness, or building the case/roadmap
  for a future system. Distinguish from implementation (the build itself), optimization (improving a
  live system), and managed-services (ongoing run/support).
---

# Technology Implementation — Pre-Implementation Qualification

Loaded when the classifier labels an opportunity `technology-implementation / pre-implementation`.
Your job: confirm this is advisory work BEFORE a committed build, qualify it against the firm's ICP
and approach, and compile the package the **delivery / proposal team** needs to scope a response.

## When this applies
Front-of-funnel advisory that precedes (and often leads into) an implementation:
- **Digital / ERP strategy** — future-state vision, target operating model, technology roadmap.
- **Readiness assessment** — is the organization, its data, and its processes ready for a build?
- **Software evaluation & selection** — assessing ERP/platform options against requirements.
- **Business case / roadmap** — justifying and sequencing a future investment.
The defining fact: NO build is committed yet. The output is a decision, a plan, or a recommendation,
not a configured system.

## The firm's evaluation approach (the credibility signal)
The firm brings a **software-agnostic, process-based** approach to evaluation — assessing options
across strategy, process, human capital, technology, and risk management, mapping business
requirements to platform capabilities for both cloud and on-premise options. Encode this: a genuine
pre-implementation engagement is vendor-neutral selection/strategy, not a thinly-disguised pitch for
one platform. That neutrality is a strength to surface and a thing to confirm the buyer wants.

## The boundary test (this skill's hardest job)
- **vs implementation:** has a build been COMMITTED? If the buyer has chosen a platform and wants it
  built, that's `implementation`. If they're still deciding whether/what to build, it's pre-implementation.
  "Help us select an ERP" = pre-implementation; "implement the ERP we selected" = implementation.
- **vs optimization:** pre-implementation precedes a system; optimization improves one that's live.
- **vs managed-services:** pre-implementation is bounded advisory; managed services is ongoing run.
A live RFP for a *build* is implementation; an RFP for *help choosing or planning* is this skill.

## Qualification rubric
- **Pre-commitment confirmation:** is the buyer still deciding (strategy, selection, readiness, case)?
  If a platform is already chosen and funded for build, re-check — this may be `implementation`.
- **Engagement type:** strategy/roadmap | readiness assessment | software evaluation & selection |
  business case. Which one (or which sequence)?
- **Lead-into-build potential:** pre-implementation is the front of the funnel — a strong selection or
  strategy engagement often leads directly into the implementation. Flag the downstream opportunity;
  it raises the strategic value even when the immediate fee is smaller.
- **Industry & ICP fit:** the firm's vertical depth (manufacturing, mining, A&D, healthcare, life
  sciences, government contracting, etc.) strengthens a strategy/selection engagement.
- **Neutrality fit:** does the buyer want vendor-neutral guidance (the firm's strength), or have they
  effectively pre-decided? A pre-decided buyer wanting rubber-stamp validation is a weaker fit.
- **Disqualifiers / flags:** a build that's actually committed mislabeled as "strategy"; a selection
  engagement where the buyer wants the firm to endorse a platform the firm doesn't deliver (sets up a
  downstream off-alliance problem — surface it).

## ICP signals specific to pre-implementation
General ICP (size, US-based, vertical) lives in `config/icp.py`. Strong pre-implementation fit tends
to look like: an enterprise or upper-mid-market organization facing a transformation decision (aging
platform, acquisition, growth) that hasn't yet chosen a path, wants vendor-neutral guidance, and
represents a credible lead into a future implementation on an alliance platform.

## Route to & package to compile
**Target team:** delivery / proposal team.
Compile into `team_package`:
- `engagement_type`: strategy/roadmap | readiness | evaluation & selection | business case
- `decision_stage`: how far from a build commitment (exploring / selecting / case-building)
- `neutrality`: vendor-neutral selection vs buyer-pre-decided
- `lead_into_build`: likelihood and shape of a downstream implementation
- `industry`: vertical + whether it's an area of named depth
- `downstream_alliance_flags`: whether the likely platform choice is on/off alliance
- `open_questions`: what's missing to scope

## Readout template
Lead with the verdict in one sentence a partner can act on in ten seconds (what kind of advisory,
how close to a build decision, lead-into-build potential), then deal shape (typically a shorter,
fixed-fee advisory engagement that may precede a much larger build), then the compiled package.