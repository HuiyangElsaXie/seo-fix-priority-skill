import pathlib,json
root=pathlib.Path.cwd(); case=root/'round2-agent-runs/seo-fix-priority-skill--sufficient-contract-retest'
p=case/'commands.json'; original=p.read_bytes(); (case/'commands-v1.json').write_bytes(original)
records=json.loads(original);records[0]['command']=[str(root/'.runtime/python-tests/python.exe'),'scripts/six_dimension_report.py',str(case/'mapped-inputs/snapshot.json'),'--context',str(case/'mapped-inputs/context.json'),'--out',str(case/'initial-report')]
records[0]['record_correction']='Reconstructed exact argv path values from recorded PowerShell invocation; original timestamp/exit telemetry preserved. commands-v1.json retains the earlier inconsistent relative display paths.'
p.write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
(case/'command-record-review.md').write_text('''# Command-record review
The first entry in commands.json incorrectly combined repository cwd with case-relative input/output display paths. The actual PowerShell invocation used absolute paths built with Join-Path from the original workspace cwd, then Push-Location to the repository root. Its script argument was scripts/six_dimension_report.py.

Preserved the prior record byte-for-byte as commands-v1.json. Corrected only the first entry command array to those actual absolute runtime/input/context/output path values, reconstructed from the recorded tool invocation. Repository cwd, start/end timestamps, exit code and stdout/stderr filenames remain unchanged. These timestamps bracket the invocation and location changes; they are not process-internal timing measurements. No additional timing telemetry is asserted.

No business rerun occurred. Report files, mapped inputs and raw stdout/stderr were not rewritten. Subsequent command entries already used absolute input/output paths and were retained. This is same-agent record review, not independent approval.
''',encoding='utf-8')
print('Preserved commands-v1.json; corrected first argv; wrote command-record-review.md.')
