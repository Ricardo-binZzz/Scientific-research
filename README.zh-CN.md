# 科研工作流

语言：[English](README.md) | 中文

这个仓库是一个面向机械/制造方向科研的半自动化工作流工具，覆盖文献整理、结构化阅读笔记、论文草稿检查、仿真数据校验和科研图表生成。

如果你想看更适合新手的完整中文教程，请阅读 [USER_GUIDE.md](USER_GUIDE.md)。

## 快速开始

在当前环境中建议使用项目记录的 bundled Python：

```powershell
$PY='C:\Users\22676\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $PY -m workflow.cli init C:\path\to\workspace --slug demo-project --name "Demo Project"
```

该命令会创建这些目录：

- `literature`：论文文件和 `library-index.json`
- `notes`：检索记录、论文总结、大纲和综述段落
- `manuscript`：论文草稿材料
- `simulation`：仿真输入/输出记录
- `figures`：生成的 SVG/JSON 图表包
- `templates`：可复用的 Markdown 模板

## 主要流程

1. 记录文献检索过程：

```powershell
& $PY -m workflow.cli note search-log notes --question "Adaptive clamping papers" --keyword "adaptive clamping" --query "adaptive clamping fixture" --source Scopus --date 2026-05-18 --filters "2020-2026" --result-count 12 --notes "Focus on mechanism design."
```

2. 把已阅读论文加入本地文献库：

```powershell
& $PY -m workflow.cli library add literature --title "Adaptive clamping fixture" --author Zhang --author Li --year 2024 --source "Journal of Manufacturing Systems" --doi "10.1000/example" --pdf-name paper.pdf --note-path notes/summary.md
```

检查文献库中记录的 PDF 是否存在：

```powershell
& $PY -m workflow.cli library check-pdfs literature
```

3. 与 Zotero 互通 BibTeX：

```powershell
& $PY -m workflow.cli library export-bibtex literature export.bib
& $PY -m workflow.cli library import-bibtex literature export.bib
```

也可以从 CSV 元数据导入论文信息：

```powershell
& $PY -m workflow.cli library import-csv literature papers.csv
```

CSV 导入器能识别常见字段，例如 `Title`、`Authors`、`Year`、`Source title`、`Journal`、`DOI`、`PDF`/`File`、`Notes`/`Note`。

4. 校验仿真数据：

```powershell
& $PY -m workflow.cli simulation validate-data simulation/result.csv --required-column time --required-column stress --numeric-column time --numeric-column stress
```

加上 `--metadata templates/simulation-metadata.json` 后，还会检查数值列的单位元数据。
元数据报告会提示缺失单位、空单位值，以及数据集中不存在但元数据里多写的列。

5. 从 CSV/JSON 数据生成图表：

```powershell
& $PY -m workflow.cli figure from-data simulation/result.csv figures --stem stress-response --title "Stress response" --figure-type trend --x-column time --y-column stress --x-label "Time (s)" --y-label "Stress (MPa)"
```

可用图表类型包括：

- `bar`：基础柱状图
- `heatmap`：使用 `--x-column`、`--y-column`、`--value-column` 的热力图
- `contour`：完整矩形网格数据的等值线图
- `errorbar`：均值加误差线图，需要匹配的 `--y-error-column`

误差线示例：

```powershell
& $PY -m workflow.cli figure from-data simulation/result.csv figures --stem stress-error --title "Stress response" --figure-type errorbar --x-column time --y-column stress --y-error-column stress_sd --x-label "Time (s)" --y-label "Stress (MPa)"
```

6. 检查论文草稿：

```powershell
& $PY -m workflow.cli manuscript check manuscript/chapter.md --required-section Introduction --required-section Method --expected-figure "Figure 1" --library-root literature
```

7. 输出项目状态报告：

```powershell
& $PY -m workflow.cli project report .
```

8. 生成写作资料包：

```powershell
& $PY -m workflow.cli project writing-pack . --out writing-pack.md
```

## 当前限制

- 文献检索和论文下载仍然依赖人工或外部工具。
- 图表渲染支持折线图、柱状图、误差线图、热力图和等值线图。
- 等值线图输入必须是完整矩形网格。
- DOCX 检查会从 Word XML 中提取文本，但还不检查 Word 样式或版式。
- 论文检查会报告重复的英文图号和跳号问题。
- BibTeX 解析目前支持基础 article 条目和常见字段。

## 验证

```powershell
& $PY -m unittest discover -v
```

## 示例

小型示例输入放在 `examples/`：

- `examples/simulation-result.csv`
- `examples/chapter.md`

查看 [examples/README.md](examples/README.md) 可以看到数据校验、草稿检查和 SVG 图表生成示例。
