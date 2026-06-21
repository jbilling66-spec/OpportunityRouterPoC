---
name: technology-implementation-managed-services-qualification
description: >
  Qualify an enterprise system MANAGED SERVICES engagement — ongoing operate, run, and support of a
  live system under a continuous service relationship (SLAs, application support, hosting, end-user
  support, often bundled continuous improvement). Use when the scope describes ongoing support,
  application management, an SLA-backed service, or a subscription support model. Distinguish from
  implementation (net-new build), optimization (a bounded improvement project), and pre-implementation
  (pre-build advisory).
---

# Technology Implementation — Managed Services Qualification

Loaded when the classifier labels an opportunity `technology-implementation / managed-services`.
Your job: confirm this is an ONGOING service relationship (not a one-time project), qualify it
against the firm's platform alliances and ICP, and compile the package the
**delivery / proposal team** needs to scope a response.

## When this applies
Ongoing operate/run/support of a live enterprise system: application support and maintenance,
hosting and cloud-infrastructure operations, end-user support, release/patch management, and often
bundled continuous improvement — all under defined SLAs with regular performance reviews. The
defining fact: a CONTINUOUS relationship with recurring scope, not a project with an end state.
The firm's named model here is "Continuum" — a monthly fixed-fee subscription covering both
application support and ongoing continuous improvement (CI).

## The boundary test (this skill's hardest job)
- **vs optimization:** is this CONTINUOUS support, or a BOUNDED improvement project? An SLA-backed,
  recurring, subscription-style relationship is managed services. A one-time "assess and improve"
  engagement with an end state is `optimization`. (Note the genuine overlap: Continuum bundles CI
  into ongoing support — so a deal can be managed services that INCLUDES optimization work. If the
  spine is a recurring service relationship, it's managed services even when CI is part of it.)
- **vs implementation:** managed services operates a system that's already live; implementation
  builds a new one. Post-go-live support that follows a build is managed services.
- **vs pre-implementation:** managed services runs an existing system; pre-implementation advises
  before a build is committed.
If the document reads as "keep our system running well over time, to a service level," it's this.

## Qualification rubric
- **Ongoing-vs-project confirmation:** is there a recurring term, an SLA, a subscription, "support,"
  "managed," "run," or "operate"? Recurring + SLA = managed services. A fixed deliverable with a
  closeout = probably optimization, re-check the route.
- **Scope of support:** application support | hosting / cloud infrastructure ops | end-user support |
  release & patch management | continuous improvement | security/vulnerability remediation. Which?
- **Platform alliance fit:** Oracle Cloud, IFS (Continuum is the IFS support model), Deltek Costpoint,
  Plex, OneStream, Sage Intacct, Salesforce. On-alliance is strong fit; off-alliance flags a gap.
- **Service-level expectations:** is there a stated uptime/availability target, incident-response
  expectation, or SLA? Concrete service levels signal a real, scopeable managed-services deal.
- **Commercial model:** recurring subscription / monthly fixed fee (the Continuum shape), T&M support
  retainer, or per-ticket? Recurring fixed-fee is the firm's preferred, highest-value shape.
- **Disqualifiers / flags:** a one-time project mislabeled as "managed services"; a support ask for an
  off-alliance platform the firm can't staff; expectations (e.g. 24/7 follow-the-sun) the delivery
  model can't meet — surface, don't silently accept.

## ICP signals specific to managed services
General ICP (size, US-based, vertical) lives in `config/icp.py`. Strong managed-services fit tends to
look like: an enterprise or upper-mid-market client live on an alliance platform that wants to
offload running it (often a client who concluded that operating the system isn't the best use of
their own resources), with defined service levels and an appetite for a recurring relationship —
frequently flowing naturally out of an implementation the firm just delivered.

## Route to & package to compile
**Target team:** delivery / proposal team.
Compile into `team_package`:
- `live_platform`: the system to be supported (+ alliance fit)
- `support_scope`: application | hosting/infra | end-user | release mgmt | CI | security
- `service_levels`: stated uptime / response / SLA expectations, or "none stated"
- `commercial_model`: subscription / monthly fixed fee | retainer | per-ticket
- `term`: recurring term length / renewal shape
- `follows_implementation`: whether this trails a build the firm did (warm continuation)
- `alliance_flags`: off-alliance or staffing concerns
- `open_questions`: what's missing to scope

## Readout template
Lead with the verdict in one sentence a partner can act on in ten seconds (what's being supported,
ongoing vs project, alliance fit), then deal shape (recurring subscription vs retainer, service
levels, term), then the compiled package.