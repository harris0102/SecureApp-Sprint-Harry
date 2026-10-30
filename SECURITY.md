# Security Policy
Academic DevSecOps project. Vulnerabilities run only in VULN_MODE for education; default build is hardened.
## Reporting
Open a private security advisory or email the maintainer; no public issues for undisclosed vulns.
## Controls
Bandit SAST + pip-audit gate every PR (GitHub Actions); OWASP ZAP DAST in evidence/dast/; protected main via reviewed PRs.
