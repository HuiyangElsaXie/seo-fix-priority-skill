# Adaptive intake / 自适应业务访谈 (v0.3)

Start with supplied briefs and previous answers. Repeat only missing, stale or conflicting answers. Ask these five grouped prompts conversationally, then only relevant branches. “Unknown” and “I cannot describe a specific problem” are valid answers. Do not demand an exhaustive questionnaire before offering useful orientation. Do not fetch data or infer an answer from a brand name.

先阅读已有 brief 和用户回答；只补问缺失、过时或矛盾处。第一轮分成以下五组，之后按需追问，允许“不知道”或“说不清具体问题”。不得因问卷未完成拒绝提供通用参考，也不得凭品牌名称补造事实。

1. What business/industry, audience, market geography and language are we serving? / 行业、服务对象、目标地区与语言分别是什么？
2. How do you describe the brand's competitive position? What evidence supports it? What stages are the brand and product in, separately? / 品牌竞争定位及依据是什么？品牌与产品分别处于什么生命周期？可标记为本人描述、假设或未知，不能当成已验证市场事实。
3. What is the primary purpose: awareness, consideration/evaluation, conversion, retention, mixed or other? What concrete problem prompted this review? / 本次优先目标是知名度、考虑/评估、转化、留存、混合还是其他？具体希望解决什么问题？如果无法说明，仍可提供行业通用报告。
4. What event would count as success, and what resources, time or implementation restrictions apply? / 什么行为算成功？有哪些人力、时间及实施限制？转化/留存/混合目标必须明确事件，例如合格询盘提交；“提高流量”不等于转化定义。
5. Which pages matter to that goal, and who owns decisions? / 哪些页面支持上述目标，为什么重要，谁负责确认与实施？没有关键页面依据时保留技术诊断，不编造业务排序。

## SEO branches / 按需追问
- Visibility: intended index/exclude/unknown, why; deliberate noindex, robots controls or cross-page canonical? Preserve exclusions regardless of conversion ambition. / 确认每页预期可见性及原因；有意 noindex、访问控制或跨页 canonical 不得为转化目标自动取消。
- Site age and migration history are separate from brand/product lifecycle. Ask dates, changed URLs/templates and approved rollback constraints when relevant. / 站龄与迁移史不等于品牌/产品生命周期；迁移相关时补问日期、改动范围与回滚限制。
- Awareness: name relevant discovery/education pages and approved success signals. No invented impressions or industry demand. Conversion/retention: define the event, audience, funnel role and page-level rationale; request permitted evidence when available. / 知名度目标确认发现/教育型页面与指标；转化/留存确认事件、人群、漏斗角色及页面依据。没有数据时不推断损失。
- Before ranking: obtain each page's business importance + sourced rationale, visibility rationale, supplied effort estimate and accountable role owner. / 排序前取得页面重要性及来源、可见性依据、工作量估计和负责人。
- If no issue triggers, still surface unanswered page/context questions; an empty queue is not a health score. / 即使无技术命中，也保留未解业务问题；空队列不代表满分。

## Three report levels / 三种报告层级
- tailored / 定制：essential context supplied; only findings passing all evidence gates receive provisional scores. Self-reported context remains labeled unverified.
- industry_general / 行业通用：industry known but concrete problem/objective or other essential context missing. Still useful for orientation, supplied technical observations, checks, decision criteria and next questions. It is not a bespoke priority list. No unsourced industry norms, competitor claims, demand or ROI.
- generic_framework / 通用框架：industry is unknown. Supply a general diagnostic framework, actual supplied observations and what to validate next. Do not claim industry-specific insight.

Report structure: context and level → observed technical evidence → conditional recommendation → assumptions/unknowns → next validation and owner. Clearly separate technical severity from business urgency. A technical HTTP error can be reported in every level; business urgency stays unestablished when context is missing. Unknown answers reduce specificity, not reference value.

报告顺序：背景和层级 → 技术观察及证据 → 条件式建议 → 假设/未知 → 下一步验证和负责人。HTTP 错误可以客观报告，但缺少业务证据时不得称紧急、高收益或给出伪精确排序。

For mixed goals, supply source-backed objective_tradeoff naming the primary goal and tradeoff; unresolved mixed priorities keep the report general and scores withheld. Consideration/evaluation uses primary_objective=consideration; name the evaluation behavior or success signal in the objective summary.
混合目标须说明主次与取舍（objective_tradeoff）；未解决的目标冲突不能解锁业务排序。考虑/评估目标使用 consideration，并说明评估行为或成功指标。
