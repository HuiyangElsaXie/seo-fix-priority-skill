# SEO 检查与修复优先级工作流

**提供一个网站 URL，采集有限的公开页面样本并生成有证据出处的六维度 SEO 检查报告；也可以直接分析你提供的抓取数据，形成修复队列。** 报告区分观察到的事实、缺失证据、适用范围和待复核项，不承诺仅凭网址完成全面验证。

[English](README.md) · [AI 使用步骤](skills/seo-fix-priority-workflow/SKILL.md) · [中英可填写问卷](skills/seo-fix-priority-workflow/QUESTIONNAIRE.md) · [六维度方法与工具](docs/SIX-DIMENSION-METHOD.md)

**改编自 [Snippet Digital 的 MIT technical-seo-audit skill](https://github.com/Snippet-Digital-Agency/tech-seo-audit-skill/tree/8b5b5d5c776ec71a0d427bd6760dfeca058b404c)。** 原版权 © 2026 Snippet Digital。[原始 skill](upstream/snippet-digital/SKILL.md)、[完整 MIT 许可](upstream/snippet-digital/LICENCE)、[固定版本记录](upstream/source-lock.json)与[具体改动映射](ADAPTATION.md)均保留。新增公开采集和报告程序为本项目编写，并非上游爬虫，也不代表上游认可。[新增内容许可仍待作者决定](LICENSE-PROPOSAL.md)。

最初用于非商业学习与职业作品展示；这不改变上游 MIT 权利，也不意味着技术上只能演示。在输入获准使用、人工审核后，可辅助日常或接案分析和开发交接。这里不宣称它是作者的主要生产工作流或经过完整验证的 SEO 服务平台。

使用前的目的/适用性问题与可运行 JSON 见[提问文件](skills/seo-fix-priority-workflow/QUESTIONNAIRE.md)及[六维 context 模板](skills/seo-fix-priority-workflow/SIX-DIMENSION-CONTEXT.template.json)。AI 先复用已知背景，缺失才问；CLI 编辑 JSON 后传入 --context。按实际本地服务和交易功能排除不适用维度，不因没有地图或购物车扣分。

## Local SEO 证据与评价示警

本地检查使用匹配到具体门店的证据，核对 NAP/营业时间、有限 LocalBusiness 字段，以及 Google 总评分/总评价数。缺数量保持未知，明确观察到零评价才建议中性邀请真实顾客评价。低评分和少评结合可调阈值、证据日期、样本量与可比背景判断；阈值不是 Google 规则。报告包含证据、不确定项、建议行动和验收方式。

详见[取证/导入流程及官方来源](docs/LOCAL-SEO-EVIDENCE.md)。仓库没有自动连接 GBP/Places、付费查询、回复评论或修改资料。需要通过可用公共工具或授权导出取得证据后导入；可见样本不能代替总评价数，也不能代表整体近期趋势。

## 最终报告会给出什么（v0.5）

行动交接分成**已确认修复、具体待验证任务、可选优化、保持不动/不适用**四组。每项行动给出证据、处理顺序理由、具体步骤、建议执行角色、依赖和验收条件。技术信号不会自动变成已确认缺陷。程序生成的最终报告与分析者写的测试说明分别交付。

规则命中默认是调查候选，需证据和明确复核建立预期行为后才能确认修复；未知业务影响不转换成虚构的紧急程度。即使零命中，也说明样本范围内可保持的部分及具体补证检查，不冒称网站健康。见[行动报告规则](docs/ACTIONABLE-HANDOFF.md)和[合成缺陷真实性测试](cases/actionable-handoff/)。

## 具体应用场景

- **新作品集或小企业网站：** 输入网址、受众和业务目标。输出样本范围内的技术/内容观察和六个报告章节，明确哪些专项适用。有城市地址不等于符合本地商家资格，展示电商项目不等于网站正在卖货。
- **客户已做好数据：** 输入规范化抓取记录、页面是否应被索引及业务背景。输出带证据、负责人和验收方式的修复/调查候选队列。离线程序不会自动识别任意 CSV 列名。
- **实际电商或多语言服务：** 输入网址、明确的适用性说明，以及可提供的带日期商品/feed、语言市场或外链材料。输出有依据的对照结果，指出需要账号资料或人工继续验证的部分。

## 实际自动执行到哪里

1. `collect_public_site.py` 有限、只读地请求公开页面：robots、HTML 元数据和正文、canonical/hreflang、JSON-LD、站点地图样本及已观察的内部链接。不渲染 JavaScript，不登录。
2. `six_dimension_report.py` 离线分析快照，生成 `report.json` 和 `report.md`，涵盖技术、页面/内容、站外、本地、电商、国际化六部分。六个章节代表覆盖框架，不代表六项都已完成自动验证。补充证据可扩大检查范围；缺失仍明确列出。
3. AI/人工复核意图、内容价值、资格、刻意排除和行动建议。机器输出保留“语义复核待完成”，复核记录不得覆盖原始输出；报告可以纳入经过格式与证据关联校验的明确复核决定，并标明它仍是所提供的判断。
4. 原有 `triage.py` 保留“分析已提供数据”的八条规则模式及修复队列。其有条件的 40/40/20 公式不用于六维度总分，也不是 Google 排名分。

Python 3.10+，只用标准库。不需要付费 API、SEO 软件套件或账号连接，不执行发布或部署。

## 通过 AI 对话使用

加载 [SKILL.md](skills/seo-fix-priority-workflow/SKILL.md)，提供 URL 或证据及需求。AI 先复用当前宿主真正可访问且获准使用的记忆、对话和文档，简述已知业务、受众、目标及来源，只追问缺失、冲突或时效敏感的关键项。不会假定能读取所有 ChatGPT 历史；信息足够时直接进行已请求的只读分析，无须重复确认。记忆不能替代抓取/GSC/真实用户性能数据，也不能授予操作权限。

[问卷](skills/seo-fix-priority-workflow/QUESTIONNAIRE.md)和[统一提问定义](INTAKE.md)涵盖行业、市场/语言、定位、生命周期、目标/转化、资源和重要页面。另需确认是否真实线下接待客户、是否销售商品、是否存在语言/地区版本，以决定专项适用性。未知是有效回答；不要把个人或客户记忆写进仓库模板。

不能提供具体问题或目标时，**行业通用报告仍有参考价值**：提供方向、条件式检查和下一步问题。连行业也未知时，输出通用框架及已观察到的技术事实。两者都不编造需求量、行业基准、业务紧急程度或 ROI。三个层级为 `tailored`、`industry_general`、`generic_framework`。

## 直接运行 Python

提前编辑输入 JSON，不需要修改 Python 代码。CLI 不会在终端逐题提问，也不会自动导入填写好的 Markdown 问卷，需要使用者或 AI 映射字段。每次用新的输出目录，保留旧记录。

```sh
# URL 公开样本。输出建议放在仓库之外。
python scripts/collect_public_site.py https://example.com --out /tmp/seo-public-new-run --max-pages 20
python scripts/six_dimension_report.py /tmp/seo-public-new-run/snapshot.json --out /tmp/seo-report-new-run

# 虚构样本；可选 context/supplement 的字段见下方文档。
python scripts/six_dimension_report.py cases/six-dimension/snapshot.json --out /tmp/seo-fictional-new-run

# 原有已提供数据模式；空模板不含编造的网站观察。
python scripts/triage.py skills/seo-fix-priority-workflow/INPUT.template.json > /tmp/seo-empty-template-output.json
# Optional explicit review: see docs/ACTIONABLE-HANDOFF.md for schema and two-pass usage.
python -m unittest discover -s tests -v
```

[六维度样本/输入说明](cases/six-dimension/README.md)提供实际文件及 `--context`、`--supplement` 格式；[INPUT-CONTRACT.md](INPUT-CONTRACT.md)说明原有规范化抓取输入。没有证据不能证明网站健康。原有空模板会自动输出通用框架、下一轮问题及空队列。

## 证据与边界

采集受来源范围、robots、请求数/页面数/体积/时间预算约束。样本不能证明站点地图完整、实际索引状态、全部外链、Google 选定 canonical、渲染内容、转化或真实用户 Core Web Vitals。采集报错/被阻止属于证据缺口，不自动判成网站故障；缺数据不填猜测值。遵守 robots 也不代表获准读取私有数据。

不会自动认定 Business Profile 资格、用 DA 保证权威、给 E-E-A-T 数字分、承诺 description 带来排名提升，或把跳出率/社交互动当已验证的排名惩罚。CWV 使用 LCP/INP/CLS，真实用户与实验室数据分开。Google 自 2026 年 5 月 7 日起不再展示 FAQ 富媒体结果，不会建议为了这种展示新增 FAQ 标记。[官方依据](docs/SIX-DIMENSION-METHOD.md#official-reference-checks)。

[Harbor 原有执行案例](cases/fictional-harbor/)、[业务问答案例](cases/fictional-context-intake/HANDOFF.md)及[六维度样本](cases/six-dimension/)均明确为虚构测试，不是客户成绩或独立人工批准。v0.1/v0.2 历史证据保留。测试只能证明有限规则的行为，不能证明排名、流量或收入提升。

所有者已批准本次干净快照公开；见[发布来源记录](PUBLICATION.md)与保留的[人工审核清单](REVIEW_BEFORE_PUBLIC.md)。新增内容许可仍待选择，公开可读不表示授予新增许可。真实网站报告、页面原文和客户背景应保存在另行获准的私有工作目录。

地图与网站目的问答：[四个实际执行的虚构报告案例及独立复核](cases/google-maps/REVIEW.md)。完整回归通过 228 项测试；测试不代表已实时访问 Google 商家账号或验证浏览器地图渲染。
