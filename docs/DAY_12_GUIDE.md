# Day 12 Local sign in and session protection

Completed October 2, 2026. Project folder: C:\Users\Dell\Desktop\Projects\SentinelLab.

## What we built and why

The browser now asks you to sign in before it shows saved login events, alerts, detection runs or investigation cases. Signing out removes the session on the server. New browser case actions use the signed-in account name; changing a form value cannot impersonate a different author.

Before today, the request token stopped unwanted cross-site writes, but anyone who could open the local page could read data and obtain that token. Authentication adds a separate check: the browser must have a valid session created after password verification. The existing request protections still apply.

Roman Urdu: Pehle page kholne se data nazar aa jata tha. Ab pehle local account se login karna hota hai. Login aap ko pehchanta hai; request token doosri website se aane wali unwanted request ko rokne mein madad karta hai.

This is a one-account, local learning prototype. It is not ready for public hosting. Browser sign-in does not encrypt SQLite or stop someone who already has access to the project files. Command-line tools rely on local filesystem access and do not ask for this browser password.

## Step 1 Open PowerShell

Press the Windows key, type PowerShell, and open it. You do not need an Administrator window. Enter:

```powershell
cd "C:\Users\Dell\Desktop\Projects\SentinelLab"
```

This changes the terminal's working folder. The next commands can now find this project's scripts and Python environment.

## Step 2 Create your private local account once

```powershell
.\.venv\bin\python.exe scripts/account.py --username usman
```

Choose a password containing 15 to 128 characters. A long phrase that you can remember is easier than trying to satisfy arbitrary punctuation rules. Enter the same password twice. Nothing appears while typing; that is intentional hidden entry. Do not paste the password into chat or include it in a command argument. Success says Local account created.

Roman Urdu: Password screen par nazar nahi aayega, lekin type ho raha hota hai. Dono dafa bilkul aik jaisa password likhein. Password kisi ko chat mein na bhejein.

The account is saved in secrets/analyst.json. This file is ignored by Git and must stay private. It holds your username, a salt and a password hash, not the original password. The setup command refuses to overwrite an existing file. There is no browser password-reset feature. If you later need a new account file, stop the server and use a different --file path deliberately, then restart with that --credentials path. Do not delete evidence to recover an account.

For this checkpoint, the owner created the usman account privately. No password is recorded in this guide or in GitHub.

## Step 3 Start the Day 12 server

The prepared Day 12 workspace is http://127.0.0.1:8773/. It uses a separate data/runtime/day12_demo.db created from the Day 11 demonstration. The original Day 11 database is preserved. At preparation time it contained 16 synthetic events, one import, three alerts, one detection run, one investigation case and five actions. Later practice changes those counts.

If the server is not running, enter:

```powershell
.\.venv\bin\python.exe scripts/serve.py --database data/runtime/day12_demo.db --port 8773 --credentials secrets/analyst.json
```

Keep the terminal open. Ctrl+C stops a foreground server. If the port is busy, try opening the existing workspace before starting another process. Missing or malformed credentials prevent startup; the program does not silently run without sign-in.

On a fresh checkout, runtime databases and credentials are absent. Create your own account, start the server, sign in, upload data/samples/day07_all_rules.jsonl and explicitly run detection/save. No private account file or generated database is downloaded from GitHub.

## Step 4 Sign in and investigate

Open the workspace. Enter your username and password, then choose Sign in. The server checks the password and creates a temporary session. You should see Signed in as usman and the existing workspace. A wrong username or password gives the same generic error, so the page does not identify which half was correct.

Use Saved alerts, open R3 and choose Investigate this alert. Its existing case opens without duplicating it. Author fields are filled automatically and are read-only. New notes and decisions submitted from this browser are assigned to the session account by the Python server, even if someone modifies a browser field manually.

The older case history still contains its original labels. Those labels were entered before authentication, and the CLI can still supply its own labels. The stored schema does not mark their origin. Therefore, do not claim that every historical action has authenticated identity or that a username proves a person's real-world identity.

## Step 5 Sign out

Save any work you want to retain, then choose Sign out. The server removes that session and clears the cookie. A page open in another tab may still display data it already loaded, but new API requests using the revoked session fail. Logging out cannot erase information already shown on a screen.

If you try to save from another tab after logout, a sign-in message appears and the draft text stays in that page. Open the sign-in link in a new tab, sign in, copy any unsaved draft you need, then reload the original tab to obtain a fresh request token. A full reload discards page-only drafts. Always review case history before retrying after a lost response.

## Step 6 Understand the new concepts

Authentication means checking that the supplied password matches this local account. Authorization means checking whether a request is allowed to access a resource. Our one-account prototype gives its signed-in account access to the whole local workspace. It does not yet have administrator/read-only roles or separate access per case.

A password hash is a one-way derived value used for comparison. A salt is random data used alongside a password so that two equal passwords do not produce the same stored value. We use Python's established scrypt function with fixed settings: N 131072, r 8, p 1, a 16-byte random salt and a 64-byte result. Hashing deliberately costs memory and processing time, making offline guessing more expensive. It is not a guarantee against weak passwords or a stolen computer.

A session is the server's temporary memory of a successful login. The browser receives a random 256-bit identifier in a cookie, while the server keeps the account and expiry information in memory. The cookie does not contain the password. Signing in again rotates the identifier and invalidates the presented previous session. Restarting the server loses all sessions and requires another sign-in.

HttpOnly means browser JavaScript cannot directly read the session cookie. SameSite Strict restricts when the browser sends it from another site's context. The cookie is host-only with Path / and a name containing the server's port. Cookies are not isolated by port: the naming helps avoid accidental demo collisions, but does not protect against a malicious local service. This HTTP loopback demo does not use the Secure cookie flag; a hosted version needs HTTPS and deployment changes.

CSRF is an attempt to make your browser perform an unwanted action from another website. Each signed-in session has a separate random request token, and writes require the exact local Origin and Host. This is why knowing the address or the login-page token is insufficient to save changes as a signed-in user.

Roman Urdu: Session login ke baad server ki temporary yaad hoti hai. Cookie us session ki pehchan hai. Logout ya expiry ke baad purani pehchan se naya data access nahi hota.

## Step 7 Understand expiry and login limits

A session expires after 15 minutes without a request, or after eight hours regardless of activity. The server checks these limits using a monotonic clock, which measures elapsed time. Typing into a form alone does not contact the server and does not extend the session.

The app allows up to ten live sessions. It admits at most ten password-verification attempts in a rolling minute and temporarily blocks attempts after five failures in that window. Only one password hash is checked at a time; simultaneous attempts receive a retry message. Wait one minute rather than repeatedly clicking. These are bounded local protections, not a complete internet-scale denial-of-service defense. Restart resets these in-memory limits.

## What each new or changed file does

| File | Purpose |
| --- | --- |
| scripts/account.py | Gets a password privately twice, validates it and creates a new account file without overwriting one. |
| src/sentinellab/web/auth.py | Uses scrypt to check passwords; controls login limits, session creation, expiry and revocation. |
| src/sentinellab/web/server.py | Requires account configuration, gates workspace/data requests, handles login/logout, verifies session request tokens and supplies the real session author to case services. |
| src/sentinellab/web/case_api.py | Accepts a server-supplied author override for authenticated browser case actions. |
| src/sentinellab/web/templates/login.html | Contains the sign-in fields, messages and first-time help. |
| src/sentinellab/web/static/auth.js | Sends login/logout requests and fills read-only author fields. |
| src/sentinellab/web/templates/index.html | Shows the signed-in account, sign-out button, expiry recovery and historical-author explanation. |
| src/sentinellab/web/static/app.js | Recognizes a 401 response and displays the sign-in recovery link while keeping the page open. |
| src/sentinellab/web/static/style.css | Styles the login panel and session controls for desktop and narrow displays. |
| tests/integration/test_auth.py | Exercises real HTTP requests and credential/session invariants. |
| tests/integration/test_web.py and test_cases.py | Explicitly isolate the older non-authentication fixtures; production startup has no unauthenticated command-line option. |
| docs/AUTHENTICATION.md | Records the exact access contract, stack decision, limits and references. |
| docs/SentinelLab_Project_Handbook.docx | The cumulative Word explanation through Day 12, including previously missing Days 10 and 11. |
| docs/SENTINELLAB_HANDBOOK.md | The readable text companion to the cumulative handbook. |
| AGENTS.md | Now requires a Word and Markdown handbook update at every future checkpoint. |

The flow is: login form -> bounded JSON request -> request checks -> password verification -> new session cookie -> protected workspace. A case write adds the session check and per-session request token before calling the existing case service. Original evidence and detection rules are unchanged.

## What we tested

The full suite passes 168 tests: the previous 157 plus eleven authentication tests. New coverage includes anonymous read/write denial, wrong credentials, rate limits, malformed login bodies, cookie flags, session rotation/logout, idle/absolute expiry, duplicate cookies, bounded sessions and hashing, salted storage, fail-closed startup and spoofed-author rejection. Existing ingestion, detection, storage and investigation tests still pass.

Browser checks used a separate synthetic QA account and database. We checked wrong-password feedback, successful sign-in, read-only account fields, case creation/note author, logout, another tab's rejected save with retained draft, and desktop/390-pixel login layout. No console errors were observed in the checked login flow. The private user account is separate from QA credentials.

## Common problems and their meaning

- Account file already exists: setup preserved it. Sign in with that account rather than repeatedly creating it.
- No characters appear when entering a terminal password: normal hidden entry.
- Username or password is incorrect: check both values; the app deliberately gives one message.
- Too many attempts or busy: wait a minute and retry once.
- Cannot start: confirm the credential path, database access and whether the selected port is already in use.
- Session ended: sign in again and obtain a new page token. Preserve unsaved drafts before a full reload.
- An older demo still opens without login: it is an older running process. Use the new Day 12 address; old processes do not automatically reload Python code.

## What remains and how to explain this in an interview

A fair description is: I built a local security monitoring prototype with deterministic rules, retained original evidence, investigation history and a single-account browser login using scrypt and expiring server-side sessions. I tested access checks and recovery behavior. Do not call it a production SIEM, tamper-proof forensic system, multi-user platform or proven attack detector.

Day 13 is proposed to add faithful investigation report exports: include source alert identity, evidence references, notes, conclusions and limitations without changing the originals. Broader visual improvements, detection evaluation, clean-setup rehearsal, demo recording and final portfolio/CV material remain planned. Target completion is October 17, 2026.

From now on, every checkpoint must update this Word handbook and its Markdown companion with completed work, easy explanations, file responsibilities, usage steps, tests, limits and next steps. Earlier chapters remain historical and the newest chapter explains current behavior.

## Sources for the access design

OWASP Password Storage Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

OWASP Session Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html

## One small learning question

If signing out removes your session, does it delete your saved case notes or original login records? Explain your answer in this chat, in English or Roman Urdu.
