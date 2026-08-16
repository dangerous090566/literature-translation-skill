# Terminology Policy

Translate for a Chinese technical reader, not for a dictionary. Preserve English when it is the field-standard form, when Chinese is ambiguous or awkward, or when the term must match code, figures, tables, benchmarks, datasets, or model names.

## Decision order

1. Follow a user-supplied glossary or the terminology already established in the target project.
2. Follow terminology used by authoritative Chinese standards or the dominant literature in the field.
3. On first mention, use `中文（English, abbreviation）` when it helps disambiguation.
4. After first mention, use the shortest unambiguous form consistently.
5. Keep English when translating would reduce precision or break alignment with artifacts.

Maintain a task-local term table for long papers with at least: source term, chosen Chinese form, retained abbreviation, context, and exceptions. Search the complete target tree for inconsistent variants before delivery.

## Usually keep English

- backbone, benchmark, token, prompt, adapter, agent, pipeline
- zero-shot, few-shot, fine-tuning, end-to-end
- leaderboard, baseline, ablation, checkpoint
- dataset, model, method, repository, and benchmark names
- source-code identifiers, CLI flags, configuration keys, and metric abbreviations

## Often use Chinese on first mention

- 大语言模型（large language model, LLM）
- 视觉语言模型（vision-language model, VLM）
- 视觉-语言-动作模型（vision-language-action model, VLA）
- 闭环评估（closed-loop evaluation）
- 开环评估（open-loop evaluation）
- 指令微调（instruction fine-tuning）
- 消融实验（ablation study）
- 语言引导自动驾驶（language-guided autonomous driving）
- 端到端自动驾驶（end-to-end autonomous driving）

## Usually translate

- introduction: 引言
- related work: 相关工作
- methodology/method: 方法
- experiment: 实验
- result: 结果
- discussion: 讨论
- conclusion: 结论
- appendix/supplementary material: 附录/补充材料
- route completion: 路线完成率
- driving score: 驾驶分数
- infraction score: 违规分数
- navigation instruction: 导航指令
- notice instruction: 提示指令
- misleading instruction: 误导性指令

## Consistency checks

- Preserve capitalization for acronyms such as LLM, VLM, VLA, BEV, RGB, LiDAR, CARLA, DS, RC, and IS.
- Do not alternate between full-width and half-width forms of the same acronym or unit.
- Keep table column names bilingual only when the English abbreviation is needed for comparison.
- Distinguish similar but non-equivalent terms; do not collapse `accuracy`, `precision`, and `recall` into one Chinese term.
- Keep the same translation across body text, captions, tables, algorithms, and appendices unless the grammatical role requires a documented exception.
