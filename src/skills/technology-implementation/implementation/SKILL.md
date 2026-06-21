---
name: technology-implementation-implementation-qualification
description: >
  Qualify a net-new enterprise system IMPLEMENTATION — a full-cycle build of an ERP or core
  business platform (select/design/configure/build/migrate/go-live). Use when the scope describes
  a greenfield or replacement system implementation, a re-implementation, or a major platform
  rollout. Distinguish from optimization (improving an existing live system), managed-services
  (run/support), and pre-implementation (advisory/readiness/roadmap before a build is committed).
---

# Technology Implementation — Implementation Qualification

Loaded when the classifier labels an opportunity `technology-implementation / implementation`.
Your job: confirm this is a true net-new build (not an upgrade or optimization in disguise),
qualify it against the firm's platform alliances and ICP, and compile the package the
**delivery / proposal team** needs to scope a response.

## When this applies
A full-cycle implementation of a core enterprise platform: platform selection through design,
configuration/build, data migration, testing, cutover, go-live, and hypercare. Includes
re-implementations (replacing a legacy system to enable process transformation, not just a
version upgrade). If the work improves or extends a system already live, that's `optimization`.
If it's ongoing operate/support, that's `managed-services`. If no build is committed and the ask
is readiness / roadmap / selection-only, that's `pre-implementation`.

## The firm's implementation methodology (four phases)
A well-formed implementation opportunity maps onto the firm's published delivery approach. Use the
phases to test whether the buyer has thought the work through and to shape the deal's phasing:
1. **Planning** — bridges objectives to a detailed implementation plan; addresses functionality,
   technology, and change management.
2. **Analyze and design** — defines the new business processes, information, and data for the
   target operating model.
3. **Build and test** — develops customizations, reports, forms, interfaces; end-to-end testing;
   plans conversion and cutover.
4. **Implement and support** — verifies configuration and testing, trains users, and stands up the
   support structure for and after go-live (hypercare).

## Platform alliance fit (a real qualifying signal)
The firm delivers implementations on a specific alliance set. Strong fit names one of:
- Oracle Cloud (ERP, EPM, HCM, SCM, Analytics) — premier Oracle PartnerNetwork member.
- IFS Cloud — deep practice (manufacturing, mining, asset-intensive, aerospace & defense).
- Deltek Costpoint — government contractors / federal marketplace (a distinct specialty).
- OneStream — CPM/EPM, unifying financial and operational data.
- Plex — manufacturing cloud (Industry 4.0, shop-floor).
- Sage Intacct / NetSuite — cloud financials (construction, not-for-profit, multi-entity).
- Salesforce — CRM-led transformation.
A deal on a platform OUTSIDE this alliance set isn't an automatic disqualifier, but flag it: it
means partnering, subcontracting, or a capability gap — material to the pursuit decision.

## Qualification rubric
- **True net-new (the boundary test):** is this a build, or an upgrade/optimization mislabeled?
  A version upgrade of a healthy live system is NOT this engagement. Extending existing features to
  new divisions/locations/lines of business is `optimization`, not implementation. A re-implementation
  to enable process transformation IS implementation. If ambiguous, note it — Tier-2 may be wrong.
- **Platform & scope clarity:** which platform, which modules (finance, SCM, HCM, procurement),
  how many entities/sites/users? Greenfield vs replacement of a named legacy system?
- **Forcing function & "why now":** the firm's named catalysts are aging platforms, new acquisitions,
  and accelerated growth — look for these. Is a platform selected yet? Live RFP, funded program,
  exec sponsor, hard go-live date? Funded + sponsored + dated = pursue now.
- **Change management scoped?** Mature buyers name organizational change management (OCM) as a
  workstream (it's phase-one in the methodology). Its presence signals adoption-readiness; its
  absence is a scoping gap to surface, not a disqualifier.
- **Industry specialization:** manufacturing, mining, asset-intensive, aerospace & defense, food &
  beverage, healthcare, life sciences, construction, government contracting, tribal & gaming are
  areas of named depth. A match strengthens fit and shapes which delivery team.
- **Disqualifiers / flags:** off-alliance platform with no partner path; "implementation" that's
  really a license resale with no services; a go-live date physically impossible for the scope.

## ICP signals specific to implementation
General ICP (size, US-based, vertical) lives in `config/icp.py`. Strong implementation fit tends to
look like: enterprise or upper-mid-market; a funded, multi-module, full-cycle program on an alliance
platform; a replacement of a fragmented legacy landscape; an exec-sponsored transformation with a
defined go-live — ideally where platform isn't yet locked, so the firm influences selection.

## Route to & package to compile
**Target team:** delivery / proposal team.
Compile into `team_package`:
- `platform`: named platform + whether it's in the alliance set
- `modules`: functional scope (finance, procurement, SCM, HCM, ...)
- `build_type`: greenfield | replacement | re-implementation
- `selection_stage`: platform selected? selection still in play?
- `forcing_function`: catalyst (aging platform / acquisition / growth) + RFP / funding / sponsor /
  go-live date, or what's missing
- `ocm_scoped`: whether organizational change management is in scope
- `industry`: vertical + whether it's an area of named depth
- `alliance_flags`: off-alliance or partnering concerns
- `open_questions`: what's missing to scope

## Readout template
Lead with the verdict in one sentence a partner can act on in ten seconds (build type, platform,
funded/sponsored/dated or not), then deal shape (phasing across the four methodology phases, size
band, term), then the compiled package.
