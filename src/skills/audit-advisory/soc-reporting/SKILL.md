---
name: soc-reporting-qualification
description: >
  Qualify a SOC (System and Organization Controls) reporting opportunity — an independent
  attestation over a service organization's controls. Use when the scope describes SOC 1,
  SOC 2, SOC 3, SOC for Cybersecurity, or SOC for Supply Chain, a SOC readiness assessment,
  or controls assurance demanded by the prospect's own customers / vendor-risk requirements.
---

# SOC Reporting Qualification

Loaded when the classifier labels an opportunity `audit-advisory / soc-reporting`.
Your job: identify which SOC report and type the deal needs, qualify it against the firm's ICP
and SOC capability, surface the independence constraint, and compile the package the
**SOC / attestation practice** needs to scope a response.

## When this applies
An independent examination of a service organization's controls, resulting in a SOC report.
Distinguish from `financial-statement-audit` (opinion on financial statements, not controls),
`compliance-readiness` (advisory prep with no report issued — though SOC *readiness* is a valid
pre-cursor engagement this practice offers), and `strategy-advisory` (non-attest consulting).

## Four-step scoping check (the firm's published method)
A well-scoped SOC opportunity has worked through: (1) what the end-user entities need in the
report's scope, (2) what's in the system description, (3) whether a readiness assessment has
started, (4) whether known control/documentation deficiencies are being remediated before the
examination period opens. Score how many of these the prospect has already addressed — the more
unresolved, the more this is a readiness engagement before an examination, not an examination yet.

## Qualification rubric
Score the deal on these:
- **Forcing function (the realness test):** is there external demand — a customer contract, an RFP
  requirement, a vendor-risk mandate — driving this? SOC need is customer-demand-driven; a deal with
  a named forcing function and deadline is real and urgent. No forcing function = exploratory, lower priority.
- **Report + type clarity:** can you tell which SOC report and Type 1/2 from the scope? If ambiguous,
  that's a readiness-assessment conversation, not a defect — note it.
- **First-time vs recurring:** first SOC examinations run ~9-14 months readiness-through-report; recurring
  annual SOC engagements are higher-value relationships. Identify which.
- **Independence:** SOC is attestation. If the firm built or operates the controls (advisory/MSP
  relationship), independence may be impaired — surface it. This is a disqualifier or a scoping wall.
- **Subservice complexity:** heavy reliance on subservice organizations (cloud hosting, downstream
  vendors) widens scope (CSOCs/CUECs) — flag it.
- **Disqualifiers:** independence conflict that can't be managed; an "ASAP" SOC 2 Type 2 with no runway
  (operating-effectiveness periods can't be compressed below the observation window — manage expectations).

## ICP signals specific to SOC
General ICP (size, US-based, vertical) lives in `config/icp.py`. Strong SOC fit tends to look like:
a SaaS / technology / data-processing service organization whose enterprise customers demand SOC 2;
a financial-services-adjacent processor (payroll, claims) needing SOC 1; a healthcare-data handler
needing SOC 2+ (HIPAA/HITRUST); a vendor that just lost or is at risk of losing a deal for lack of a report.

## Route to & package to compile
**Target team:** SOC / attestation practice.
Compile into `team_package`:
- `soc_report`: SOC 1 | SOC 2 | SOC 3 | SOC-for-Cybersecurity | SOC-for-Supply-Chain | SOC 2+
- `soc_type`: Type 1 | Type 2 | undetermined
- `forcing_function`: the customer/contract/regulatory driver, or "none stated"
- `readiness_needed`: whether a readiness assessment precedes the examination
- `independence_flags`: any advisory/operate relationship that could impair attestation
- `additional_frameworks`: HIPAA, HITRUST, etc., if SOC 2+
- `timeline`: deadline + whether it's achievable given the observation-period constraint
- `open_questions`: what's missing to scope

## Readout template
Lead with the verdict in one sentence a partner can act on in ten seconds (which report, real or
exploratory, the forcing function), then deal shape, then the compiled package.