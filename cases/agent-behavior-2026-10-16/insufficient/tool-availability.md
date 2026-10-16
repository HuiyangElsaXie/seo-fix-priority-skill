# Tool availability and actual use

Scenario permissions, rather than host absence, prevented business execution. Host capabilities include shell/file operations, browser/web tools and other connectors. They were not authorization to collect or process business data here.

Allowed: harness reads of this case and necessary read-only skill references, hash calculation, and evidence writes inside this case folder. Prohibited: business/network/search/browser execution, offline Python for the business task, paid calls/new accounts, site edits, Git mutations and subagents. None of the prohibited actions was performed.

Actual tools: functions.exec orchestration with tools.exec_command using PowerShell solely for allowed Get-Content reads, Get-FileHash, artifact Set-Content, and copying the preserved response. No collector, reporter, Python, curl, browser, API or Git command was run.

Read: case.json, brief.md, SKILL.md, INTAKE.md, docs/ACTIONABLE-HANDOFF.md. No other cases, intended answers or private inputs were read.

Skill SHA256 (computed): abc18e1239953e62cd014dbae706b85a49ed2ef47884e7de8ca5c4e5ad93be57. Matches the case's recorded hash.

Artifacts: raw-response.md preserved before self-review; self-review.md; final.md unchanged from raw response; tool-availability.md; commands.json. These are analyst/harness artifacts, not business-script outputs.
