# Security Implementation & Remediation Report

This document outlines the vulnerability classes analyzed, their vulnerable code patterns, proof-of-concept exploit evidence, secure code fixes, and verification steps in compliance with CYC386 requirements.

---

## 1. Buffer Overflow (CWE-119 / CWE-120)
* **Vulnerable Component:** Native C helper (`app/c_extension/bof_helper.c`) using unsafe `strcpy`.
* **Exploit Evidence:** Passing 100 'A' characters triggers `*** stack smashing detected ***` and process termination when compiled with stack protection flags.
* **Remedior / Fix:** Replaced `strcpy` with `snprintf(buffer, sizeof(buffer), "%s", input)` and enabled compiler defenses (`-fstack-protector-strong`, `-D_FORTIFY_SOURCE=2`).

## 2. Command Injection (CWE-78)
* **Vulnerable Component:** Network diagnostic ping route (`app/routes.py`) using `shell=True` with user input.
* **Exploit Evidence:** Appending `; whoami` to the target string executes arbitrary shell commands on the underlying Linux host.
* **Remedior / Fix:** Avoid shell interpretation entirely by passing argument arrays to `subprocess.run([...])` or sanitizing inputs against strict allow-lists.

## 3. IDOR (Insecure Direct Object Reference) (CWE-639)
* **Vulnerable Component:** User profile endpoint (`/profile?id=1`) performing direct database lookup without session authorization.
* **Exploit Evidence:** Modifying the `id` query parameter (`?id=2`) exposes confidential records of other users.
* **Remedior / Fix:** Implemented strict object-level authorization verifying that the logged-in user owns or has permissions to access the requested resource ID.

## 4. CSRF (Cross-Site Request Forgery) (CWE-352)
* **Vulnerable Component:** Fund transfer action (`/transfer_form`) lacking state validation tokens.
* **Exploit Evidence:** External malicious sites can forge automated POST requests executing unauthorized transactions on behalf of an authenticated session.
* **Remedior / Fix:** Implemented Synchronizer Token Pattern (cryptographic `csrf_token` checked on POST) combined with `SameSite=Strict` cookie policies.

## 5. Clickjacking (UI Redressing) (CWE-1021)
* **Vulnerable Component:** Web UI framing vulnerability where sensitive pages can be embedded into malicious external iframes.
* **Exploit Evidence:** Invisible transparent overlays trick users into clicking underlying UI components.
* **Remedior / Fix:** Configured `@app.after_request` to inject `X-Frame-Options: DENY` and Content Security Policy `frame-ancestors 'none'`.
