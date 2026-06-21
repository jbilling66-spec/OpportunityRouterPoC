---
name: audit-advisory-strategy-advisory-qualification
description: >
  Qualify a STRATEGY ADVISORY engagement — the broad, non-attest advisory catch-all of the audit
  line, centered on strategy and management consulting. Spans corporate/growth strategy, profit
  improvement, commercial/market due diligence (esp. PE), organizational and operational performance
  (people/process/systems), governance, internal audit and ERM, board services, and public-sector
  operational consulting. Use for advisory work that strengthens strategy, operations, governance, or
  risk and ISN'T a specific audit, SOC report, or framework-certification prep. Distinguish from
  financial-statement-audit and soc-reporting (attest), compliance-readiness (framework-specific prep),
  and technology-implementation work.
---

# Audit Advisory — Strategy Advisory Qualification

Loaded when the classifier labels an opportunity `audit-advisory / strategy-advisory`.
This is the deliberately broad advisory bucket. Don't force it into rigid sub-types — instead match
the opportunity against the example engagements below, confirm it's non-attest advisory, qualify it
against the firm's ICP, and compile the package the
**risk advisory / strategy & management consulting team** needs.

## What this bucket covers
Non-attest advisory that improves an organization's strategy, operations, governance, or risk posture.
No opinion, report, or certification is issued — the output is analysis, a plan, a roadmap, an
improved function, or a recommendation. It is intentionally broad; the examples below show the range.

## Example engagements (match against these; the list is illustrative, not exhaustive)
- **Growth strategy.** Market, competitive-landscape, go-to-market, and operations analysis to drive
  revenue growth, using data-driven frameworks for C-level decisions.
- **Profit improvement.** Margin, cost-reduction, and revenue-generation work for middle-market and
  enterprise companies.
- **Commercial / market due diligence (PE).** "Quality of Strategy" for PE funds and independent
  sponsors — primary research on market dynamics and target positioning, "Day 1" growth plans, risk
  mitigation. Deadline-driven around a deal.
- **Operational performance (people / process / systems).** Holistic assessment of the operating
  environment to find root causes and improvement opportunities across people (right talent/roles/
  capacity), process (fix manual/burdensome workflows), and systems (integration, monitoring).
- **Organizational planning & strategy.** Vision-setting, change management, leadership/succession
  planning, prioritizing competing initiatives.
- **Governance.** Board/council/committee effectiveness — strategic leadership alignment,
  accountability processes, defined roles, audit-committee governance, IPO/regulatory-change readiness.
- **Internal audit & ERM.** Building or transforming an IA function (outsourced/co-sourced), risk-based
  audit planning, ERM program design (charters, risk committees, KRIs/KPIs, risk registers).
- **Human capital advisory.** HR transformation — culture, talent, workforce planning, performance
  management.
- **Capital projects advisory.** Construction-contract audits, performance/progress monitoring, risk
  reduction on capital programs.
- **Public-sector operational consulting.** Performance audits, organizational analysis, programmatic
  planning/monitoring/evaluation, policies-and-procedures consulting for government, higher-ed,
  not-for-profit, and Tribal entities.

## The boundary test (what pushes OUT of this bucket)
- **vs financial-statement-audit / soc-reporting:** is an opinion/report being ISSUED (attest)? If so,
  not this — strategy advisory is non-attest.
- **vs compliance-readiness:** is the work pinned to a SPECIFIC framework/certification (HITRUST, SOC 2,
  SOX, etc.)? That's compliance-readiness. Broad governance/strategy advisory not tied to a
  certification stays here.
- **vs technology-implementation / pre-implementation:** a technology *selection/strategy* tied to an
  ERP/system build routes to pre-implementation. Business/operational strategy not centered on a system
  build stays here (even if "systems" is one of the people/process/systems lenses).
- **vs tax / accounting:** financial-function work that's really tax planning or outsourced accounting
  routes to those lines.

## Qualification rubric
- **Which example(s) does it match?** Name the closest engagement type(s) from the list. Multiple is fine.
- **Buyer & driver:** operating company | PE fund/sponsor | portfolio company | public-sector entity
  (government, higher-ed, NFP, Tribal). Is there a board mandate, a transaction/diligence deadline, an
  IPO, a PE value-creation plan, a regulatory/leadership change, a performance/cost pressure, or a
  maturity gap? A named driver + sponsor = real, funded engagement.
- **Delivery model (IA/recurring work):** outsourced | co-sourced | advisory-only. Co-source/outsource
  and PE-portfolio relationships recur and are higher-value.
- **Public-sector fit:** government/higher-ed/Tribal performance and governance work is an area of named
  depth (and a strong fit signal) — flag it.
- **Disqualifiers / flags:** an attest engagement mislabeled as advisory; a framework certification that
  belongs in compliance-readiness; a system-selection that belongs in pre-implementation; a tax/
  accounting ask.

## ICP signals specific to strategy advisory
General ICP (size, US-based, vertical) lives in `config/icp.py`. Strong fit tends to look like: an
enterprise, upper-mid-market, PE fund/sponsor or portfolio company, or public-sector / mission-driven
entity (state and local government incl. city/county/special districts, Tribal governments, higher-ed,
not-for-profits, utilities) facing a strategy, growth, governance, or operational-performance inflection.
Recurring co-source and PE-portfolio relationships are especially valuable.

## Route to & package to compile
**Target team:** risk advisory / strategy & management consulting team.
Compile into `team_package`:
- `engagement_match`: closest example engagement(s) from the list
- `buyer_type`: operating company | PE fund/sponsor | portfolio company | public sector
- `driver`: board mandate | transaction/diligence | IPO | PE value creation | regulatory/leadership
  change | performance/cost pressure | maturity gap | growth/turnaround
- `delivery_model`: outsourced | co-sourced | advisory-only (where applicable)
- `public_sector`: whether it's a government/higher-ed/NFP/Tribal entity (named-depth signal)
- `recurring_potential`: one-time project vs ongoing / portfolio relationship
- `open_questions`: what's missing to scope

## Readout template
Lead with the verdict in one sentence a partner can act on in ten seconds (which kind of advisory, the
buyer and driver, recurring vs one-time), then deal shape (advisory engagement; co-source/recurring for
IA, deadline-driven for PE diligence, program-based for public sector), then the compiled package.