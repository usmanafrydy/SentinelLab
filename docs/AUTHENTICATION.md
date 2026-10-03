# Day 12 local access contract

## Scope and stack decision

Keep the existing loopback-only standard-library server for this bounded local teaching checkpoint. Use Python hashlib.scrypt, secrets, compare_digest and server-side sessions rather than inventing password cryptography or signing a custom token. This is not a public deployment server. FastAPI/Flask migration, HTTPS, multi-user roles and account recovery are separate work; a framework alone would not supply those controls. CLI startup requires a credential file and fails closed when absent/invalid. An explicit constructor-only testing_no_auth switch supports older isolated regression fixtures; it is not a command-line option.

One account is provisioned locally through scripts/account.py using hidden password entry and confirmation. Username is 3..40 ASCII letters/digits/underscore/dot/hyphen; password is 15..128 characters, UTF-8 up to 512 bytes, with no composition requirement. No plaintext password is stored. Credential JSON contains a version, username, random 16-byte salt and 64-byte scrypt hash. Fixed scrypt parameters N=131072, r=8, p=1; memory allowance 256 MiB. Credential files must remain under ignored secrets or data/runtime directories. Setup refuses overwrite; changing accounts requires stopping the server and explicitly creating a new file. No browser registration/reset is provided.

## Session contract

All data APIs and workspace HTML require a signed-in session. Only login HTML and explicitly public static assets are accessible without a session. Login requires exact Host/Origin and the per-process login request token; max 4096 bytes of strict JSON with username/password strings. Generic invalid-credential response; no account enumeration message. Five failed attempts within 60 seconds block further attempts until the window expires. A global attempt limiter and one verification lock bound concurrent password hashing. No unbounded queue of hashing work: busy verification returns a retry response. This limiter is local/in-memory and resets with the server.

A successful login creates a fresh 256-bit opaque cookie and per-session CSRF token, invalidating any presented existing session. Store sessions only in memory, maximum 10. Idle expiry 15 minutes, absolute expiry 8 hours, checked on the server using monotonic time. Logout is protected POST and removes server state; restart invalidates all sessions. Cookie is HttpOnly, SameSite=Strict, Path=/, host-only. Its name includes the port to avoid accidental collisions with other SentinelLab demos. It is not Secure because this exact loopback demo uses HTTP; cookies are not port-isolated and this is not protection from malicious local software or another untrusted service on the same host. Never expose/tunnel this server.

Authenticated writes still require exact Origin and a matching per-session request token; no tokens in URLs. Anonymous APIs return 401. Expired browser requests show a sign-in link without automatically discarding drafts. Password and token values are not logged. No session or credential is committed to GitHub.

## Author attribution and historical records

Browser case author values are supplied by the server from the session account, overriding the posted author label. Existing historical labels remain unchanged and CLI author labels remain self-declared. The record schema does not distinguish their provenance, so the UI must not claim all history has authenticated identity. Application history remains editable by anyone with direct database access. CLI tools bypass browser sign-in and rely on filesystem access.

## Verification and references

Test failed-closed startup, password verification and format rejection, unauthorized reads/writes, login CSRF and size/type checks, cookie attributes, session rotation, logout, idle/absolute expiry, rate limiting, credential privacy and author-spoof prevention. Preserve all earlier behavior through the isolated legacy fixtures. Exercise login, protected workspace, logout and anonymous rejection through the browser using synthetic test credentials. No production security claim.

References reviewed October 2, 2026:
- https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
