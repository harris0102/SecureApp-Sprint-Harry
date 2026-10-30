# Security Implementation & Remediation

Each class is demonstrated in VULN_MODE and fixed in the default (secure) build.
Evidence screenshots in evidence/screenshots/.

## 1. Buffer Overflow (CWE-120)
- Component: native/bof_helper.c — vulnerable_process() uses strcpy() with no bounds check.
- Exploit: ./native/bof_asan vuln "<200 A's>" -> AddressSanitizer stack-buffer-overflow (SS-01);
  hardened build -> "*** stack smashing detected ***" (SS-02).
- Fix: secure_process() uses snprintf() bounded to sizeof(buffer); compiled with
  -fstack-protector-strong -D_FORTIFY_SOURCE=2 (ASLR + NX enabled by default).
- Verify: ./native/bof_hardened secure "<200 A's>" processes input safely, no crash (SS-03).

## 2. Command Injection (CWE-78)
- Component: /ping — VULN path calls subprocess with shell=True on user input.
- Exploit: target "127.0.0.1; whoami" executes whoami, returns "harry" (SS-05).
- Fix: allow-list regex ^[A-Za-z0-9.-]+$, then subprocess.run([...], shell=False).
- Verify: same payload -> "Rejected…" (SS-09). Unit test: test_command_injection_blocked.

## 3. IDOR (CWE-639)
- Component: /profile?id= — VULN path returns any record without ownership check.
- Exploit: logged in as alice, /profile?id=2 reveals Bob's confidential record (SS-04).
- Fix: require authentication; requested id must equal session user_id, else HTTP 403.
- Verify: /profile?id=2 as alice -> 403 (SS-08). Unit test: test_idor_other_profile_blocked.

## 4. CSRF (CWE-352)
- Component: /transfer — VULN path accepts a state-changing POST with no token.
- Exploit: csrf_poc.html auto-submits a forged POST -> "Transferred $9999 to attacker" (SS-06).
- Fix: per-session synchronizer token verified on POST; SameSite=Strict session cookie.
- Verify: same PoC -> 403 (SS-10). Unit test: test_csrf_rejected_without_token.

## 5. Clickjacking (CWE-1021)
- Component: pages framable (no anti-framing header in VULN mode).
- Exploit: /clickjacking embeds /transfer in an iframe that renders (SS-07).
- Fix: after_request sets X-Frame-Options: DENY and CSP frame-ancestors 'none'.
- Verify: iframe blocked; console shows "Refused to display … X-Frame-Options" (SS-11).
  Unit test: test_clickjacking_header_present.
