# 全科研工作流新手使用教程

Language: [English](USER_GUIDE.en.md) | 中文

本文档面向第一次使用本工作流的人。目标是让你知道：每个文件夹放什么、每一步运行什么命令、什么时候必须人工确认，以及结果应该去哪里找。

请用支持 UTF-8 的编辑器查看和编辑本文档。如果在 Windows PowerShell 里看到乱码，优先确认读取编码是不是 UTF-8。

`USER_GUIDE.md` 是总入口和完整流程教程。网页界面的详细操作单独放在 `WEB_GUIDE.md`，它是“本地网页界面”的主教程；以后网页新增按钮、表单、结果卡片或交互行为，优先更新 `WEB_GUIDE.md`，再按需要同步本文件的总入口说明。

## 1. 这套工具做什么

这套工作流不是直接替你完成整篇论文，而是把科研过程拆成可追踪的步骤：

1. 检索论文并记录检索过程。
2. 下载 PDF 后人工判断是否值得入库。
3. 给论文做摘要卡片，保留可引用的结论、页码和局限。
4. 生成论文提纲、综述段和写作素材。
5. 接收 ANSYS、Abaqus、COMSOL 等软件导出的 CSV/JSON 数据。
6. 检查仿真数据字段、数值和单位。
7. 用 Python 生成论文图，包括折线图、柱状图、误差棒图、热力图和等值线图。
8. 检查论文草稿里的引用、图号、章节和本地文献库覆盖情况。

人工确认点很重要：论文是否可靠、仿真设置是否合理、图是否能进论文，都需要你确认。

## 2. 两个目录不要混淆

当前目录是工具本体：

```text
C:\Users\YourName\Documents\科研
```

以后每个真实课题都建议单独建一个项目目录，例如：

```text
C:\Users\YourName\Documents\fixture-study
```

工具本体负责提供命令；课题目录负责存放论文、笔记、仿真数据和生成的图。

## 3. 不会用 Python 时，先用本地网页界面

如果你不想手敲命令，优先看网页教程：

```text
C:\Users\YourName\Documents\科研\WEB_GUIDE.md
```

它是本项目“本地网页界面”的主教程，专门说明网页怎么打开、先点哪里、结果怎么看、出错后怎么处理。

打开网页的方法很简单：直接双击工具目录里的：

```text
C:\Users\YourName\Documents\科研\start_web.bat
```

它会启动本地网页服务，并打开：

```text
http://127.0.0.1:8000
```

启动脚本会依次查找 `.venv\Scripts\python.exe`、Windows 的 `py` 启动器和 `python` 命令。若提示找不到 Python，请先安装 Python 3.10+，或在工具目录里创建 `.venv`。

如果想减少手动配置，可以先双击工具目录里的 `install_windows.bat`。它会创建本地 `.venv`，检查网页模块，并生成 `Research Workflow Web.bat` 启动器；之后日常使用时双击这个启动器即可。

网页里先填写你的课题目录，例如：

```text
C:\Users\YourName\Documents\fixture-study
```

如果只是想先试用，不想马上新建自己的课题，也可以填写仓库自带示例课题：

```text
C:\Users\YourName\Documents\科研\examples\demo-project
```

网页界面和推荐使用顺序可以先看这张示意图，详细解释见 `WEB_GUIDE.md`：

![科研工作流网页使用顺序示意图](workflow/web_assets/workflow-guide.svg)

第一次打开网页时，建议按这个顺序操作：

1. 填写“项目根目录”，或点击“加载示例课题”先试跑。
2. 点击“流程状态”，先看任务向导告诉你下一步该做什么。
3. 点击“扫描可用文件”，让网页自动填入常见数据、稿件和输出路径。
4. 按任务向导跳到对应功能区，逐步处理文献、笔记、仿真、图表和稿件。
5. 每完成一轮，点击“项目体检”检查还有哪些缺口。

网页会记住项目根目录和最近成功操作，能复制/下载结果，也会在运行中禁用按钮，避免重复提交。结果卡片、必填字段、错误提示、重跑按钮和常用报告保存位置，都以 `WEB_GUIDE.md` 为准。

## 4. 如果要用命令行，先设置 Python

先进入工具目录：

```powershell
cd C:\Users\YourName\Documents\科研
```

设置本环境可用的 Python 路径：

```powershell
$PY='C:\path\to\python.exe'
```

后面所有命令都默认你已经设置了 `$PY`。

可选：如果你想用命令入口而不是每次输入 `-m workflow.cli`，可以在工具仓库目录运行：

```powershell
& $PY -m pip install -e . --no-build-isolation
```

安装后可以使用 `research-workflow` 运行 CLI，或使用 `research-workflow-web` 启动本地网页；不安装也可以继续使用下面的 `$PY -m workflow.cli ...` 命令。

## 5. 10 分钟快速试跑

第一次使用时，先用仓库自带的 `examples` 快速确认工具能跑起来。

检查示例仿真数据：

```powershell
& $PY -m workflow.cli simulation validate-data C:\Users\YourName\Documents\科研\examples\simulation-result.csv `
  --required-column time `
  --required-column stress `
  --numeric-column time `
  --numeric-column stress
```

生成一张示例图：

```powershell
& $PY -m workflow.cli figure from-data C:\Users\YourName\Documents\科研\examples\simulation-result.csv C:\Users\YourName\Documents\科研\examples\output `
  --stem quick-check `
  --title "Quick check" `
  --figure-type trend `
  --x-column time `
  --y-column stress `
  --x-label "Time (s)" `
  --y-label "Stress (MPa)"
```

检查示例稿件：

```powershell
& $PY -m workflow.cli manuscript check C:\Users\YourName\Documents\科研\examples\chapter.md `
  --required-section Introduction `
  --expected-figure "Figure 1"
```

这三步能跑通，说明命令行环境没有问题，再开始创建自己的课题目录。

仓库里还有一个更完整的可试跑课题：

```text
C:\Users\YourName\Documents\科研\examples\demo-project
```

它里面已经放了示例文献库、占位 PDF、论文摘要卡、仿真 CSV、稿件草稿、`project-check.json` 和 `literature-tracker.json`，项目体检从零警告开始。在网页里把“项目根目录”填成这个路径后，可以按顺序点击“流程状态”“扫描可用文件”“项目体检”“文献库统计”“生成文献对比表”“预览数据”“生成 SVG 图”“检查稿件”“保存常用报告”，快速看完整流程。

## 6. 创建一个新课题

示例：创建一个夹具优化课题。

```powershell
& $PY -m workflow.cli init C:\Users\YourName\Documents --slug fixture-study --name "夹具优化研究"
```

生成的目录大致如下：

```text
fixture-study
├── literature    # PDF、文献索引 library-index.json
├── notes         # 检索记录、论文摘要、提纲、综述段
├── manuscript    # 论文草稿
├── simulation    # 仿真软件导出的数据
├── figures       # 生成的论文图
├── templates     # 可复用模板
├── project-check.json  # 一键体检配置
└── literature-tracker.json  # 新文献追踪主题
```

`project-check.json` 记录默认体检规则，例如稿件必须包含哪些章节、预期有哪些图号、仿真数据必须有哪些列、哪些列必须是数字、单位元数据文件在哪里。新手可以先不改它，等课题结构稳定后再调整。
`literature-tracker.json` 记录需要持续检索的研究主题、关键词、数据库来源和上次检索日期。新建课题时会先给出一个示例主题，你可以按自己的方向改成真实关键词。

其中 `simulation.ranges` 可以写仿真结果的合理范围，例如：

```json
{"stress":[0,1000]}
```

这样运行 `project check` 时会自动报告超出范围的仿真结果。

## 7. 记录一次论文检索

在 Google Scholar、Web of Science、Scopus、知网等平台检索后，用命令把检索条件记录下来。

```powershell
& $PY -m workflow.cli note search-log C:\Users\YourName\Documents\fixture-study\notes `
  --question "自适应夹具优化研究" `
  --keyword "adaptive fixture" `
  --keyword "clamping force optimization" `
  --query "adaptive fixture clamping force optimization" `
  --source "Google Scholar" `
  --date "2026-05-18" `
  --filters "2020-2026" `
  --result-count 12 `
  --notes "优先关注机械结构、夹紧力、有限元验证"
```

运行后会在 `notes` 目录生成一份检索记录。

如果你用网页生成检索记录，右侧会显示“笔记已生成”卡片，直接给出新笔记路径和下一步建议。检索记录生成后，建议继续下载候选 PDF，人工确认相关性，再把有价值的论文加入文献库。

## 8. 下载 PDF 后先人工确认

把下载的 PDF 放到：

```text
C:\Users\YourName\Documents\fixture-study\literature
```

入库前先检查：

- 这篇论文是否和课题相关。
- 是否有明确方法、数据、图表或结论。
- 结论是否能被你的论文复用。
- 是否有明显局限或不适用条件。

不建议把所有下载的 PDF 都入库。只把确认有价值的论文加入文献库。

如果想先自动找一批候选文献，可以用 Crossref 开放元数据检索：

```powershell
& $PY -m workflow.cli library discover C:\Users\YourName\Documents\fixture-study\literature --query "adaptive fixture manufacturing" --limit 5
```

确认结果合适后，可以把候选条目合并进本地文献库：

```powershell
& $PY -m workflow.cli library discover C:\Users\YourName\Documents\fixture-study\literature --query "adaptive fixture manufacturing" --limit 5 --merge
```

如果你已经有可以合法访问的 PDF 直链，可以下载到文献目录：

```powershell
& $PY -m workflow.cli library download-pdf C:\Users\YourName\Documents\fixture-study\literature https://example.org/paper.pdf --filename paper.pdf
```

这个功能只使用开放元数据和你提供的直接 PDF 链接，不会绕过出版社权限、学校账号登录或付费墙。下载后建议再运行 `library check-pdfs`，确认文献库里的文件名和本地 PDF 对得上。

## 9. 给论文做摘要卡片

```powershell
& $PY -m workflow.cli note paper-summary C:\Users\YourName\Documents\fixture-study\notes `
  --title "Adaptive clamping fixture design" `
  --author "Zhang" `
  --author "Li" `
  --source "Journal of Manufacturing Systems" `
  --year 2024 `
  --doi "10.1000/example" `
  --problem "传统夹具对复杂零件适应性差" `
  --method "建立自适应夹紧机构并用有限元验证" `
  --data "夹紧力、变形量、应力分布" `
  --key-figures "Fig. 3 结构示意图；Fig. 6 应力云图" `
  --main-result "夹紧变形降低约20%" `
  --limitation "实验样本较少" `
  --reuse-value "可借鉴其夹紧力评价指标" `
  --source-pages "pp. 4-8"
```

摘要卡片要写清楚“结论来自哪几页”，后面写论文时才方便回查。

如果你用网页生成论文摘要卡，右侧会显示“笔记已生成”卡片，直接给出新摘要卡路径。后续在“添加文献”时，可以把这个路径填到 `note-path`，这样 `library check-notes`、写作素材包和写作看板都能识别它。

## 10. 把确认过的论文加入文献库

单篇手动加入：

```powershell
& $PY -m workflow.cli library add C:\Users\YourName\Documents\fixture-study\literature `
  --title "Adaptive clamping fixture design" `
  --author "Zhang" `
  --author "Li" `
  --year 2024 `
  --source "Journal of Manufacturing Systems" `
  --doi "10.1000/example" `
  --pdf-name "adaptive-clamping-fixture-design.pdf" `
  --note-path "notes/paper-summary-adaptive-clamping-fixture-design.md" `
  --keyword "fixture" `
  --keyword "clamping" `
  --url "https://example.com/paper" `
  --database-source "Scopus" `
  --citation-count 12
```

如果你从 Scopus、Web of Science、Crossref 或其他平台导出了论文元数据 CSV，可以批量导入：

```powershell
& $PY -m workflow.cli library import-csv C:\Users\YourName\Documents\fixture-study\literature C:\Users\YourName\Documents\fixture-study\papers.csv
```

CSV 常见列名会自动识别，包括 `Title`、`Article Title`、`Authors`、`Author full names`、`Year`、`Publication Year`、`Source title`、`Publication Name`、`Journal`、`DOI`、`PDF`、`File`、`Notes`、`Note`、`Abstract`、`Keywords`、`Author Keywords`、`URL`、`Link`、`Database`、`Cited by`、`Times Cited`。Scopus 导出的作者全名、作者关键词、链接和引用次数，Web of Science 导出的期刊名、分类和被引次数也会尽量自动匹配。导入时按 DOI 优先、标题其次去重。

本地文献库现在可以保存更多信息：摘要、关键词、论文链接、数据库来源和引用次数。`library search` 不只搜索题名、作者、来源和 DOI，也会搜索摘要、关键词、链接和数据库来源。

平台导出的 CSV 通常没有本地 PDF 文件名，所以导入后 `PDF` 字段可能为空。你可以后续手动整理 `literature` 文件夹里的 PDF 文件名，或用 `library check-pdfs` 检查哪些条目还没有对应 PDF。

查看文献库：

```powershell
& $PY -m workflow.cli library list C:\Users\YourName\Documents\fixture-study\literature
```

如果文献越来越多，可以按题名、作者、来源期刊或 DOI 关键词搜索：

```powershell
& $PY -m workflow.cli library search C:\Users\YourName\Documents\fixture-study\literature "clamping"
```

搜索不区分大小写，适合在写综述、补 PDF 或回查某篇论文时快速定位条目。输出里会列出匹配论文的题名、作者、年份、来源、DOI、PDF 文件名和笔记路径。

如果只想看最近几年的文献，可以按年份过滤：

```powershell
& $PY -m workflow.cli library recent C:\Users\YourName\Documents\fixture-study\literature --since 2020
```

这会列出 `2020` 年及之后发表的条目，适合写研究现状前先筛近期文献。

如果只想看某个期刊或会议来源，可以按来源关键词过滤：

```powershell
& $PY -m workflow.cli library source C:\Users\YourName\Documents\fixture-study\literature "Manufacturing"
```

这会在文献来源字段里查找关键词，适合检查某个期刊、会议或数据库来源下有哪些条目。

如果你用网页做添加、导入或搜索，右侧会先显示文献操作结果卡片。搜索和筛选时先看命中数和前几篇题名；添加和导入后建议继续运行 `library check-pdfs` 和 `library check-notes`，避免后面写作时发现 PDF 或摘要卡缺失。

如果你用网页做文献库统计、缺 PDF 检查或缺笔记检查，右侧会先显示文献资产概览卡片。优先处理“缺失项”卡片里的文件名或笔记路径。

检查 PDF 是否缺失：

```powershell
& $PY -m workflow.cli library check-pdfs C:\Users\YourName\Documents\fixture-study\literature
```

检查摘要卡或阅读笔记是否缺失：

```powershell
& $PY -m workflow.cli library check-notes C:\Users\YourName\Documents\fixture-study\literature
```

`note-path` 通常写成 `notes/xxx.md`。如果文献库目录是课题目录下的 `literature`，工具会到同一个课题目录下的 `notes` 文件夹检查这个文件是否存在。缺笔记的论文建议先补 `paper-summary`，否则后面写综述时很难回查证据。

查看文献库统计：

```powershell
& $PY -m workflow.cli library stats C:\Users\YourName\Documents\fixture-study\literature
```

它会显示文献总数、年份范围、缺失 PDF 数量、缺失笔记数量、来源期刊或会议分布，以及作者分布。写综述或准备投稿前，可以用它快速判断文献库是否太旧、PDF 和摘要卡是否还没补齐、来源或作者是否过于集中。

导出 BibTeX，后续可导入 Zotero：

```powershell
& $PY -m workflow.cli library export-bibtex C:\Users\YourName\Documents\fixture-study\literature C:\Users\YourName\Documents\fixture-study\export.bib
```

也可以把基本 BibTeX 条目导回本地文献库：

```powershell
& $PY -m workflow.cli library import-bibtex C:\Users\YourName\Documents\fixture-study\literature C:\Users\YourName\Documents\fixture-study\export.bib
```

## 11. 生成论文提纲

```powershell
& $PY -m workflow.cli note outline C:\Users\YourName\Documents\fixture-study\notes `
  --topic "自适应夹具优化研究" `
  --problem-statement "复杂零件加工中夹具适应性和夹紧稳定性不足" `
  --section "Introduction:研究背景|现有问题|本文贡献" `
  --section "Method:结构设计|仿真模型|评价指标" `
  --section "Results:夹紧力结果|应力结果|对比分析" `
  --conclusion "提出一种可验证的夹具优化流程"
```

提纲适合先生成，再人工改成自己的章节结构。

## 12. 生成综述段素材

```powershell
& $PY -m workflow.cli note literature-review C:\Users\YourName\Documents\fixture-study\notes `
  --paper "Zhang et al. 2024" `
  --claim "自适应夹具可以降低复杂零件装夹变形" `
  --evidence "作者通过有限元比较了传统夹具和自适应夹具的应力分布" `
  --connection "本文可沿用其夹紧力评价指标，并进一步加入制造约束" `
  --limit "该研究实验样本较少，泛化能力仍需验证"
```

综述段里的每个关键结论都要能回链到论文、页码或摘要卡片。

## 13. 接入仿真数据

从 ANSYS、Abaqus、COMSOL 等软件导出 CSV 或 JSON，放到：

```text
C:\Users\YourName\Documents\fixture-study\simulation
```

CSV 读取时会自动识别一部分常见仿真软件表头，并转换成稳定列名：

- 时间：`Time [s]`、`Step Time`、`t (s)` → `time`
- 应力：`Equivalent Stress [MPa]`、`S: Mises`、`solid.mises (MPa)` → `stress`
- 位移或变形：`Total Deformation [mm]`、`U: Magnitude`、`solid.disp (mm)` → `displacement`
- 反力或载荷：`RF: Magnitude`、`Reaction Force` → `force`
- 温度：`T (K)`、`Temperature` → `temperature`

因此，很多从 ANSYS、Abaqus、COMSOL 直接导出的 CSV，可以先用 `time`、`stress`、`displacement`、`force`、`temperature` 这些标准列名检查和画图。如果某个软件导出的表头暂时没有被识别，就按 CSV 里的原始列名传给命令。

假设导出的文件是：

```text
C:\Users\YourName\Documents\fixture-study\simulation\result.csv
```

先查看工具识别出的列名和前几行数据：

```powershell
& $PY -m workflow.cli simulation inspect-data C:\Users\YourName\Documents\fixture-study\simulation\result.csv --rows 5
```

如果输出里看到：

```text
Columns: time, stress, displacement
```

说明表头已经被识别成标准列名，后续命令就可以直接使用这些列名。

再查看数值列的大致范围：

```powershell
& $PY -m workflow.cli simulation summarize-data C:\Users\YourName\Documents\fixture-study\simulation\result.csv
```

它会列出每个数值列的有效数量、最小值和最大值。若某列既有数字又有坏值，仍会显示数字部分的范围，并在 `Non-numeric columns` 中提醒你这列需要回到原始数据检查。

如果你用网页操作，“预览数据”“汇总数值范围”和“校验数据”会在右侧先显示仿真数据概览卡片。建议顺序是：先预览确认列名，再汇总看数值范围，最后校验必需列和数值列。概览卡片只帮助快速判断，完整 Markdown 报告仍在下方。

如果你的仿真软件已经提供命令行入口，也可以让工具启动外部求解器命令并保存日志。例如：

```powershell
& $PY -m workflow.cli simulation run-command --log C:\Users\YourName\Documents\fixture-study\simulation\solver.log C:\Users\YourName\Documents\fixture-study\simulation -- ansys2024 -b -i solve.inp
```

这只是调用你本机已经安装好的求解器命令，不会替你操作商业软件 GUI。求解完成后，仍然建议导出 CSV/JSON，再继续运行 `inspect-data`、`summarize-data`、`validate-data` 和 `check-ranges`。

如果你已经知道某些结果的合理范围，可以先做范围检查：

```powershell
& $PY -m workflow.cli simulation check-ranges C:\Users\YourName\Documents\fixture-study\simulation\result.csv `
  --range stress:0:500 `
  --range displacement:0:5
```

`--range` 的格式是 `列名:最小值:最大值`，可以重复写多次。报告里的 `Out-of-range` 表示超出范围的行数，`Non-numeric` 表示该列里不能转成数字的单元格数量。

如果里面有 `time` 和 `stress` 两列，再检查数据：

```powershell
& $PY -m workflow.cli simulation validate-data C:\Users\YourName\Documents\fixture-study\simulation\result.csv `
  --required-column time `
  --required-column stress `
  --numeric-column time `
  --numeric-column stress
```

如果有单位元数据文件，例如：

```json
{"columns":{"time":"s","stress":"MPa"}}
```

可以一起检查：

```powershell
& $PY -m workflow.cli simulation validate-data C:\Users\YourName\Documents\fixture-study\simulation\result.csv `
  --required-column time `
  --required-column stress `
  --numeric-column time `
  --numeric-column stress `
  --metadata C:\Users\YourName\Documents\fixture-study\templates\simulation-metadata.json
```

报告里的常见提示：

- `Missing columns`：缺少必要列。
- `Non-numeric columns`：本该是数字的列里有文本或空值。
- `Missing unit metadata`：数值列没有单位记录。
- `Empty unit metadata`：单位字段存在但为空。
- `Extra unit metadata`：元数据里写了数据表不存在的列。

## 14. 生成论文图

### 折线图

适合时间响应、载荷-变形曲线等连续数据：

```powershell
& $PY -m workflow.cli figure from-data C:\Users\YourName\Documents\fixture-study\simulation\result.csv C:\Users\YourName\Documents\fixture-study\figures `
  --stem stress-response `
  --title "Stress response" `
  --figure-type trend `
  --x-column time `
  --y-column stress `
  --x-label "Time (s)" `
  --y-label "Stress (MPa)"
```

### 柱状图

适合不同方案、工况或样本的对比。把 `--figure-type trend` 改成：

```powershell
--figure-type bar
```

### 误差棒图

如果仿真或实验数据里有均值列和误差列，例如 `stress` 与 `stress_sd`：

```powershell
& $PY -m workflow.cli figure from-data C:\Users\YourName\Documents\fixture-study\simulation\result.csv C:\Users\YourName\Documents\fixture-study\figures `
  --stem stress-error `
  --title "Stress response" `
  --figure-type errorbar `
  --x-column time `
  --y-column stress `
  --y-error-column stress_sd `
  --x-label "Time (s)" `
  --y-label "Stress (MPa)"
```

每个 `--y-column` 需要对应一个 `--y-error-column`。

### 热力图和等值线图

如果数据是 `x, y, value` 三列，可以生成二维图：

```powershell
& $PY -m workflow.cli figure from-data C:\Users\YourName\Documents\fixture-study\simulation\grid.csv C:\Users\YourName\Documents\fixture-study\figures `
  --stem temperature-field `
  --title "Temperature field" `
  --figure-type heatmap `
  --x-column x `
  --y-column y `
  --value-column value `
  --x-label X `
  --y-label Y
```

把 `--figure-type heatmap` 改成 `--figure-type contour` 可以生成等值线图。等值线图要求数据形成完整矩形网格。

如果你用网页生成图，“图类型”可以直接选择趋势图、柱状图、误差棒图、热力图或等值线图。误差棒图需要填写“误差列”；热力图和等值线图需要把 `Y 列` 填成 y 坐标列，并填写“数值列”。

网页里还可以调整这些图形参数：

- 图宽、图高，单位是 `mm`；不填时默认是 `180 x 120 mm`。
- `X 最小值`、`X 最大值`、`Y 最小值`、`Y 最大值`，用来固定坐标轴范围；不填则自动按数据范围计算。
- 配色方案：默认科研配色、色盲友好、黑白灰、期刊稳重色。
- 是否显示图例、是否显示网格。
- 标题字号、轴标签字号、刻度字号。
- 线宽和刻度数量。

如果你用命令行，也可以在 `figure from-data` 后面加这些可选参数：

```powershell
--palette colorblind `
--show-legend true `
--show-grid true `
--title-font-size 18 `
--label-font-size 15 `
--tick-font-size 14 `
--line-width 2 `
--tick-count 5
```

常用建议：准备放进论文的图，优先试 `--palette colorblind` 或 `--palette journal`；黑白打印时用 `--palette mono`；如果图太密，可以减少 `--tick-count` 或关闭网格。

生成完成后，如果你用网页操作，右侧会先显示“图形生成结果”卡片。先确认 `.svg` 和 `.json` 路径是否在你的课题 `figures` 文件夹里，再打开 SVG 检查图是否适合放进论文。

输出文件在 `figures` 目录：

```text
figures\stress-response.svg
figures\stress-response.json
```

`.svg` 是图，可以放进论文；`.json` 是图形参数和数据来源记录，方便以后复现。

## 15. 检查论文草稿

把草稿放到：

```text
C:\Users\YourName\Documents\fixture-study\manuscript
```

检查 Markdown、纯文本或基础 `.docx`：

```powershell
& $PY -m workflow.cli manuscript check C:\Users\YourName\Documents\fixture-study\manuscript\chapter.md `
  --required-section Introduction `
  --required-section Method `
  --expected-figure "Figure 1" `
  --library-root C:\Users\YourName\Documents\fixture-study\literature
```

它会检查：

- 文中识别到哪些引用。
- 文中识别到哪些图号。
- 指定章节是否存在。
- 文中引用是否能在本地文献库找到。
- 文献库中是否有未被引用的条目。
- 英文图号是否重复，例如重复出现 `Figure 1`。
- 英文图号是否跳号，例如有 `Figure 1`、`Figure 3` 但缺少 `Figure 2`。
- 中文图号是否跳号，例如有 `图 1`、`图 3` 但缺少 `图 2`。
- Markdown 标题是否跳级，例如从 `#` 直接跳到 `###`。
- 已经出现引用标记时，是否缺少 `References`、`Bibliography` 或 `参考文献` 章节。
- Markdown 标题是否为空，例如只有 `##` 但没有标题文字。
- Markdown 图片附近是否缺少图题，例如图片前后没有 `Figure 1` 或 `图 1`。
- Markdown 表格附近是否缺少表题，例如表格前后没有 `Table 1` 或 `表 1`。
- 参考文献章节是否明显过短，目前少于 3 条参考文献会提示。
- `.docx` 图片或绘图对象是否引用了缺失的嵌入图片文件，或者缺少替代文本。
- `.docx` 是否残留 Word 修订痕迹或批注标记，提交前建议在 Word 里接受/拒绝修订并清理批注。

如果你用网页点击“检查稿件”，右侧会先显示可视化问题概览。新手建议先看上方卡片：优先处理警告数量最多、和引用/图表/章节有关的问题；确认后再看下方完整报告逐条修改。

章节检查支持常见中英文别名。例如配置里要求 `Introduction`，正文标题写 `引言` 或 `绪论` 也会通过；要求 `Method`，标题写 `方法` 或 `研究方法` 也会通过；要求 `Results`，标题写 `结果` 或 `结果与讨论` 也会通过。

引用检查支持单个引用 `[@zhang2024]`，也支持一组引用 `[@zhang2024; @li2023fixture]`。

## 16. 查看项目状态和一键体检

```powershell
& $PY -m workflow.cli project report C:\Users\YourName\Documents\fixture-study
```

它会统计文献、笔记、图、仿真导出和论文草稿数量。

如果想一次性检查整个课题，运行：

```powershell
& $PY -m workflow.cli project check C:\Users\YourName\Documents\fixture-study
```

`project check` 会汇总检查：

- 文献库条目数量。
- 文献库登记的 PDF 是否缺失。
- 文献库登记的摘要卡或阅读笔记是否缺失。
- 仿真 CSV/JSON 是否可读、必要列是否存在、数值列是否真是数字、单位元数据是否完整、数值是否超出 `project-check.json` 里设置的合理范围。
- 稿件是否缺章节、缺图号、缺引用、引用是否能在本地文献库找到、图号是否重复或跳号。
- 当前项目的笔记、图、仿真导出、稿件数量。
- `Next Actions` 会把当前缺口转换成下一步建议，例如先检查缺失 PDF、补摘要卡、复查仿真数据，或重新运行稿件检查。网页里的“项目体检”也会把这些建议单独显示成“下一步建议”卡片；示例课题如果已经干净，会显示 `No immediate fixes needed`。

## 17. 生成写作素材包

```powershell
& $PY -m workflow.cli project writing-pack C:\Users\YourName\Documents\fixture-study --out C:\Users\YourName\Documents\fixture-study\writing-pack.md
```

`writing-pack.md` 会汇总当前课题中可用于写作的文献、笔记、图、仿真结果和论文草稿。开头还会附带文献库概览，包括文献总数、年份范围和缺失 PDF 数量，方便写作前先判断资料是否够用。

素材包还会单独列出：

- `Recent Literature (since 2020)`：2020 年及之后的近期文献，适合写研究现状时优先查看。
- `High Citation Literature`：按引用次数列出优先关注的高引用文献，适合快速挑综述里需要重点阅读的论文。
- `Keyword Coverage`：统计文献关键词出现次数，适合判断当前文献是否覆盖了你的主要研究方向。
- `Abstract Coverage`：列出已经有摘要的文献数量和题名，适合判断哪些条目能直接进入综述筛选。
- `Library Gaps`：缺失的 PDF 和缺失的摘要卡或阅读笔记，适合写作前补材料。
- `Manuscript Drafts`：当前 `manuscript` 文件夹里的 `.md`、`.txt`、`.docx` 草稿。

如果你用本地网页界面，点击“生成写作素材包”也会看到这些内容。

网页右侧会先显示规划报告概览卡片，帮助你快速判断这份素材包主要有哪些区块，再看下方完整报告。

如果只想快速看文献库是否够用，不需要生成完整写作素材包，可以在网页里点击“文献洞察”。它会优先显示摘要覆盖、高引用文献、关键词排行和数据库来源，并用卡片把关键数字放在最上方，适合作为写综述前的快速检查。

## 18. 生成文献对比表

如果你已经为多篇论文生成了 `paper-summary` 摘要卡，可以把这些摘要卡汇总成一张对比表：

```powershell
& $PY -m workflow.cli project literature-table C:\Users\YourName\Documents\fixture-study --out C:\Users\YourName\Documents\fixture-study\literature-table.md
```

`literature-table.md` 会从 `notes` 文件夹里的 `# Paper Summary` 笔记中提取题名、作者、年份、来源、研究问题、方法、数据、主要结论、局限、可复用价值和来源页码。它适合在写综述前快速比较多篇论文的共同点和差异。

如果你用本地网页界面，点击“生成文献对比表”可以直接在网页右侧看到同样的表格。

网页会先显示规划报告概览卡片。对比表适合写综述前使用，先看区块和条目数量，再复制下方 Markdown 表格。

## 19. 生成写作看板

写作看板会把“能直接用于写作的材料”和“还缺什么”放到一起：

```powershell
& $PY -m workflow.cli project writing-dashboard C:\Users\YourName\Documents\fixture-study --out C:\Users\YourName\Documents\fixture-study\writing-dashboard.md
```

它会按背景、方法、结果和草稿整理近期文献数量、摘要卡数量、已有摘要的文献数量、高引用候选文献数量、关键词排行、仿真导出、图表包、稿件文件，以及缺失 PDF、缺失笔记等待补项。写论文前可以先看这份看板，再决定先补文献、补图，还是继续写正文。

## 20. 生成文献地图

文献地图是文本版的文献关系概览：

```powershell
& $PY -m workflow.cli library map C:\Users\YourName\Documents\fixture-study\literature --out C:\Users\YourName\Documents\fixture-study\literature-map.md
```

它会汇总年份分布、来源期刊或会议分布、关键词分布、数据库来源分布、高引用文献、作者分布，以及每个作者对应哪些论文。适合快速判断文献是否集中在某几年、某个来源、某些关键词或某几个作者。

## 21. 生成新文献追踪清单

先打开课题目录里的：

```text
C:\Users\YourName\Documents\fixture-study\literature-tracker.json
```

把里面的 `topics` 改成你的真实研究方向、关键词、检索平台和上次检索日期。然后运行：

```powershell
& $PY -m workflow.cli project literature-tracker C:\Users\YourName\Documents\fixture-study --out C:\Users\YourName\Documents\fixture-study\literature-tracking-plan.md
```

它会把每个主题转换成下一次检索建议，包括检索式、关键词、来源平台和下一步动作。检索完后，建议继续生成 `search-log`，再把有价值的论文加入文献库。

如果你用本地网页界面，可以直接点击“生成写作看板”“生成文献地图”“生成追踪清单”。

这些规划类报告都会先显示规划报告概览卡片，再保留完整 Markdown 报告。建议先看概览卡片判断用途，再决定是补材料、写综述，还是继续检索。

## 22. 推荐的日常使用顺序

每个课题建议按这个顺序推进：

```text
检索论文
→ 记录 search-log
→ 下载 PDF
→ 人工确认是否入库
→ library add 或 library import-csv
→ library search / library stats / library check-pdfs / library check-notes
→ 写 paper-summary
→ literature-table
→ library map
→ 写 outline / literature-review
→ 做仿真并导出 CSV/JSON
→ simulation inspect-data
→ simulation summarize-data
→ simulation check-ranges
→ simulation validate-data
→ figure from-data
→ manuscript check
→ project check
→ project report
→ writing-pack
→ writing-dashboard
→ literature-tracker
```

## 23. 常见问题

### PowerShell 提示找不到 python

使用本文档提供的 `$PY` 路径，不要直接输入 `python`。

### 命令太长怎么办

PowerShell 里反引号 `` ` `` 表示换行。复制本文档的多行命令时，不要删除行尾反引号。

### 文档打开后中文乱码怎么办

请用 UTF-8 查看本文档。例如在 PowerShell 中使用：

```powershell
Get-Content C:\Users\YourName\Documents\科研\USER_GUIDE.md -Encoding UTF8
```

### 生成的图在哪里

在课题目录的 `figures` 文件夹里。

### PDF 检查显示 missing

说明 `library-index.json` 里登记的 `pdf_name` 和实际 PDF 文件名不一致，或者 PDF 没放进 `literature` 文件夹。

### 能不能直接控制仿真软件

现在可以用 `simulation run-command` 调用你本机已经安装好的求解器命令行入口并保存日志；它不控制商业软件 GUI，也不替你配置许可证或模型。推荐流程仍然是：在仿真软件里确认模型和求解设置，必要时用命令行批处理运行，导出 CSV/JSON 后由本工作流检查数据和绘图。

### Word 排版能不能自动检查

现在 `.docx` 除了读取正文文本，还会检查一部分 Word 包结构问题，例如缺少 `styles.xml`、页面边距或页面大小设置缺失、页面宽高属性不完整、页眉/页脚引用的部件缺失、嵌入图片目标文件缺失、脚注/尾注引用目标缺失、正文使用了未定义段落样式、没有检测到 Word 引用/参考文献域、参考文献章节存在但没有 bibliography 域、图片或绘图对象缺少替代文本，以及残留修订痕迹或批注标记。它仍然不能替代 Word 模板审阅或 Zotero 字段人工核对；最终排版仍需在 Word 里确认。
