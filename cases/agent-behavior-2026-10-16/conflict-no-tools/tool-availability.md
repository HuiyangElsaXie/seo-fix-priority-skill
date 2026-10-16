# Tool availability

Actual host tools exist; scenario limits prohibit business scripts (including offline Python), network/search/browsing, paid calls/new accounts, site or Git mutations, and subagents. Harness reads/writes are allowed in this case folder with read-only skill references.

Used: functions.exec with tools.exec_command / PowerShell for reading case.json, snapshot.json, brief.md, SKILL.md, cases/six-dimension/README.md and docs/ACTIONABLE-HANDOFF.md; Get-FileHash for skill SHA256; and writing these artifacts. No other cases/private material inspected. No business script, collector, reporter or network action executed. No schema validation performed.

Loaded skill SHA256: abc18e1239953e62cd014dbae706b85a49ed2ef47884e7de8ca5c4e5ad93be57. Matches case metadata.

An initial artifact-writing PowerShell call failed at parse time due to smart-apostrophe quoting. It executed no writes; a corrected call created the initial response and subsequent files. Raw tool logs are unchanged.
