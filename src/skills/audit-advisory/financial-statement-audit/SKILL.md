---
name: financial-statement-audit-qualification
description: >
  Qualify a financial statement audit opportunity (independent attest engagement
  resulting in an opinion on GAAP/GASB financial statements). Use when the scope
  describes an external audit, attestation, or assurance over financial statements —
  including single audits of federal awards, employee benefit plan audits, and public
  company (PCAOB) audits.
---

# Financial Statement Audit Qualification

Loaded when the classifier labels an opportunity `audit-advisory / financial-statement-audit`.
Your job: qualify the engagement against the firm's ICP and audit capability, read the deal
shape, and compile the package the **assurance / audit engagement team** needs to scope a response.

## When this applies
An independent attest engagement producing an opinion on financial statements: recurring annual
audits, first-year audits, single audits of federal award recipients (Uniform Guidance), employee
benefit plan (EBP) audits, and public company (PCAOB) audits. Distinguish from `soc-reporting`
(controls attestation, not financial statements), `compliance-readiness` (pre-audit advisory, no
opinion issued), and `strategy-advisory` (consultative, non-attest).

## Capability grounding (what the firm actually delivers)
The firm's financial statement audit practice covers, and qualifies strongly for:
- Standards depth: ASC 606 (revenue recognition), ASC 842 / GASB 87 (leases) — GASB signals
  government / public-sector audit capability, a real strength.
- Single audits & federal awards compliance audits (Uniform Guidance) — federal-funding recipients fit.
- Employee benefit plan (EBP) audits — a distinct, recognized specialty.
- Public company audits (PCAOB) and international audit coordination.
- A risk-based, data-analytics-driven approach (Tableau, TeamMate, CaseWare; RPA for efficiency).

## Qualification rubric
Score the deal on these:
- Attest vs. advisory: does the scope actually call for an opinion / attestation? If it's pre-audit
  cleanup or advice with no opinion issued, it is NOT this engagement — flag for re-route.
- Standards & entity fit: GAAP / GASB / PCAOB framework named or implied, and it maps to the firm's
  depth above (strong: GASB government entity, Single Audit recipient, EBP, ASC 606/842 complexity).
- Independence: any existing non-attest relationship (bookkeeping, internal audit, advisory) that
  could impair independence is a disqualifier or scoping constraint — surface it explicitly.
- Recurring vs. one-time: a recurring annual audit relationship is higher value than a single year.
- Disqualifiers: opinion required on a framework the firm doesn't attest to; independence conflict
  that can't be managed; scope that's actually advisory (belongs in another engagement type).

## ICP signals specific to financial statement audit
General ICP (size, US-based, target vertical) lives in `config/icp.py`. On top of that, strong
financial-statement-audit fit tends to look like: a government / higher-ed / not-for-profit entity
with GASB or Single Audit requirements; a federal-award recipient triggering Uniform Guidance; a
plan sponsor needing an EBP audit; a pre-IPO or public company needing PCAOB-standard audit; a
private company with a financing or covenant-driven audit requirement.

## Deal-shape heuristics
Read and report: recurring annual engagement vs. one-time; likely fee basis (fixed annual fee);
first-year incremental effort (opening balances, prior-auditor coordination); busy-season timing
constraints; multi-entity or consolidated scope.

## Route to & package to compile
**Target team:** assurance / audit engagement team.
Compile into `team_package`:
- `audit_type`: recurring | first-year | single-audit | EBP | public-company
- `framework`: GAAP | GASB | PCAOB | other
- `independence_flags`: any existing relationships that could impair independence
- `key_dates`: fiscal year-end, report deadline, regulatory filing dates
- `entity_profile`: entity type, federal-award exposure, consolidation/multi-entity scope
- `open_questions`: what's missing to scope the engagement

## Readout template
Lead with the verdict in one sentence a partner can act on in ten seconds, then deal shape,
then the compiled package below the fold.