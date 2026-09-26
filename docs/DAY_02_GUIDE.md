# Day 2 - Reading and checking login records

## What we are making

We made a small Python program that reads a file and checks each login record. It does not detect hacking yet.

Roman Urdu: Aaj hum ne code banaya jo file parhta hai aur batata hai ke record ka format theek hai ya nahi.

## Step 1: Python environment

Python runs our code. The .venv folder keeps this project's environment separate. Today we use tools already included with Python, so no extra packages were installed.

Roman Urdu: Python code chalata hai. .venv project ka apna environment hai.

Check: the environment reports Isolated: True. SETUP.md contains the exact commands and troubleshooting steps.

## Step 2: Read one line at a time

The input is JSON Lines. Each line contains one JSON object. A JSON object stores named values, such as username and outcome. json.loads turns the JSON text into Python values. The official reference is https://docs.python.org/3.12/library/json.html

Python example:

```python
record = {"username": "demo_user", "outcome": "failure"}
print(record["outcome"])
```

This prints failure. A Python dictionary keeps values under names called keys.

Roman Urdu: Dictionary mein har value ka naam hota hai. outcome naam se hamein login ka result milta hai.

## Step 3: Validate the record

Validation means checking data against our agreed format. The reader checks required fields, text types, allowed values, IP addresses, and timestamps.

```python
if value["outcome"] not in {"success", "failure"}:
    raise ValidationError("outcome must be success or failure")
```

Read it as: if the outcome is neither success nor failure, explain the problem. A function is a named block of work; validate_event performs these checks. An exception reports a problem to the caller, which records the reason and continues with the next line.

Roman Urdu: Agar outcome success ya failure nahi hai, to record reject hoga aur wajah batayi jayegi. Agli line phir bhi check hogi.

## Step 4: Normalize values

Normalization means storing equivalent values in one consistent form. 15:00 at +05:00 and 10:00 UTC are the same instant. Our reader turns both into UTC. It also standardizes IP address text and keeps the original accepted record separately in memory.

Roman Urdu: Waqt badalta nahi; sirf likhne ka tareeqa ek jaisa hota hai.

## Step 5: Keep the result

A dataclass groups related values under clear names. Event holds a checked record. ImportResult keeps accepted records, rejected-line reasons, and the blank-line count.

Today these values stay in memory. When the program ends, they are not saved to a database. Database storage comes next. Duplicate event IDs are not handled yet; repeated records are still counted separately.

## Step 6: Show a clear summary

Run the good sample using SETUP.md. Expected: 3 accepted and 0 rejected.

Accepted does not mean the login succeeded. A properly formatted failed-login record is accepted too. It means our program can understand the record.

Run the mixed sample. Expected: 2 accepted, 1 rejected, and 1 blank line. The second record has outcome banana, so it fails the format check.

Roman Urdu: Accepted ka matlab record ka format theek hai. Is ka matlab successful login nahi hai.

## Step 7: Check our code with tests

A test supplies an example and checks the expected result. We ran 27 tests, including invalid dates, wrong IP addresses, missing fields, duplicate JSON keys, mixed good/bad lines, oversized input, and command exit codes.

Passing these tests gives evidence for the reader's tested behavior. It does not prove the whole application is finished or secure.

## Your exercise

1. If outcome is failure and every field is valid, should the reader accept the record?
2. If outcome is banana, should it accept or reject the record?
3. If one line is bad, should the program stop or continue checking later lines?

Answer in the project conversation using simple English or Roman Urdu. No file creation is needed.

## Next session

Store accepted events in SQLite, keep the data after restart, and define duplicate/conflict behavior. We still target October 17 for completion.
