# READMEWriter evaluations

这里提供七个合成工程夹具：iOS App、CLI、Python Library、Embedded Firmware、Model Benchmark、Browser Extension 与 Agent Skill。它们用于检验从有限证据选择措辞的能力，不是可发布产品，也不保证可构建。

每个目录包含：

- `fixture/`：项目事实和有意包含问题的起始 README。
- `prompt.md`：给予待评估 Agent 的任务。
- `case.json`：分类、起始 lint 预期、关键 claim id 与语义评分标准。
- `reference.md` / `reference.evidence.json`：本次由实现 Agent 编写并检查的参考结果，用于测试评估管线，不是独立模型运行结果。

## 自动回归

从 READMEWriter 根目录运行：

```sh
python3 -m unittest discover -s tests -v
python3 scripts/run_evals.py --output evals/results/reference-integrity.json
```

运行器把每个 fixture 复制到临时目录，检查起始 README 应当报错，再放入参考结果，检查 lint、证据引用、摘录与哈希。不会执行夹具源码，也不会调用模型。报告明确标注 `model_invoked: false` 和 `semantic_review: not_run`。

这证明输入能暴露结构错误、参考结果与证据记录自洽；不证明 Agent 在未知项目上能自主完成任务。

## 独立生成评估

1. 将每个 `fixture/` 复制到隔离目录，向待评估 Agent 提供当前技能和对应 `prompt.md`。不给它参考结果、`case.json` 或预期答案。禁止改动证据源文件。
2. 保存输出到 `candidate-root/CASE/README.md` 与 `candidate-root/CASE/evidence.json`。记录模型、技能版本、时间与运行条件；失败或缺失文件也保留，不挑选最好的一次。
3. 执行下列命令。`candidate-root` 是实际输出根目录，不是本仓库自带文件。

```sh
python3 scripts/run_evals.py --candidates candidate-root --output evals/results/candidate-integrity.json
```

4. 评审者使用各 case 的 rubric，将每条标为 pass / fail / uncertain，并说明对应正文与来源。重点审查未登记到 evidence.json 的强断言，不能仅检查主声明。`uncertain` 不能计作通过。
5. 汇总结构检查和语义评审两类结果，单独记录主观可读性；若比较技能前后效果，使用相同模型、输入和评审标准。不要把作者编写的参考结果称为盲测。

当前运行器不自动判断所有自然语言声明是否成立；语义评分需要 Agent 或人工逐条检查。报告不计算一个掩盖这些差异的总通过率。
