# Day 1 - Understand the system before implementing it

## 1. State the problem

Purpose: explain why the project exists. A security analyst needs to connect related login events and record an evidence-based investigation.

Your explanation: SentinelLab takes login records, detects defined suspicious patterns, and helps an analyst review them. It does not establish guilt or compromise automatically.

Verification: explain the problem without mentioning a framework or programming language.

## 2. Understand the folders

- src/sentinellab/ingestion: turn input records into validated, consistent events.
- src/sentinellab/storage: save and retrieve events, alerts, and investigations.
- src/sentinellab/detection: evaluate rules over related events.
- src/sentinellab/web: present the dashboard and investigation screens.
- tests: prove specific behavior and complete workflows.
- data/samples: shareable synthetic examples.
- docs: requirements, design, lessons, and progress.
- scripts: future setup and lab utilities.
- reports/examples: future sanitized investigation examples.

The application folders currently contain placeholders. There is no application to run yet.

## 3. Follow one event

Open data/samples/day01_login_events.jsonl. Each line represents one event, not a user or an alert. Identify the source, account, time, address, and outcome.

Authentication means checking identity. Authorization means deciding what that identity may access. Our sample records authentication outcomes.

The Z suffix means UTC. Displaying a time in Pakistan time changes its representation, not when the event happened.

## 4. Follow the data flow

Raw event -> validate fields -> normalize time/IP -> store -> evaluate rules -> create evidence-backed alert -> investigate -> export report.

Validation asks whether the input follows our format. Detection asks whether valid events match suspicious behavior. Invalid input is an import problem, not automatically a security incident.

## 5. Understand false positives

One failed sign-in could be a typing mistake. Repeated failures may be suspicious, but a user can make several mistakes. If we flag benign activity, that is a false positive. If a suspicious sequence goes undetected, that is a false negative.

Thresholds trade off sensitivity and noise. We will test normal behavior as well as suspicious scenarios.

## 6. Understand an acceptance criterion

A criterion is an observable statement that lets us decide whether a feature works. Example: importing the same file twice must not create duplicate events.

A test exercises that statement. Documentation alone does not prove it. All release acceptance criteria are pending today.

## Your short exercise

Using the three sample events, answer:

1. How many failed sign-ins occurred, and how many succeeded?
2. Should a rule requiring five failures in five minutes trigger?
3. Does a later successful sign-in prove an account was compromised? Why?
4. Which folder will contain the rule, and which will save the events?

You do not need to write code or create files for this exercise. Send your answers in the project conversation. If the JSON is difficult to read, describe which field is confusing and we will walk through it.

## Day 1 output

A project brief, measurable release criteria, a documented initial event format, a small synthetic example, and a schedule ending October 17. Next: choose and verify the Python environment before building the importer.
