---
name: audit-advisory-compliance-readiness-qualification
description: >
  Qualify a COMPLIANCE READINESS engagement — advisory, NON-ATTEST preparation for a compliance
  framework or certification: readiness assessments, gap analysis, remediation, policy/procedure
  development, and control maturation ahead of a formal audit, examination, or certification. Use
  when the scope describes preparing for HITRUST, SOC 2, ISO 27001, NIST, CMMC, SOX, or financial/
  government regulation (BSA/AML, OFAC, CFPB, etc.) — before the attest/certification event.
  Distinguish from financial-statement-audit and soc-reporting (the attest engagements themselves),
  strategy-advisory, and tech work.
---

# Audit Advisory — Compliance Readiness Qualification

Loaded when the classifier labels an opportunity `audit-advisory / compliance-readiness`.
Your job: confirm this is advisory preparation (NOT the attest engagement itself), qualify it against
the firm's framework capabilities and ICP, and compile the package the
**compliance / readiness advisory team** needs to scope a response.

## When this applies
Advisory, non-attest work that prepares an organization to pass a future audit, examination,
certification, or regulatory exam: readiness assessment against a framework, gap analysis,
remediation support, policy and procedure development, compliance-program build, and control
maturation. The defining fact: the output is a readier organization and a remediation road map —
NOT an opinion, report, or certification (those are the separate attest/certification events this
PREPARES for).

## The non-attest / independence logic (this is the qualifying key)
Readiness and remediation are delivered under NON-ATTEST standards, by the risk/advisory practice —
deliberately SEPARATE from the team that would later perform an attest examination or certification.
This separation is the point: because readiness is advisory, a team can help build and remediate
controls that the attest auditors are independence-barred from touching. So:
- Readiness/remediation for a framework where the firm is NOT the eventual attestor = clean fit.
- If the SAME firm is slated to perform the subsequent attest examination/certification, the readiness
  and the attest work must be done by separate independent teams — flag it; it's a scoping wall, not
  necessarily a disqualifier (e.g. Baker Tilly is a HITRUST External Assessor and runs validated
  assessments under non-attest standards, with a separate risk-advisory team for remediation).

## The boundary test
- **vs soc-reporting / financial-statement-audit:** is the ask to PREPARE for a report/certification
  (readiness) or to ISSUE one (attest)? "Get us ready for SOC 2 / HITRUST" = this skill. "Perform our
  SOC 2 examination / HITRUST validated assessment" = the attest engagement.
- **vs strategy-advisory:** readiness is framework-specific control preparation; strategy-advisory is
  broader governance/operational advisory.
- **vs risk-advisory (a service line your taxonomy folds elsewhere):** heavy cyber/controls advisory
  may belong to a risk line; readiness-FOR-a-certification or regulatory exam is the audit-advisory
  readiness lane. (Note: at the real firm, compliance work genuinely straddles audit-advisory and
  risk-advisory — this taxonomy simplifies it here.)

## Qualification rubric
- **Framework clarity:** which framework(s)? Two broad families: (1) cyber/data certifications —
  HITRUST (e1/i1/r2), SOC 2 readiness, ISO 27001, NIST, CMMC, PCI DSS, NYDFS 23 NYCRR 500; and
  (2) financial / government / industry regulation — SOX 404, BSA/AML, OFAC sanctions, CFPB, FCPA,
  GLBA, HIPAA, GDPR, FERPA, FISMA. Most organizations face five or more — overlapping frameworks
  raise value and complexity (shared evidence reduces audit fatigue).
- **Readiness vs attest confirmation:** is this preparation, or the exam itself? If the buyer wants
  the certification ISSUED, re-check the route — it may be `soc-reporting` or a certification engagement.
- **Forcing function:** is there a customer/contractual mandate, a regulatory deadline, a certification
  the business needs to win/keep deals? Named driver + deadline = real and urgent.
- **Scope of help:** readiness assessment only | gap analysis | remediation | policy/procedure
  authoring | testing & monitoring | benchmarking | full compliance-program development. Broader = larger.
- **Timeline realism:** certification journeys run ~6-12 months end to end (scoping → readiness →
  remediation → validation); implemented-control periods can't be compressed (e.g. HITRUST's 90-day
  minimum). An "ASAP certification" with no runway is an expectations-management flag.
- **Independence flag:** is the firm also the intended attestor? If so, separate-team scoping required.
- **Disqualifiers:** an attest/certification issuance mislabeled as "readiness"; a framework the firm
  doesn't assess against with no partner path.

## ICP signals specific to compliance readiness
General ICP (size, US-based, vertical) lives in `config/icp.py`. Strong readiness fit tends to look
like: a regulated or vendor-scrutinized organization (healthcare/PHI, financial services, defense,
higher-ed/research, government contractors, SaaS handling customer data) facing a customer or
regulatory mandate for a named certification or regulatory exam, with a real deadline and an honest
gap between current and required control maturity.

## Route to & package to compile
**Target team:** compliance / readiness advisory team.
Compile into `team_package`:
- `framework`: cyber/data (HITRUST e1/i1/r2 | SOC 2 readiness | ISO 27001 | NIST | CMMC | PCI | NYDFS)
  | financial/gov (SOX | BSA/AML | OFAC | CFPB | FCPA | GLBA | HIPAA | GDPR | FERPA | FISMA) | other
- `readiness_scope`: assessment | gap analysis | remediation | policy/procedure | testing & monitoring
  | benchmarking | program development
- `forcing_function`: customer/contract | regulatory deadline | certification to win/keep business
- `attest_relationship`: is the firm also the intended attestor? (independence/separate-team flag)
- `timeline`: deadline + whether the certification runway is achievable
- `multi_framework`: overlapping frameworks that could share evidence (reduce audit fatigue)
- `open_questions`: what's missing to scope

## Readout template
Lead with the verdict in one sentence a partner can act on in ten seconds (which framework, readiness
vs attest, real forcing function), then deal shape (advisory engagement, often a precursor to a larger
certification journey), then the compiled package.