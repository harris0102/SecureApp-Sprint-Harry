# Security Testing & Automated Quality Gate Report

## 1. Static Application Security Testing (SAST)
* **Tool Used:** Bandit (Integrated into GitHub Actions CI/CD pipeline).
* **Configuration:** Scanned recursive source directory (`app/` and `app.py`) with high/critical severity threshold filtering (`-ll --severity-level high`).
* **Findings:** Identified insecure shell invocation patterns (`shell=True` in subprocess calls) and memory-unsafe C constructs during initial scans, satisfying the lab requirement for the pipeline to demonstrably fail on critical severity findings.

## 2. Dynamic Application Security Testing (DAST) & Verification
* **Buffer Overflow:** Verified that native helper binary compiled with `-fstack-protector-strong` successfully detects stack smashing and terminates execution when input bounds are exceeded.
* **Command Injection:** Validated that shell metacharacters (e.g., `; whoami`) successfully executed in the vulnerable route and were subsequently remediated via argument array isolation.
* **IDOR:** Verified unauthorized cross-user profile access when object-level permission checks were absent, and confirmed prevention upon implementing session ownership validation.
* **CSRF & Clickjacking:** Verified synchronizer token validation on state-changing forms and confirmed `X-Frame-Options: DENY` successfully blocks UI redressing framing attempts.

## 3. Pipeline Quality Gate Status
* **GitHub Actions Workflow:** Configured in `.github/workflows/ci-cd.yml`.
* **Gate Behavior:** The pipeline executes build verification and Bandit security scans on every push and pull request, exiting with a non-zero status code (failing the build) upon encountering high-severity security findings.
