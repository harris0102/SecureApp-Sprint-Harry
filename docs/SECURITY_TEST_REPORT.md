# Security Testing Report

## 1. SAST — Bandit
Gate command (CI): `bandit -r app.py -ll`
- Pre-fix: `shell=True` in the ping path raised **B602 (OS command injection, HIGH)** and
  failed the pipeline — see the red GitHub Actions run (SS-RED).
- Hardened: the injectable path is confined to VULN_MODE and annotated `# nosec B602`
  with justification; `bandit -r app.py -ll` reports no medium/high issues, so the gate
  passes (SS-20). JSON report: evidence/bandit_report.json.
- Residual LOW findings (full scan, retained with justification) (SS-19):

| Test | Severity | Justification |
|------|----------|---------------|
| B404 subprocess import | Low | Required for ping; mitigated by shell=False + allow-list |
| B105 hardcoded password x2 | Low | Mock lab users only; no real credentials |
| B603 subprocess without shell=True | Low | Intended — this is the fix (no shell) |
| B607 partial executable path | Low | 'ping' resolved via PATH in the lab host; acceptable |

## 2. DAST — OWASP ZAP baseline
Tool: zap-baseline.py against the running app (unauthenticated).
- Before (VULN_MODE): evidence/dast/zap_before.html (SS-17)
- After (secure):      evidence/dast/zap_after.html  (SS-18)
- Key before/after delta: the **Anti-clickjacking Header** check moves to PASS in the secure
  build (X-Frame-Options: DENY + CSP frame-ancestors), confirming the clickjacking fix at runtime.
- Residual ZAP warnings (accepted / out of scope):
  - Absence of Anti-CSRF Tokens: ZAP scans unauthenticated and never reaches the authenticated
    /transfer form; the synchronizer-token fix is verified by unit test instead.
  - Missing X-Content-Type-Options / Permissions-Policy / full CSP: informational hardening
    headers, future work beyond the mandatory scope.

## 3. Pipeline quality gate
Workflow .github/workflows/ci-cd.yml runs build-test, sast, dependency-audit on push and PR.
- Fail-on-critical demonstrated: pre-fix run failed on the B602 HIGH finding (SS-RED).
- Pass after remediation: hardened branch run is green (SS-21).

## 4. Unit-test verification (pytest)
Five tests prove the fixes behaviourally: IDOR → 403, command-injection rejected, CSRF → 403,
clickjacking header present, legitimate self-access allowed. Executed in the build-test job.
