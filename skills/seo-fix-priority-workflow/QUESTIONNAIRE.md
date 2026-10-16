# Fillable intake / 可填写访谈问卷

Use this with the canonical [INTAKE.md](../../INTAKE.md) and [input contract](../../INPUT-CONTRACT.md); their definitions govern. This is a fillable companion, not a new scoring policy. Reuse the brief and previous answers, ask only missing/stale/conflicting information, and accept “unknown.” Do not require every field before providing orientation.

配合规范性的 [INTAKE.md](../../INTAKE.md) 与[输入契约](../../INPUT-CONTRACT.md)使用；本文件只是填写工具，不改变评分规则。先复用 brief／已有回答，仅补问缺失、过时或矛盾处；允许“不知道”，无需填完才能获得参考报告。

## Choose your workflow / 选择用法

- AI conversation: load [SKILL.md](SKILL.md) and supply your brief/available evidence → the agent asks missing questions from this form and INTAKE.md → answer what you know → the agent explicitly maps answers and permitted observations into JSON, runs the helper, reviews the output, and writes a report with evidence, limits and next questions.
- AI 对话：加载技能并提供 brief／已有证据 → agent 仅补问缺失信息 → 回答已知内容 → agent 明确映射为 JSON、运行脚本、审阅输出，再提供证据、边界及下一步问题。
- CLI: copy and edit [INPUT.template.json](INPUT.template.json), not Python script code. Run from the repository root as shown below. The CLI is noninteractive: it automatically selects a report mode and emits structured next questions; it does not conduct a chat or stop to ask for answers. An agent/person uses those questions for the next round and reruns a new input version.
- CLI：复制并编辑 JSON 模板，不改脚本代码。命令行不交互，自动判断报告层级并输出后续问题；不会在终端访谈或等待答案。人或 agent 可据此补充下一版输入后重跑。

Filling this Markdown does not import anything automatically. A person or agent must map answers into the exact JSON fields below; no questionnaire parser or arbitrary CSV importer exists. Preserve original sources and outputs under new filenames.

填写本 Markdown 不会自动导入；必须由人或 agent 按下列准确字段映射。没有问卷解析器或任意 CSV 导入器；保留原始来源，输入和输出使用新文件名。

## Start with accessible context / 先复用可访问背景

The AI should first reuse actually accessible, authorized memory, current-chat context and supplied documents. Do not assume global ChatGPT memory or access to other conversations. If the host has no accessible memory, use the supplied brief. The CLI has no memory connector: it reads only the JSON file. Do not add memory-specific keys to the schema.

AI 先复用实际可访问且获准使用的记忆、当前对话和已提供文档；不得假设能读取全局 ChatGPT 记忆或其他聊天。宿主没有可访问记忆时使用所提供的 brief。CLI 没有记忆连接器，只读 JSON；不要添加契约外的记忆字段。

Briefly state the business, audience and objective being used, with source/date and confidence for critical fields. Distinguish supported facts, self-reports and inferences. Check whether information is stale, conflicting or belongs to another client; the latest user instruction takes precedence. If context is sufficient, continue authorized read-only analysis without mandatory reconfirmation; ask only for gaps, conflicts or time-sensitive essentials. Unknown answers remain valid and may still appear in the CLI's unanswered-question output; do not force the user to repeat them each round.

先简述采用的业务、人群与目标，关键字段注明来源、日期及把握程度；分清事实、自述与推断。检查资料是否过时、冲突或属于其他客户，以用户最新指示为准。背景足够时直接继续已授权的只读分析，无需强制重复确认；仅补问缺口、冲突或时效敏感的关键信息。未知回答仍有效，CLI 可能继续将其列入后续问题，不代表每轮都必须逼用户重答。

Use the existing `sources` and structured-answer fields to record provenance: source scope/provenance in `description`, actual date in `observed_at`, and `source_id`/`evidence_locator`/`status` in answers. Explain confidence in prose; there is no input `confidence` field for answers. Treat inferred background as `assumption`, not `confirmed`. If an old recollection has no attributable source/date, do not invent one or use it to unlock priority.

来源映射沿用已有 `sources` 与回答字段：`description` 说明范围／来历，`observed_at` 为真实日期，回答使用 `source_id`／`evidence_locator`／`status`。把握程度用文字说明，输入答案没有 `confidence` 字段。推断使用 `assumption`，不能标成 `confirmed`。旧记忆没有可追溯来源／日期时，不能编造，也不能用它解锁评分。

Memory supplies context only; it never replaces actual crawl/Search Console evidence or grants permission to fetch, modify or publish. This helper does not directly import Search Console data. Keep personal/client memory out of this public repository and its templates; use a separately authorized private working input for real projects.

记忆仅补充背景，不能替代真实抓取／Search Console 证据，也不授予采集、修改或发布权限。本脚本不直接导入 Search Console。个人／客户记忆不得写入本公开仓库或模板；真实项目使用另行授权的私有工作输入。

**Fictional conversational example / 虚构对话示例 (not supplied project facts / 非实际项目事实):**
“Your supplied brief (2026-10-10, audience section) describes a fictional industrial supplier serving UK procurement teams; your latest message changes the goal from awareness to qualified enquiries. I'll use the latest goal. These are attributed self-reports, not verified market facts. The enquiry event is still unspecified: what event counts as a qualified enquiry? No crawl rows have been provided, so I can offer a framework but cannot diagnose pages.”

“已有资料显示：虚构 brief（2026-10-10，人群章节）描述的是面向英国采购团队的工业供应商；你最新消息把目标从知名度改为合格询盘。本次据此采用最新目标，以上均为可追溯自述，不是已验证市场事实。目前还缺询盘事件定义：什么事件算合格询盘？尚未提供抓取行，因此现在可给框架，但不能诊断页面。”

## Record source and answer status / 先记录来源与回答状态

Fill once per actual source; use additional source IDs for separate exports or briefs.

- Source ID / 来源 ID: ____ → a key under `sources`; answers and rows reference it via `source_id`.
- Source kind / 类型: ____ → `kind`: `supplied_manual_check` (e.g. supplied brief/answer), `supplied_export`, or `fictional_fixture` (fiction only).
- Scope and provenance / 覆盖范围及来历: ____ → `description` (nonempty).
- Observation date / 观察日期: ____ → `observed_at`, ISO `YYYY-MM-DD`, no later than top-level `as_of` (report reference date / 报告基准日): ____.
- Locator convention / 可追溯位置规则: ____ → `evidence_locator`, e.g. actual brief section or export row. Do not invent a locator to missing evidence.

For every structured answer, fill: value / 内容 ____; status / 状态 ____; source_id / 来源 ____; evidence_locator / 位置 ____.

Exact `status` keys: `confirmed` = supported by supplied evidence, not independently verified by this helper; `self_reported` = attributed self-report; `assumption` = explicitly unverified hypothesis, cannot unlock priority; `unknown` = unknown with `value: null` or empty string. `confirmed` and `self_reported` require a registered source ID and nonempty locator. Known values are strings; assumptions also require nonempty text. Missing structured fields mean unknown.

准确状态键：`confirmed`（所供证据支持，不等于脚本独立核实）、`self_reported`（可追溯自述）、`assumption`（假设，不能解锁排序）、`unknown`（`value` 为 null 或空字符串）。前两者必须有有效来源及位置；假设仍需非空文本。缺失的结构化字段视为未知。

Unknown answer / 未知回答: `{"value": null, "status": "unknown"}`.
Known answer shape / 已知回答格式: `{"value": "your supplied answer", "status": "self_reported", "source_id": "your_actual_source_id", "evidence_locator": "your_actual_locator"}`. Replace the illustrative text; it is not evidence.

## Five opening groups / 五组初始问题

For each line, use the answer/status/source/locator format above. Keys below belong under `business_context.answers` unless stated otherwise.

每行按上述格式填写内容、状态、来源、位置。除特别注明外，字段均放入 `business_context.answers`。

### 1. Business and market / 业务及市场
- What industry/business? / 行业与业务？ `industry`: ____
- Who is the audience? / 服务谁？ `audience`: ____
- What market geography? / 目标地区？ `geography`: ____
- What content/audience language? / 内容与受众语言？ `language`: ____

### 2. Position and lifecycle / 定位与生命周期
- Competitive positioning and supporting evidence? / 竞争定位及证据？ `positioning`: ____
- Brand stage? / 品牌阶段？ `brand_lifecycle`: ____
- Product stage, separately? / 产品阶段（单独回答）？ `product_lifecycle`: ____

Self-description is not verified market leadership, demand or traffic impact. / 自述不等于已验证的市场领先、需求或流量影响。

### 3. Goal and concrete problem / 目标及具体问题
- Primary objective? / 主要目标？ `primary_objective`: ____
  Exact values / 准确取值: `awareness` 知名度; `consideration` 考虑／评估; `conversion` 转化; `retention` 留存; `mixed` 混合; `other` 其他. If unknown, use null + unknown status rather than inventing an enum value.
- Why this review now; what specific problem? / 为什么现在检查，具体想解决什么？ `specific_problem`: ____ (unknown is valid / 可以未知)
- Brief human goal summary / 人可读的目标摘要: ____ → `business_context.objective`, required nonempty string; use `"unknown"` if unavailable. This summary alone does not fill structured essentials. For consideration, describe the evaluation behavior/success signal here.

### 4. Success, resources and constraints / 成功标准、资源与限制
- Which event counts as success? / 什么事件算成功？ `conversion_definition`: ____
  Required for tailored conversion/retention/mixed; “more traffic” alone is not a conversion event. / 转化、留存、混合目标要达到定制层级需有明确事件；“增加流量”不等于转化事件。
- For mixed goals, which is primary and what tradeoff is approved? / 混合目标的主次及取舍？ `objective_tradeoff`: ____ (source-backed answer required for tailored mixed mode / 混合目标定制报告需有来源依据)
- Available people/time/implementation capacity? / 人力、时间、实施能力？ `resources`: ____
- Restrictions or approvals needed? / 限制及审批要求？ `constraints`: ____
  If there are genuinely none, record that as an attributed answer, not an assumption. / 确实无限制也应作为有来源的回答，不能自行假设。

### 5. Important pages and owners / 关键页面与负责人
- Which pages support the goal, why, and who decides/implements? / 哪些页面支持目标，为什么，谁确认及实施？ ____
- Engineering owner / 工程负责人: ____ → `business_context.owners.engineering`
- SEO owner / SEO 负责人: ____ → `business_context.owners.seo`
- Content owner / 内容负责人: ____ → `business_context.owners.content`

Use nonempty actual names/teams; omit unknown roles (the starter uses `{}`). There is no separate decision-owner JSON field; retain that answer in the brief. Map actual page observations below; do not turn a bare URL or business answer into a technical observation.

负责人填真实非空姓名／团队；未知角色省略（模板为 `{}`）。JSON 没有单独的决策负责人字段，可保留于 brief。仅按下节录入实际页面证据，不能把 URL 或业务回答变成技术观察。

## Relevant branches / 按需分支
- Site age / 站龄: ____ → `business_context.answers.site_age`
- Migration dates, changed URLs/templates, rollback restrictions / 迁移日期、URL／模板变化及回滚限制: ____ → `business_context.answers.migration_history`; implementation restrictions may also belong in `constraints`.
- Intended visibility, deliberate noindex/access control/canonical choices / 预期可见性、刻意 noindex／访问控制／canonical: ____ → per-page fields below. Protect intentional exclusions regardless of conversion goals.

Site age is separate from brand/product lifecycle. Positioning/lifecycle never creates impact multipliers. / 站龄不等于品牌或产品生命周期，定位及生命周期不自动成为收益或影响倍数。

## Repeat for each supplied page / 每个已提供证据的页面填写一组

Do not add a row until required observation fields are available. `rows: []` is valid and produces no page diagnosis. Unknown HTTP status cannot be null; keep that URL in the brief for follow-up rather than fabricating status 200.

必填观察字段不足时先不加行。`rows: []` 合法，但不提供页面诊断。HTTP 状态不接受 null；未知时将 URL 留在 brief 待补证，不能编造 200。

Required plain row fields / 必填普通字段:
- Exact absolute HTTP(S) URL, no credentials / 完整 URL、无凭据: ____ → `url`; exact duplicates require explicit reconciliation.
- Observation source and locator / 观察来源及位置: ____ / ____ → `source_id`, `evidence_locator`
- Observed HTTP status integer 100–599 / 已观察 HTTP 状态整数: ____ → `status` (different from structured-answer status / 不同于回答状态)
- Intended search visibility / 搜索可见性意图: ____ → `intent`: `index` / `exclude` / `unknown`
- Business importance / 业务重要性: ____ → `importance`: `critical` / `supporting` / `low` / `unknown`

Structured row answers using the same value/status/source/locator format / 以下行字段使用同样的结构化回答格式:
- Why this page matters to the stated goal / 此页如何支持目标: ____ → `business_impact`
- Why it should be indexed/excluded; deliberate noindex? / 索引／排除理由，是否刻意 noindex: ____ → `visibility_reason`
- Why canonical differs, if applicable / canonical 不同的原因（如适用）: ____ → `canonical_intent`

Optional supplied signals / 可选的实际信号:
- `indexable`: ____; `robots_blocked`: ____ → JSON boolean `true`/`false` or `null` (not quoted strings).
- `canonical`: ____ → absolute URL, empty string or `null`; `title`: ____ → string or `null`. An actual empty title is not an unknown title.
- `depth`: ____; `inlinks`: ____; `redirect_hops`: ____ → nonnegative integer or `null`. Missing measurement is not zero.
- `effort`: ____ → integer 1–10; omit if unknown, because `null` is invalid for effort. Do not substitute a default estimate.

Unknown optional measurements can be omitted/null as allowed above. Never infer indexability from HTTP status. Business scoring additionally requires tailored context, page rationale/visibility, known importance/index intent, supplied effort, accountable role owner, fresh evidence and every rule-specific gate. Canonical differences and zero-inlink findings still require manual corroboration.

未知测量按上述规则省略／填 null。不得从 HTTP 状态推断可索引性。业务评分还要求定制背景、页面依据及可见性、已知重要性与索引意图、工作量、负责人、有效时效及全部规则门槛；canonical 差异及零入链仍需人工验证。

## Run and interpret / 运行与解读

From the repository root / 在仓库根目录运行:

```sh
python scripts/triage.py skills/seo-fix-priority-workflow/INPUT.template.json > /tmp/seo-input-template-output.json
```

The unchanged starter is explicitly empty fictional scaffolding, not a website or client example. It has a fixed reference date of 2026-10-16, unknown business answers and no rows. Before real use, copy it to a new file, set the actual report date, replace `template_stub` with actual source entries and original observation dates, and add only supplied rows/answers. Do not refresh dates merely to pass a freshness gate.

原始模板是明确的空白虚构框架，不代表网站或客户案例。基准日固定为 2026-10-16，业务答案未知，页面为空。实际使用先复制新文件，填真实报告日期，以真实来源及原始观察日期替换 `template_stub`，仅添加已提供的行与答案；不能仅为通过时效检查而改日期。

Expected unchanged-template output / 原样运行的预期输出:
- `intake.mode`: `generic_framework`
- `summary.supplied_urls`: 0; `summary.candidate_findings`: 0; `queue`: `[]`
- `intake.missing_essential`: eight missing essentials; `intake.questions`: 13 unanswered context questions; `intake.page_questions`: `[]`

An empty queue or empty coverage gaps here means no supplied page observations, not a healthy website or completed audit. No diagnosis is possible without supplied rows. The agent can still explain the framework and request evidence.

此时空队列／空覆盖缺口只表示没有提供页面观察，不等于网站健康或审计完成。没有页面行就没有页面诊断；agent 仍可解释框架并请求证据。

The helper automatically selects exactly three modes; no mode flag or script edit is required / 脚本自动选择且仅有三种层级，无需模式开关或改代码:
- `generic_framework`: industry unknown/assumed / 行业未知或仅假设。
- `industry_general`: source-backed industry known but essential context incomplete / 行业有来源依据，关键背景仍不全。
- `tailored`: all essentials source-backed, including conditional conversion/tradeoff fields / 关键背景均有来源依据，含适用的转化事件及混合目标取舍。This does not guarantee any score; page/evidence gates still apply / 不保证有评分，仍受页面与证据门槛约束。

Next questions live in `intake.questions` (field/reason) and `intake.page_questions` (URL/questions), not a top-level `next_questions` field. An agent uses them conversationally; the CLI only prints JSON. The final human report follows INTAKE.md: context/level → observed evidence → conditional recommendations → unknowns → validation/owner. No website changes or publishing are authorized.

后续问题位于 `intake.questions`（字段／原因）与 `intake.page_questions`（URL／问题），不是顶层 `next_questions`。agent 可用于对话，CLI 只打印 JSON。最终人工报告沿用 INTAKE.md 的顺序：背景／层级→证据→条件式建议→未知→验证／负责人。本工具不授权修改或发布网站。

## URL-first six-dimension branch / URL 六维度分支 (v0.4)

Reuse the business answers above. The existing INPUT.template.json remains the supplied-data triage template. URL mode accepts a website and optionally a separate context JSON; Markdown/memory are not automatically imported. Exact shapes: [six-dimension examples](../../cases/six-dimension/README.md).

复用上面的业务答案，不重复提问。原模板继续用于已提供数据模式；URL 模式可另加 context JSON，不自动导入问卷或记忆。

Ask only relevant missing branches / 只问相关缺口：
- Public URL and desired scope / 公开网址及检查范围：____
- Local: actual in-person customer contact or eligible service-area business? Do not infer from an address. / 是否真实线下接待或符合条件的服务区域业务？不可仅凭地址推断：____
- Ecommerce: current product sales, or only past ecommerce case studies? / 当前卖货，还是仅展示过去电商项目？____
- International: intended equivalent language/region URL versions? / 计划中的同内容语言/地区版本？____
- Available field CWV, backlinks, local listing or product/feed comparisons, with scope/source/date? / 可提供的补充数据及范围/来源/日期？____

Map applicability to `applicability.local/ecommerce/international` with `value: yes|no|unknown`; explicit yes/no also require `reason`, `source`, `date`. Measurements use documented supplemental records. Business answers do not replace measurements. Unknown is valid and produces limited/general reporting, not invented failures, priority or ROI. Keep real answers and client data outside this repository.

## Six-dimension applicability intake / 六维适用性提问

For the URL-first reporter, use [SIX-DIMENSION-CONTEXT.template.json](SIX-DIMENSION-CONTEXT.template.json) with `six_dimension_report.py --context`. This is a different context file from the legacy triage.py INPUT.template.json. Markdown answers are not automatically imported; the AI/person maps them explicitly.

先简述已经复用的背景与来源，例如：“已有资料显示这是求职作品集，主要读者是招聘者；未确认是否承接当地到店服务。”只补问缺失、冲突或时效性信息；无回答用 unknown，不反复强制确认。首次把以下内容合并成最多三个问题，后续才按适用分支追问。

1. **Purpose / 目的**：网站主要用于作品集、内容阅读、咨询获客，还是实际在线销售？谁会来，预期完成什么动作？填写 business_model 的 source/reason，结合原业务目标；网站形态或独立域名本身不决定适用性。
2. **Local service / 本地需求**：是否有真实到店、上门服务或特定地区获客目的？顾客需不需要到某个地点？这是公开营业地址还是不能公开的私人/服务区域地址？将 local_customer_service、local_acquisition_goal 标为 yes/no/unknown；只有确认需要引导到店且地址可公开，map_visit_context 才能是 yes。
3. **Transactions / 交易功能**：是否真的在线出售商品或服务、下订单、结账/付款？还是仅展示目录、预约、咨询表单？online_transactions 按实际交易功能判断；一个联系/预约表单不自动等于电商。commercial 指实际商业目的，不是看到某个商品图片。

仅在本地分支适用时追问：是否已有 GBP？正确 listing/place ID 和门店是哪一个？单店还是多店？营业地址能否公开？营业时间/特别时段由谁确认？不知道就记录待核验，不为了完成报告创建新账号、收集凭证或公开住址。GBP有无不决定本地业务是否适用，也不能从地图缺失推断没有GBP。

Only when local scope is relevant, ask about existing GBP/listing identity, branch count, public-address policy, actual customer visits and current hours. Keep these answers as attributed business context and evidence metadata, not invented verification. For Maps inspection, use map_visit_context for the visitor task and expected branch identity from supplied evidence. Public-address consent/privacy is distinct from SEO relevance.

### Actual mapping / 真正接入报告的字段

- business_model.commercial / local_customer_service / local_acquisition_goal / online_transactions: yes, no or unknown; shared source/date/reason records provenance.
- Explicit applicability.local/ecommerce overrides inferred defaults; include reasons and dated sources for yes/no. Keep explicit unknown when unresolved.
- Reuse known answers to derive applicability; local yes from a supported local service/acquisition purpose, online_transactions yes/no controls ecommerce. Noncommercial default does not force either; explicit positive local purpose or online transaction evidence still matters.
- Missing map, missing cart or missing schema never answers these questions. Unknown and N/A do not receive a score penalty. N/A excludes that dimension's defect checks and explains why.

例子：个人作品集/纯线上非商业内容通常无需 local/ecommerce；无线上销售的本地店可以 local适用、ecommerce不适用；独立域名诊所仍可适用local；有当地服务与在线交易的多门店品牌可以两者都适用。以上以真实回答为准，不是根据网址自动贴标签。
