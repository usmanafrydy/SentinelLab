# Day 16 Making setup repeatable

Completed 4 October 2026. Work began on 3 October. The planned completion date remains 17 October, at least two days before 19 October.

## What we achieved

Today we checked whether the project can work without relying on your existing virtual environment, private account or demonstration database. We prepared a separate source folder, created a fresh Python environment, ran the tests and exercised the complete synthetic login-to-report workflow. The unchanged Day 15 source passed 193 tests. After adding today's reusable rehearsal command and regression test, the clean candidate passed 194 tests.

We also repaired the setup documentation. Earlier daily instructions had accumulated in one page, with several ports, database names and old test counts. Those commands were useful at their original checkpoints, but confusing for someone installing the project now. SETUP.md now has one section for continuing your own laptop project and a separate ordered path for a fresh copy.

The main application has no new detection rule, database schema or browser screen today. The value is that another person has a clearer way to install and check it. A portfolio project needs to be understandable and repeatable, as well as working on its owner's machine.

Roman Urdu: Sirf apne laptop par chalna kafi nahi. Doosra banda bhi instructions follow karke project chala sake. Aaj hum ne nayi environment mein check kiya aur setup ke confusing steps saaf kiye.

## A fresh environment in easy English

A Python interpreter is the program that runs Python code. A virtual environment, often called a venv, gives a project its own interpreter entry point and package area. This helps keep project dependencies separate from other work. It does not create another operating system, virtual machine or strong security boundary.

Your existing environment is .venv/bin/python.exe because this laptop uses MSYS2 UCRT Python. Other Windows Python installations commonly use .venv/Scripts/python.exe. A guide that assumes only one layout may fail even when Python is installed correctly. The new setup page checks both locations and assigns the working path to a PowerShell variable named projectPython.

The ampersand before that variable tells PowerShell to run the executable whose path the variable contains. This avoids needing an activation script or changing Windows execution policy. The variable exists only in that terminal; a new terminal needs the selection step again. The fresh environment was made without pip because the application currently needs only Python's standard library.

SQLite stores the project records. hashlib.scrypt supports the existing password hashing. We checked that both are available. The environment reported Python 3.12.7, SQLite 3.46.1, scrypt available and Isolated True. These are observations about this laptop. We did not certify every Python distribution or install Python on a new computer.

## How we obtained the source for the check

The published starting commit was 834a51c1bc170c1c1f6240f72d8d02837594387b. A commit identifies a particular Git history snapshot. Before changing anything, we compared all 137 published file hashes with the local source files. Every file matched.

We attempted to obtain a new archive from GitHub. The Python download failed because its TLS certificate chain could not be verified, and PowerShell's download also failed during the TLS connection. TLS is the protection used for HTTPS connections. We did not turn off certificate checking just to make the download succeed.

Instead, we copied only the source files that matched the published GitHub blob hashes into the separate rehearsal folder. A Git blob hash identifies the stored bytes of a file, including its Git object header. Matching every file establishes that the staged source equals that published snapshot. It does not turn a failed network download into a successful one. The record explicitly says the download and clone path remains unverified.

The clean folder is data/runtime/day16_clean inside the active project. It is ignored by Git and used only for the rehearsal. Your working project remains C:\Users\Dell\Desktop\Projects\SentinelLab. We did not copy your private account, saved cases, original investigation database or existing environment into the clean folder.

## What the new rehearsal command does

The command is scripts/rehearse.py. A rehearsal means a practice run that checks the important steps before presenting the system to someone else. It is also a broad smoke check: if a basic integration is broken, it should fail visibly. It complements the detailed unit and integration tests rather than replacing them.

First, it makes a temporary directory. Inside that directory it creates a new synthetic account and a new database path. The password is generated randomly and held in memory; it is not printed, passed as a command-line argument or saved in Git. Account creation uses the same application service as the existing setup command.

Second, it starts a child Python process. That worker uses the real LocalServer class, real authentication and a port assigned by the operating system on 127.0.0.1. A port is the local number used to reach a service. Choosing an unused port automatically avoids changing your usual demonstration port. Authentication stays enabled throughout the exercise.

Third, it connects over HTTP, which is the same request-and-response protocol used by the browser. It gets the sign-in token, signs in, receives the session cookie and reads the authenticated workspace token. Those tokens stay inside the helper. It checks that an anonymous request is rejected. The helper does not bypass the sign-in checks or write directly into database tables to pretend a workflow succeeded.

Fourth, it uploads the existing synthetic sample, explicitly saves detection, creates a case, saves a note and records a decision. Fifth, it downloads JSON and Markdown reports and checks their contents. Sixth, it stops the worker, starts a new process with the same temporary database and checks persistence. Finally, it logs out, checks access rejection, stops the worker and removes its temporary files.

The command returns JSON containing status, seven completed checks, Python version, environment isolation and limitations. An exit code of zero means the rehearsal passed. An exit code of one means it failed. Read the failure reason and fix the problem before relying on the result. This command does not start your everyday demonstration server permanently.

## The workflow and results step by step

The sample day07_all_rules.jsonl contains sixteen synthetic login events. The first upload inserted sixteen and rejected zero. The second upload inserted zero and identified sixteen duplicates. This confirms that repeated upload does not double the saved evidence. An import record can still be created to record the second attempt; import counts and event counts are different things.

Running all three rules saved three alerts, one for R1, one for R2 and one for R3. Running detection again left three alerts and recorded a second run. A run records the act of checking; an alert records a finding. Repeating an unchanged check should not invent new copies of the same finding.

We selected the R3 alert and created a synthetic case. The case received a note explaining that the alert needs context. It was closed with a suspicious disposition and an explicit reason. Its revision became three: creation, note and decision each advanced the saved history. This was an exercise, not confirmation that a real account was compromised.

The JSON report contained the case at revision three, all three actions and original event text matching the sample. Every action carried the signed-in rehearsal analyst name. The client supplied a different author label, but the server correctly used the session identity. The Markdown endpoint returned an attachment with the report heading. Reports include saved work, not browser drafts.

After restarting the worker, the case and three alerts still existed. The previous session was rejected and a new sign-in worked. This demonstrates the difference between persistence and session memory. SQLite data survives process restart. In-memory authentication sessions do not. Logout also caused the protected summary request to be rejected.

Roman Urdu: Server band hone se saved records delete nahi hote. Lekin login session khatam ho jata hai. Dobara server chalane par sign in karein; pehle se saved case phir milna chahiye.

## Why shutdown needed attention on Windows

The first helper experiment used ordinary process termination. Windows virtual environments can involve a launcher process and a child interpreter, and forced tree termination was unreliable in this restricted session. A rehearsal must not report success while silently leaving a test server running.

The final helper uses cooperative shutdown. The parent owns a private input pipe to the worker. Closing that pipe tells the worker that no more input will arrive. The worker then calls server.shutdown, joins its serving thread and closes the server before exiting. The parent waits for a clean exit before claiming cleanup. There is no public HTTP shutdown route and no taskkill command in the final helper.

Normal completion and Python exceptions go through cleanup. If shutdown times out, the helper reports failure. A forced operating-system failure, process termination or machine crash can still leave temporary files; this is not a promise that cleanup succeeds after every possible failure. The earlier trial terminal processes ended with the app/session restart. The final workers were observed to finish their cooperative exits.

## What we could not verify today

The interactive account command reached its first hidden-password prompt. However, automatic approval review blocked sending terminal input because sandbox_approval is disabled in this session. We did not ask you to reveal a password. The final rehearsal exercises account creation through the actual account service with a random test password, so hidden keyboard entry remains a separate manual check.

The source download encountered certificate errors. The source itself was verified against published hashes, but a fresh network download or clone was not completed. No certificate setting was weakened. A person following the new guide can use Git or a downloaded ZIP once their machine's trust/network setup permits it.

This is a fresh virtual environment on the same Windows laptop, not a fresh operating system. We did not run a new visual browser audit because today's application HTML, CSS and JavaScript were unchanged. Real HTTP requests tested the workflow, but they cannot prove button layout, keyboard focus or screen-reader usability. Earlier browser checks remain historical evidence.

We also keep the existing Word rendering limitation separate. The cumulative Word content is updated and checked for preservation and structure, but the bundled renderer requires a LibreOffice executable that has been unavailable. A test count is not proof that Word pages look right. The final status reports the renderer result explicitly.

## Every file changed today

scripts/rehearse.py is the new reusable workflow command. It contains the worker startup/shutdown, HTTP helpers, synthetic exercise, result checks and cleanup. tests/integration/test_rehearsal.py runs that command from another working directory, checks successful JSON output and confirms it did not create files in that calling directory. Running outside the repository checks that the helper locates its source and sample from its own file path.

tests/integration/test_auth.py received a focused correction after Windows error 10053 interrupted a header-rejection check. The header-only cases now send an empty body; malformed-body cases remain separate. This tests the expected rejection without racing an early connection close against a discarded upload. The security requirements and application code are unchanged. The corrected check passed twenty targeted runs, and the full suite result was checked separately.

The same transport error subsequently appeared in an anonymous-request check. tests/integration/test_web.py now buffers each complete finite test request before sending it, instead of sending headers and body separately. This shared test client does not retry writes or change expected response statuses. After this adjustment, the complete clean-environment suite passed all 194 tests. This transport correction is limited to test infrastructure.

docs/SETUP.md replaces the accumulated historical startup sequence with current instructions for both existing and fresh users. docs/SETUP_REHEARSAL.md is the technical evidence record: source commit, environment, checks, limitations and fixes. docs/DAY_16_GUIDE.md is this plain-English lesson.

README.md reports the current checkpoint and links the setup/rehearsal material. docs/ACCEPTANCE_CRITERIA.md adds today's evidence without claiming that the whole release is finished. docs/PROGRESS.md records what happened. docs/NEXT_SESSION.md gives the next checkpoint and the current demonstration details.

docs/SentinelLab_Project_Handbook.docx and docs/SENTINELLAB_HANDBOOK.md receive chapter 33 and a refreshed current completion map. Earlier chapters remain as historical explanations. Temporary source folders, test databases, account files and authoring helpers are not published. No detection-engine source, authentication contract, existing case schema or event format changed today.

## Your commands and your part

For your existing laptop project, open PowerShell and run:

```powershell
cd "C:\Users\Dell\Desktop\Projects\SentinelLab"
.\.venv\bin\python.exe scripts/rehearse.py
$LASTEXITCODE
```

Expect status passed, seven checks and exit code zero. You do not need to create another private account or import records into your current database for this command. It takes care of its own synthetic data and temporary account. Your task is to read each check and understand why it matters, rather than just looking for the word passed.

To run the full test suite, use .\.venv\bin\python.exe scripts/run_tests.py. For a fresh installation, follow docs/SETUP.md in order. Do not apply its clone or account-creation steps over your existing project. If the command cannot find Python, check the bin versus Scripts location as the guide explains.

For your ordinary interface, continue using day14_demo.db, port 8776 and your existing account. Start it only when stopped using the existing-project section of SETUP.md. Keep the terminal open while using it. The rehearsal command starts and closes temporary servers; it does not leave the everyday interface running.

When presenting the project, you can say: I verified the source files against a published commit, created a clean Python environment and built an isolated authenticated workflow rehearsal that checks deduplication, case history, reports and restart persistence. Also state the boundaries: the network download and interactive hidden entry were not reverified, and this was one Windows environment.

## What comes next

Day 17 is planned for the portfolio demonstration and release preparation: create a clear synthetic story, decide the presentation sequence, gather representative screenshots, draft a truthful case study and CV bullets, and map completed work against final acceptance. Any remaining release blockers should be recorded and handled before claiming the project complete. The target remains 17 October.

Your one practice question is: after restarting SentinelLab with the same database, should your saved case disappear, or should only your login session need renewal? Explain why in this chat. A short answer is enough.
