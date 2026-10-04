# SentinelLab portfolio material

Prepared 4 October 2026. This folder presents the implemented local learning prototype, not a production security deployment or completed release certification.

- [Five minute demonstration](DEMO_SCRIPT.md): ordered steps, speaking notes, expected results and recovery.
- [Project case study](CASE_STUDY.md): problem, design, evidence, tradeoffs, evaluation and limitations.
- [CV and interview notes](CV_AND_INTERVIEW.md): accurate project wording, explanation prompts and ownership guidance.
- [Release readiness](../RELEASE_READINESS.md): all fifteen acceptance criteria mapped to evidence and remaining checks.
- [Synthetic example report](sample-report.md) and [JSON version](sample-report.json): real exports from the browser-created demonstration case. Their export timestamps differ because they were generated separately; saved case, actions and evidence agree.

All screenshots and example report data in this folder are synthetic. They show the actual application, not generated mockups. Screenshots are viewport excerpts, not a complete export of every record or a full accessibility audit. No credential file, cookie or private investigation was included.

## Overview

The demo has 16 saved events after two imports of the same sample. Completed imports counts attempts; saved events counts unique records.

![Synthetic overview with 16 saved events and two imports](screenshots/01-overview.jpg)

## Explained finding

R3 links five earlier failures and one successful login for lab_user at 192.0.2.71. The interface explains the threshold and warns against concluding compromise. Additional evidence rows continue below this viewport.

![R3 explanation and saved rule facts](screenshots/02-alert.jpg)

## Reasoned investigation

Case 1 is In progress / Suspicious at revision 3 after creation, a note and a decision. This is not a confirmed incident. The report exports retain the full saved history and original evidence.

![Synthetic investigation at revision three](screenshots/03-case.jpg)
