# 科研工作流工作台

中文 | [English](README.md)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)
![Tests](https://img.shields.io/badge/tests-unittest-2E7D32)
![License](https://img.shields.io/badge/license-MIT-blue)
![本地优先](https://img.shields.io/badge/local--first-no%20account-2E7D32)
![界面](https://img.shields.io/badge/UI-web%20%2B%20CLI-455A64)

这是一个本地优先的科研工作台，用来管理文献导入、结构化阅读笔记、仿真数据检查、可复现 SVG 图表生成和论文草稿质量检查。

它主要面向机械、制造和工程类科研场景，目标是把 Zotero/Word、仿真软件导出的数据、科研图表和论文写作检查串成一个更稳的本地流程。

![工作流示意图](workflow/web_assets/workflow-guide.svg)

## 为什么做这个项目？

很多科研项目的问题不是“没有工具”，而是材料散在太多地方：论文文件夹、Zotero、阅读笔记、仿真结果、Excel 表格、图表草稿、论文正文各管一段。到写论文或投稿前，常见问题会集中爆发：文献缺摘要、PDF 找不到、仿真列名不统一、图表无法复现、正文引用和参考文献对不上。

这个项目不替代你的判断，也不替代 Zotero、Word、仿真软件和人工阅读。它做的是给科研流程加上可重复的检查点：

- 哪些论文已经收集、总结、引用？
- 哪些 PDF 或阅读笔记还缺失？
- 仿真数据列名是否稳定，数值列是否真的都是数字？
- 关键仿真结果是否超出设定范围？
- 图表是否能从同一份数据和设置重新生成？
- 论文草稿是否缺章节、引用、图号、图注、表注或参考文献？

## 核心能力

| 模块 | 能做什么 |
| --- | --- |
| 文献库 | 添加论文，导入 CSV/BibTeX 元数据，按标题、作者、来源、DOI、摘要、关键词搜索，检查缺失 PDF 和笔记 |
| 阅读笔记 | 生成论文总结卡片和检索记录，方便后续综述和写作 |
| 写作准备 | 生成写作资料包、文献对比表、写作仪表盘、文献地图和后续检索计划 |
| 仿真数据 | 预览标准化列名，统计数值范围，校验必需列和单位元数据，检查超范围数值 |
| 图表生成 | 从 CSV/JSON 生成 SVG/JSON 图表包，支持趋势图、柱状图、误差线图、热力图和等值线图 |
| 论文检查 | 检查 Markdown、纯文本和 DOCX 草稿中的引用、标题层级、图号、图注、表注和参考文献问题 |
| 本地网页 | 不会敲 Python 命令也可以在浏览器里完成常用流程 |

## 快速开始

### 方式 A：本地网页界面

如果你不熟悉命令行，优先用网页：

```powershell
.\start_web.bat
```

启动器会在本机 `127.0.0.1` 打开网页；如果 `8000` 端口被占用，会自动尝试后面的端口，并打开实际可用的网址。

建议第一次这样试：

1. 打开网页。
2. 加载 `examples/demo-project` 示例项目。
3. 点击工作流状态。
4. 扫描项目文件。
5. 运行项目体检。
6. 按页面推荐顺序试文献、仿真、图表和论文检查功能。

网页专用教程：[WEB_GUIDE.md](WEB_GUIDE.md)

### 方式 B：命令行

如果你熟悉命令行，可以使用当前环境里的 Python：

```powershell
$PY='C:\path\to\python.exe'
& $PY -m workflow.cli init C:\path\to\workspace --slug demo-project --name "Demo Project"
```

生成项目体检报告：

```powershell
& $PY -m workflow.cli project check C:\path\to\workspace
```

生成写作资料包：

```powershell
& $PY -m workflow.cli project writing-pack C:\path\to\workspace --out writing-pack.md
```

从仿真数据生成图表：

```powershell
& $PY -m workflow.cli figure from-data simulation/result.csv figures --stem stress-response --title "Stress response" --figure-type trend --x-column time --y-column stress --x-label "Time (s)" --y-label "Stress (MPa)"
```

完整中文新手教程：[USER_GUIDE.md](USER_GUIDE.md)

## 示例项目

可运行示例放在 [examples/demo-project](examples/demo-project)，里面包括：

- 小型文献库
- 论文总结笔记
- 仿真 CSV 数据
- 论文草稿
- 项目体检配置
- 文献追踪计划

建议先用这个示例项目熟悉流程，再迁移到自己的真实课题。

## 项目结构

新建工作区会使用下面的结构：

```text
literature/      论文文件和 library-index.json
notes/           检索记录、论文总结、对比表、文献地图、追踪计划
manuscript/      论文草稿和写作报告
simulation/      仿真导出数据和元数据
figures/         生成的 SVG/JSON 图表包
templates/       可复用 Markdown 模板
project-check.json
literature-tracker.json
```

## 这个项目和普通脚本有什么不同？

- 本地优先：数据保存在普通文件和文件夹里，不需要账号。
- 新手可用：常用功能可以通过本地网页点击完成。
- 可脚本化：同一套功能也能用命令行运行，适合复现和自动化。
- 面向科研流程：文献、仿真、图表和论文检查放在同一套流程里。
- 保留人工判断：工具负责暴露缺口和风险，不替你做黑箱决策。
- 图表可复现：SVG 图表会配套保存 JSON 设置文件。

## 文档入口

- [英文 README](README.md)
- [中文新手教程](USER_GUIDE.md)
- [网页界面专用教程](WEB_GUIDE.md)
- [英文新手教程](USER_GUIDE.en.md)
- [示例说明](examples/README.md)
- [贡献指南](CONTRIBUTING.md)
- [安全策略](SECURITY.md)
- [更新日志](CHANGELOG.md)

## 参与贡献

如果问题或改进建议符合“本地优先科研工作流”的范围，欢迎提交 issue 或 pull request。请优先使用 GitHub issue 模板；如果问题依赖 CSV、Markdown、DOCX 或文献库输入，请提供已经脱敏的最小示例。

提交 PR 前，请先运行测试，并确认没有提交个人路径、密钥、未公开论文内容或私有科研数据。

## 当前限制

- 文献检索和论文下载仍然依赖人工或外部工具。
- DOCX 检查会从 Word XML 中提取文本，但还不检查 Word 样式和版式。
- 等值线图输入必须是完整矩形网格。
- BibTeX 解析重点支持常见 article 字段。

## 验证

```powershell
& $PY -m unittest discover -v
```

## 建议填写的 GitHub About

Description:

```text
Local-first research workflow workbench for literature notes, simulation data checks, publication figures, and manuscript QA.
```

Topics:

```text
research-workflow, reproducible-research, academic-writing, literature-review, manuscript, simulation-data, scientific-figures, local-first, python
```
