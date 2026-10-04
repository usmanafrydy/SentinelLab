# Set up and run SentinelLab

Current instructions for v0.1.0 through Day 20, 4 October 2026. See HANDOVER.md for the short existing-laptop guide. Optional practice is not a setup or release requirement. This is a local learning prototype. It imports files when asked; it does not automatically monitor your laptop or network. Run the server on its built-in loopback address only.

## Continue your existing laptop project

Your project is C:\Users\Dell\Desktop\Projects\SentinelLab. Keep your existing private account and day14_demo.db. Do not repeat fresh installation or recreate the account. If the server is already running, open http://127.0.0.1:8776/ and sign in. Otherwise use:

```powershell
cd "C:\Users\Dell\Desktop\Projects\SentinelLab"
& .\.venv\bin\python.exe scripts/serve.py --database data/runtime/day14_demo.db --port 8776 --credentials secrets/analyst.json
```

Keep that terminal open while using the app. Ctrl+C stops the server. Saved records survive; sessions do not. Earlier day databases are separate copies and do not synchronize. Browser navigation keeps drafts in memory but does not save them. Only explicit save actions store changes.

## Fresh installation in a new folder

These steps are for a new copy. Do not run git clone over the existing Desktop project. Use a writable folder, Python 3.12 with SQLite and hashlib.scrypt available, and Git if you choose cloning. No third-party application packages are needed. The rehearsal used Windows and MSYS2 UCRT Python 3.12.7; other operating systems and Python versions are not certified by that run.

### 1 Get the source

From your chosen parent folder:

```powershell
git clone https://github.com/usmanafrydy/SentinelLab.git SentinelLab-fresh
cd SentinelLab-fresh
git rev-parse HEAD
```

Alternatively, download the repository ZIP from GitHub, extract it, and open PowerShell inside the extracted folder containing scripts and src. A ZIP has no Git history. Record the commit you downloaded if reproducibility matters. GitHub source does not contain private accounts, runtime databases or virtual environments. The Day 16 automated source-download attempt was blocked by local TLS certificate errors. On Day 18, bundled workspace Python successfully downloaded the exact Day 17 commit ZIP with TLS verification enabled, and all 152 extracted blobs matched GitHub. A fresh environment passed 194 tests and the complete HTTP rehearsal. This verifies a working archive route, not git clone or a repair to the earlier runtime. See FINAL_ACCEPTANCE.md and the historical SETUP_REHEARSAL.md. Do not disable certificate checks to work around that error.

### 2 Create a fresh Python environment

```powershell
python --version
python -m venv --without-pip .venv
```

Check that the first command reports the intended Python 3.12 installation. If python is unavailable, use the full path to an installed Python 3.12 executable or configure that installation first. On a machine with a registered launcher, py -3.12 may work; it was not available on this laptop. A venv is a separate project environment. Recreate it when moving a project instead of copying somebody else's environment. Pip is unnecessary for this standard-library application.

### 3 Select its executable

```powershell
if (Test-Path '.venv/Scripts/python.exe') {
    $projectPython = '.venv/Scripts/python.exe'
} elseif (Test-Path '.venv/bin/python.exe') {
    $projectPython = '.venv/bin/python.exe'
} else {
    throw 'Create the project environment first.'
}
& $projectPython -c "import sys, sqlite3, hashlib; print(sys.version); print('Isolated:', sys.prefix != sys.base_prefix); print('scrypt:', hasattr(hashlib, 'scrypt'))"
```

Expect Isolated: True and scrypt: True. Normal Windows Python commonly uses Scripts; this laptop uses bin. In PowerShell the ampersand runs the executable stored in the variable. No environment activation or execution-policy change is needed. If you open a new terminal, select the executable again because the variable belongs to that terminal.

### 4 Verify the application before adding your own data

```powershell
& $projectPython scripts/run_tests.py
& $projectPython scripts/rehearse.py
& $projectPython scripts/evaluate.py
```

Check $LASTEXITCODE immediately after each command; 0 means that command completed successfully. The test runner currently contains 194 tests. Rehearsal should print status passed and seven checks. It uses a random temporary test account, synthetic events and temporary databases; it does not change your own account or investigations. Its worker is a separate process using the real HTTP server and stops cooperatively before cleanup.

Evaluation should show 12 scenarios and 12 expected-rule agreements, with TP, FP, TN and FN each 3. This is an authored synthetic benchmark, not real-world accuracy. Read DAY_15_GUIDE.md before interpreting the percentages. Passing the rehearsal does not test your keyboard entry, browser usability or every deployment condition.

### 5 Create your private account once

```powershell
& $projectPython scripts/account.py --username your_name
```

Choose your own username in place of your_name. Enter the same private 15-to-128-character password twice. Nothing appears while typing; press Enter after each entry. Do not put a password in a command, chat, screenshot or repository. The default account file is secrets/analyst.json. Keep it private. Existing files are never overwritten. If it already exists, use the existing account rather than deleting it. Account recovery requires deliberate local handling; it is not automatic.

The rehearsal exercises account creation through the application service. Hidden interactive entry was not reverified during Day 16 because terminal-input automation was blocked. On Day 18 the owner ran the command in PowerShell with a separate ignored test file and reported account creation. The assistant confirmed file existence without reading credentials; it did not observe keyboard visibility. This test account does not replace the existing everyday account.

### 6 Start the new empty workspace

```powershell
& $projectPython scripts/serve.py --database data/runtime/events.db --port 8765 --credentials secrets/analyst.json
```

Open http://127.0.0.1:8765/ in a browser and sign in. This fresh path begins empty. The server creates its database and parent directory; you do not need to make them manually. Keep the terminal running. A port already in use needs a different available port and matching browser URL; do not stop an unrelated application.

### 7 Walk through the sample

1. In Events, upload data/samples/day07_all_rules.jsonl. Expect 16 inserted events. Uploading again should insert zero and report 16 duplicates; the saved event count stays 16.
2. In Detection, run all rules and save. Expect three alerts, one each for R1, R2 and R3. Run again: the alert total stays three and a new run is recorded.
3. Open the R3 alert, inspect its failure and success evidence, and open an original record. An alert is a reason to investigate, not proof of hacking.
4. Create an investigation from the alert. Save a note describing what the records show. Record a decision and its reason. Use an appropriate disposition; do not claim confirmed compromise from these logs alone.
5. Download JSON and Markdown reports from the case. They contain saved case state, action history, rule evidence and original records. Unsaved drafts are excluded. Review reports before sharing because real imports and notes could contain private information.
6. Stop and restart the server with the same database and account. Sign in again. Saved work should remain. Logout should remove access until you sign in again.

## Troubleshooting

- Cannot find a script: open the folder containing scripts and src. Relative database/account paths are resolved from your current directory. Follow the startup command from the project folder.
- Python not found or wrong version: inspect python --version and select the actual installed executable. Do not assume the py launcher exists.
- No scrypt or SQLite: use a compatible Python build before creating accounts. The project does not replace missing standard-library capabilities with insecure alternatives.
- Account already exists: it was preserved. Continue with that account; do not recreate it during everyday startup.
- Server cannot start: check the chosen account file, writable database directory and port. Never print or share the credential file while troubleshooting.
- Browser cannot connect: check the terminal is still running and the browser port matches it. A restart invalidates sessions; sign in again.
- Rehearsal failure: read its safe reason and rerun after fixing the stated environment issue. Do not treat a failed run as complete. A forced process/OS failure can leave temporary files even though normal cleanup is checked.
- GitHub certificate error: resolve the machine/network trust setup or use an authorized connected download route. Do not turn off TLS verification. The Day 16 fallback is documented rather than disguised as a successful download.
- Windows connection-aborted error during a test: record it, rerun the affected test, then rerun the suite. A repeatable failure needs investigation; do not silently discard it.

Earlier daily guides and handbook chapters retain historical commands for learning. Use this page for current setup, and the existing-project section for the owner's current demonstration. Local Git metadata on the owner's original copy remains behind under existing Windows restrictions; the published GitHub source is the verified checkpoint. Do not reset that copy or change its access controls to hide the difference.
