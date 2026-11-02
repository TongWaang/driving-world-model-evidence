# 中文使用说明

本材料包对应论文《A Critical Review of Evaluation Evidence for Autonomous Driving World Models》的 Revision 4。包括 17 个系统、35 条任务和输入变体记录、四组论文内数值对照、英文补充材料 S1，以及本次新编写的验证代码。

## 从哪里查询

- 阅读 `S1.md`：查看分类规则、来源版本、任务变体、证据状态和数值出处。
- 阅读 `S1.pdf`：用于离线阅读或作为投稿补充文件。
- 查看 `../data/evidence_register.json`：读取完整机器可读记录。
- 查看 `../data/numerical_contrasts.json`：核对表 5 与图 2 所用四组对照的数值、条件、单位和出处。
- 查看 `../reports/validation_report.json`：查看算例计算、数值变化和边界检查结果。

## 如何运行

安装 Python 3.10 或更新版本后，在仓库根目录执行：

```bash
python scripts/validate.py
python scripts/query.py --study GenAD
python scripts/query.py --validation reactive_simulation
python scripts/query.py --status NR --text intervention
```

验证与查询只使用 Python 标准库，无需安装深度学习框架。重新生成 S1 PDF 才需要可选依赖 ReportLab。

## 应如何解释

D 表示直接测试所指定的终点，不等于实验质量很高；P 表示代理或选定定性证据；X 表示测试的是其他终点，不等于没有该能力；NR 表示所检查材料中尚未解决，不等于负结果。记录明确区分原论文报告的终点和本综述额外提出的更强用途问题。

这些附件是根据当前主文和本次定向来源核查重新整理的，脚本也是本次新编写的。不能将其描述为恢复了未提供的原始历史记录，或已经完成独立双人编码、新驾驶实验及道路验证。

## 与主文衔接

建议在第 2.3 节明确附件的实际文件名和公开链接，并如实交代整理时间与单一 AI 辅助工作流。表 5 和图 2 中 LAW 的描述应改为“以视觉潜变量和预测轨迹为条件的未来潜变量预测”；视觉潜变量与预测轨迹是输入条件。

主文引用正式论文，而本附件部分检查的是明确冻结版本的作者预印本；以 `sources.json` 中的 inspected_version 和 inspected_url 为准。WorldRFT 的 Table 11 位于含附录的 arXiv 版本。公开仓库提供的是当前 17 系统样本的配套材料，不代表已经补完全部文献覆盖或解决投稿前评价报告中的其他问题。
