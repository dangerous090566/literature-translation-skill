# Terminology Policy

## Principle

Translate for a Chinese technical reader, not for a dictionary. Preserve English terms when they are standard in the field, when the Chinese rendering is awkward, or when the English term is needed to match code, tables, figures, benchmarks, datasets, or model names.

## Usually Keep English

- backbone
- benchmark
- token
- prompt
- adapter
- agent
- pipeline
- zero-shot / few-shot
- fine-tuning
- end-to-end
- closed-loop / open-loop
- leaderboard
- baseline
- ablation
- checkpoint
- dataset names, model names, method names, repository names

## Often Use Chinese With English On First Mention

- 大语言模型（LLM）
- 视觉语言模型（VLM）
- 视觉-语言-动作模型（VLA）
- 闭环评估（closed-loop evaluation）
- 开环评估（open-loop evaluation）
- 指令微调（instruction fine-tuning）
- 消融实验（ablation study）
- 语言引导自动驾驶（language-guided autonomous driving）
- 端到端自动驾驶（end-to-end autonomous driving）

After first mention, use the shorter form that reads best in context.

## Usually Translate Into Chinese

- introduction: 引言
- related work: 相关工作
- methodology/method: 方法
- experiment: 实验
- result: 结果
- conclusion: 结论
- appendix/supplementary: 附录/补充材料
- route completion: 路线完成率
- driving score: 驾驶分数
- infraction score: 违规分数
- navigation instruction: 导航指令
- notice instruction: 提示指令
- misleading instruction: 误导性指令

## Style Checks

- Do not translate code identifiers, file names, command-line flags, dataset splits, metric abbreviations, or model checkpoints.
- Keep table column names bilingual only when the abbreviation is important, e.g. `驾驶分数（DS）`.
- Avoid over-localizing common AI terms. `backbone` is usually clearer than `骨干网络` in method-comparison tables, while prose may say `LLM backbone` or `模型 backbone`.
- Preserve original capitalization for acronyms such as LLM, VLM, VLA, BEV, RGB, LiDAR, CARLA, DS, RC, and IS.
