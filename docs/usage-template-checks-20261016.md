# Usage template checks / 用法模板检查

Checked locally on 2026-10-16 against the existing v0.3 implementation. Scope: documentation and starter-input compatibility only; no live website, client data, implementation change or SEO outcome validation.

2026-10-16 本地检查，使用既有 v0.3 实现。仅验证文档与初始输入兼容性；不涉及真实网站、客户数据、实现变更或 SEO 成效验证。

## Executed commands and results

From repository root:

```sh
python scripts/triage.py skills/seo-fix-priority-workflow/INPUT.template.json > /tmp/seo-input-template-output.json
python -m unittest discover -s tests -v > /tmp/seo-docs-tests.log 2>&1
```

Both commands exited 0. The unchanged template produced:
- `intake.mode`: `generic_framework`
- `summary.supplied_urls`: 0
- `summary.candidate_findings`: 0
- `queue`: `[]`
- `intake.missing_essential`: 8 fields
- `intake.questions`: 13 context questions
- `intake.page_questions`: `[]`

The existing test suite ran 44 tests: all passed. Runtime JSON and test logs were left in temporary storage outside the repository; this note records the observed result, not a committed copy of those temporary files.

既有 44 项测试全部通过。运行输出及日志保留于仓库外临时目录；本文件记录观察结果，不包含临时文件副本。空队列只说明没有输入页面，不能据此诊断网站或认定健康。

## Additional checks

- The template passed the existing `scripts.triage.validate` function.
- Its 15 `business_context.answers` keys exactly matched the existing `CONTEXT_FIELDS` set.
- All 15 field mappings were present in the bilingual questionnaire, including fully qualified site-age and migration-history paths.
- Relative Markdown links in both READMEs, SKILL.md and QUESTIONNAIRE.md resolved locally.
- The starter uses unknown/null structured answers, an empty owner map and empty rows; its only source is explicitly labeled empty fictional scaffolding.
- Documentation distinguishes answer `status` from numeric row HTTP `status`, unknown effort (omit; null invalid), source kinds and source/locator requirements.
- Memory-first behavior is AI workflow guidance only. The CLI reads JSON and has no memory integration or questionnaire importer.

These checks do not independently verify supplied evidence, grant website-change permission, establish broader production readiness, or alter existing executed-case evidence.
