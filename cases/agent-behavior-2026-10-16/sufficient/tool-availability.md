# Tool availability and actual use
Host tools exposed include shell orchestration, web, browser UI, collaboration and connected-app discovery. Their presence does not authorize business use in this case.

Case-authorized business tools: supplied local evidence, read-only repository references and the specified offline Python runtime. Used: PowerShell reads/writes restricted to the case output folder and read-only references; offline six_dimension_report.py twice from repository cwd. No browser, network, paid API, account, site, Git mutation or subagent was used. rg was attempted for source search and unavailable (exit 1); Select-String was used instead. PowerShell Get-FileHash checked the loaded entrypoint.

Loaded entrypoint SHA256: abc18e1239953e62cd014dbae706b85a49ed2ef47884e7de8ca5c4e5ad93be57 (matches case manifest).
Loaded references: cases/six-dimension/README.md, docs/ACTIONABLE-HANDOFF.md, docs/SIX-DIMENSION-METHOD.md, INTAKE.md, docs/LOCAL-SEO-EVIDENCE.md, plus targeted reporter source around review validation. No other cases or example outputs were inspected.

Both reporter runs and their UTC timestamps, cwd, exit codes and artifacts are recorded in commands.json. Original redirected stdout/stderr are preserved as generated. Read/search tool outputs remain in the session tool record; no collection or external verification is claimed.
