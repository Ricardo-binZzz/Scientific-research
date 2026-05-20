const statusText = document.getElementById("statusText");
const resultMeta = document.getElementById("resultMeta");
const output = document.getElementById("output");
const projectRoot = document.getElementById("projectRoot");
const toast = document.getElementById("toast");
const insightPanel = document.getElementById("insightPanel");
const actionButtons = Array.from(document.querySelectorAll("button[data-action]"));
const storageKey = "researchWorkflow.projectRoot";
const demoProjectRoot = String.raw`C:\Users\22676\Documents\科研\examples\demo-project`;

function valueOf(id) {
  const element = document.getElementById(id);
  return element ? element.value : "";
}

function checkedValueOf(id) {
  const element = document.getElementById(id);
  return element && element.checked ? "true" : "false";
}

function setBusy(button, busy) {
  actionButtons.forEach((item) => {
    item.disabled = busy;
  });
  if (button) button.disabled = busy;
  statusText.textContent = busy ? "运行中" : "就绪";
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("visible");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.remove("visible"), 2600);
}

async function runAction(action, button) {
  const payload = {
    action,
    base_dir: valueOf("baseDir"),
    project_slug: valueOf("projectSlug"),
    project_name: valueOf("projectName"),
    project_root: valueOf("projectRoot"),
    query: valueOf("libraryQuery"),
    since_year: valueOf("sinceYear"),
    source_query: valueOf("sourceQuery"),
    csv_path: valueOf("csvPath"),
    title: valueOf("title"),
    authors: valueOf("authors"),
    year: valueOf("year"),
    source: valueOf("source"),
    doi: valueOf("doi"),
    pdf_name: valueOf("pdfName"),
    note_path: valueOf("notePath"),
    abstract: valueOf("abstract"),
    keywords: valueOf("keywords"),
    url: valueOf("url"),
    database_source: valueOf("databaseSource"),
    citation_count: valueOf("citationCount"),
    summary_title: valueOf("summaryTitle"),
    summary_authors: valueOf("summaryAuthors"),
    summary_source: valueOf("summarySource"),
    summary_year: valueOf("summaryYear"),
    summary_doi: valueOf("summaryDoi"),
    summary_problem: valueOf("summaryProblem"),
    summary_method: valueOf("summaryMethod"),
    summary_data: valueOf("summaryData"),
    summary_key_figures: valueOf("summaryKeyFigures"),
    summary_main_result: valueOf("summaryMainResult"),
    summary_limitation: valueOf("summaryLimitation"),
    summary_reuse_value: valueOf("summaryReuseValue"),
    summary_source_pages: valueOf("summarySourcePages"),
    search_question: valueOf("searchQuestion"),
    search_keywords: valueOf("searchKeywords"),
    search_query: valueOf("searchQuery"),
    search_source: valueOf("searchSource"),
    search_date: valueOf("searchDate"),
    search_filters: valueOf("searchFilters"),
    search_result_count: valueOf("searchResultCount"),
    search_notes: valueOf("searchNotes"),
    data_path: valueOf("dataPath"),
    required_columns: valueOf("requiredColumns"),
    numeric_columns: valueOf("numericColumns"),
    figure_data_path: valueOf("figureDataPath"),
    figure_out_dir: valueOf("figureOutDir"),
    figure_stem: valueOf("figureStem"),
    figure_title: valueOf("figureTitle"),
    figure_type: valueOf("figureType"),
    x_column: valueOf("xColumn"),
    y_columns: valueOf("yColumns"),
    y_error_columns: valueOf("yErrorColumns"),
    value_column: valueOf("valueColumn"),
    x_label: valueOf("xLabel"),
    y_label: valueOf("yLabel"),
    figure_width_mm: valueOf("figureWidthMm"),
    figure_height_mm: valueOf("figureHeightMm"),
    x_min: valueOf("xMin"),
    x_max: valueOf("xMax"),
    y_min: valueOf("yMin"),
    y_max: valueOf("yMax"),
    show_legend: checkedValueOf("showLegend"),
    show_grid: checkedValueOf("showGrid"),
    palette: valueOf("palette"),
    title_font_size: valueOf("titleFontSize"),
    label_font_size: valueOf("labelFontSize"),
    tick_font_size: valueOf("tickFontSize"),
    line_width: valueOf("lineWidth"),
    tick_count: valueOf("tickCount"),
    manuscript_path: valueOf("manuscriptPath"),
    required_sections: valueOf("requiredSections"),
    expected_figures: valueOf("expectedFigures"),
    report_kind: valueOf("reportKind"),
  };

  output.classList.remove("empty-state");
  output.textContent = "运行中...";
  resultMeta.textContent = button ? button.textContent.trim() : action;
  setBusy(button, true);

  try {
    const response = await fetch("/action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const responseText = await response.text();
    output.textContent = responseText;
    renderResultCompanion(action, response.ok, responseText);
    statusText.textContent = response.ok ? "完成" : "需要处理";
    if (response.ok && action === "scan_project_files") {
      applySuggestedPaths(responseText);
    }
    showToast(response.ok ? "操作完成" : "操作返回问题，请查看结果");
    document.getElementById("resultPanel").scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch (error) {
    output.textContent = "请求失败：" + error;
    renderResultCompanion(action, false, "");
    statusText.textContent = "请求失败";
    showToast("请求失败");
  } finally {
    actionButtons.forEach((item) => {
      item.disabled = false;
    });
  }
}

actionButtons.forEach((button) => {
  button.addEventListener("click", () => runAction(button.dataset.action, button));
});

document.getElementById("clearOutput").addEventListener("click", () => {
  output.classList.add("empty-state");
  output.textContent = "结果已清空。选择一个操作继续。";
  hideInsightPanel();
  resultMeta.textContent = "等待操作";
  statusText.textContent = "就绪";
});

document.getElementById("copyOutput").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(output.textContent);
    showToast("结果已复制");
  } catch (error) {
    showToast("复制失败，请手动选择结果文本");
  }
});

document.getElementById("downloadOutput").addEventListener("click", () => {
  const blob = new Blob([output.textContent], { type: "text/markdown;charset=utf-8" });
  const link = document.createElement("a");
  const timestamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-");
  link.href = URL.createObjectURL(blob);
  link.download = `workflow-result-${timestamp}.md`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(link.href);
  showToast("结果已下载");
});

document.querySelectorAll("[data-scroll-output]").forEach((button) => {
  button.addEventListener("click", () => {
    document.getElementById("resultPanel").scrollIntoView({ behavior: "smooth" });
  });
});

const rememberedRoot = window.localStorage.getItem(storageKey);
if (rememberedRoot && projectRoot && !projectRoot.value) {
  projectRoot.value = rememberedRoot;
}

if (projectRoot) {
  projectRoot.addEventListener("input", () => {
    window.localStorage.setItem(storageKey, projectRoot.value);
  });
}

function setValue(id, value) {
  const element = document.getElementById(id);
  if (element && !element.value) element.value = value;
}

function setChecked(id, value) {
  const element = document.getElementById(id);
  if (element) element.checked = value;
}

function forceValue(id, value) {
  const element = document.getElementById(id);
  if (element && value) element.value = value;
}

function applySuggestedPaths(text) {
  const map = {
    data_path: "dataPath",
    figure_data_path: "figureDataPath",
    figure_out_dir: "figureOutDir",
    manuscript_path: "manuscriptPath",
    csv_path: "csvPath",
  };
  let applied = 0;
  text.split(/\r?\n/).forEach((line) => {
    const match = line.match(/^-\s+([a-z_]+):\s+(.+)$/);
    if (!match || !map[match[1]]) return;
    forceValue(map[match[1]], match[2].trim());
    applied += 1;
  });
  if (applied > 0) {
    showToast("已自动填充可用路径");
  }
}

function renderResultCompanion(action, ok, text) {
  if (action === "literature_insights" && ok) {
    renderLiteratureInsights(text);
    return;
  }
  if (action === "scan_project_files" && ok) {
    renderProjectFileScan(text);
    return;
  }
  if (action.startsWith("simulation_") && ok) {
    renderSimulationReport(action, text);
    return;
  }
  if (action === "figure_from_data" && ok) {
    renderFigureResult(text);
    return;
  }
  if (action === "save_standard_report" && ok) {
    renderSavedReportResult(text);
    return;
  }
  if ((action === "note_paper_summary" || action === "note_search_log") && ok) {
    renderNoteResult(action, text);
    return;
  }
  if ((action === "library_stats" || action === "library_check_pdfs" || action === "library_check_notes") && ok) {
    renderLibraryAssetReport(action, text);
    return;
  }
  if (["writing_dashboard", "literature_map", "literature_table", "literature_tracker", "writing_pack"].includes(action) && ok) {
    renderPlanningReport(action, text);
    return;
  }
  if (action.startsWith("library_") && ok) {
    renderLibraryResult(action, text);
    return;
  }
  if (action === "workflow_status" && ok) {
    renderWorkflowStatus(text);
    return;
  }
  if (action === "project_report" && ok) {
    renderProjectReport(text);
    return;
  }
  if (action === "init_project" && ok) {
    renderProjectInitResult(text);
    return;
  }
  if (action === "project_check" && ok) {
    renderProjectCheck(text);
    return;
  }
  if (action === "manuscript_check" && ok) {
    renderManuscriptCheck(text);
    return;
  }
  renderResultFallback(action, ok, text);
}

function hideInsightPanel() {
  if (!insightPanel) return;
  insightPanel.hidden = true;
  insightPanel.innerHTML = "";
}

function renderResultFallback(action, ok, text) {
  if (!insightPanel) return;
  const advice = resultFallbackAdvice(action, ok, text);
  const target = fallbackTargetForAction(action);
  insightPanel.innerHTML = `
    <div class="insight-title">
      <div>
        <h3>${ok ? "操作已完成" : "操作需要处理"}</h3>
        <p>${escapeHtml(advice.description)}</p>
      </div>
    </div>
    <div class="result-fallback-card ${ok ? "ready" : "todo"}">
      <div>
        <span>当前操作</span>
        <strong>${escapeHtml(advice.actionLabel)}</strong>
      </div>
      <div>
        <span>${ok ? "下一步" : "优先检查"}</span>
        <p>${escapeHtml(advice.nextStep)}</p>
      </div>
      ${target ? `<button class="workflow-jump-button" type="button" data-target-section="${escapeHtml(target)}">去对应区域</button>` : ""}
      <p>完整原始结果仍在下方，可以复制或下载保存。</p>
    </div>
  `;
  insightPanel.hidden = false;
}

function resultFallbackAdvice(action, ok, text) {
  const labels = {
    project_report: "项目总览",
    project_check: "项目体检",
    workflow_status: "流程状态",
    scan_project_files: "扫描可用文件",
    init_project: "创建课题",
    figure_from_data: "生成 SVG 图",
    manuscript_check: "检查稿件",
  };
  if (ok) {
    return {
      actionLabel: labels[action] || action,
      description: "这个操作暂时没有专属概览卡片，但已经返回结果。",
      nextStep: "先看下方原始结果；如果要保存，可用复制或下载按钮。",
    };
  }
  const lowered = (text || "").toLowerCase();
  let nextStep = "先检查项目根目录、输入路径和必填字段是否正确。";
  if (lowered.includes("项目根目录")) nextStep = "先填写项目根目录，或点击“加载示例课题”确认网页能正常运行。";
  if (lowered.includes("no such file") || lowered.includes("找不到") || lowered.includes("不存在")) {
    nextStep = "先确认文件路径真实存在；也可以点击“扫描可用文件”自动填入常见路径。";
  }
  if (lowered.includes("required") || lowered.includes("必填")) nextStep = "先补齐当前功能区里的必填字段，再重新运行。";
  return {
    actionLabel: labels[action] || action,
    description: "操作没有完成。上方先给出最可能的处理方向，下方保留原始错误文本。",
    nextStep,
  };
}

function fallbackTargetForAction(action) {
  if (action.startsWith("library_") || action === "literature_insights") return "library";
  if (action.startsWith("note_")) return "notes";
  if (action.startsWith("simulation_")) return "simulation";
  if (action === "figure_from_data") return "figures";
  if (action === "manuscript_check") return "manuscript";
  return "overview";
}

function renderLiteratureInsights(text) {
  if (!insightPanel) return;
  const coverage = parseMarkdownListSection(text, "Coverage");
  const keywords = parseMarkdownListSection(text, "Top Keywords");
  const databases = parseMarkdownListSection(text, "Databases");
  const cited = parseMarkdownListSection(text, "High Citation Literature");
  const abstracts = parseMarkdownListSection(text, "Abstract-ready Literature");
  const total = valueAfterLabel(coverage, "Total entries");
  const abstractReady = valueAfterLabel(coverage, "Abstract-ready entries");
  const highCitation = valueAfterLabel(coverage, "High-citation candidates");
  const missingPdfs = valueAfterLabel(coverage, "Missing PDFs");
  const missingNotes = valueAfterLabel(coverage, "Missing notes");

  insightPanel.innerHTML = `
    <div class="insight-title">
      <div>
        <h3>文献洞察</h3>
        <p>摘要覆盖、资料缺口和重点文献的快速视图。</p>
      </div>
    </div>
    <div class="insight-grid">
      ${insightMetric("文献总数", total)}
      ${insightMetric("已有摘要", abstractReady)}
      ${insightMetric("高引用候选", highCitation)}
      ${insightMetric("缺 PDF / 笔记", `${missingPdfs || "0"} / ${missingNotes || "0"}`)}
    </div>
    <div class="insight-columns">
      ${renderInsightList("关键词排行", keywords, "keyword-pill")}
      ${renderInsightList("数据库来源", databases, "source-pill")}
      ${renderInsightList("高引用文献", cited, "rank-list")}
      ${renderInsightList("已有摘要文献", abstracts, "rank-list")}
    </div>
  `;
  insightPanel.hidden = false;
}

function renderProjectFileScan(text) {
  if (!insightPanel) return;
  const suggestions = parseSuggestedPaths(text);
  const groups = [
    ["仿真数据", "dataPath", suggestions.data_path],
    ["绘图数据", "figureDataPath", suggestions.figure_data_path],
    ["图表输出", "figureOutDir", suggestions.figure_out_dir],
    ["稿件检查", "manuscriptPath", suggestions.manuscript_path],
    ["文献 CSV", "csvPath", suggestions.csv_path],
  ].filter((item) => item[2]);

  insightPanel.innerHTML = `
    <div class="insight-title">
      <div>
        <h3>路径助手</h3>
        <p>扫描结果已自动填入第一批可用路径，也可以点下面的按钮重新填入对应表单。</p>
      </div>
    </div>
    <div class="path-grid">
      ${
        groups.length
          ? groups.map(([label, targetId, path]) => renderPathCard(label, targetId, path)).join("")
          : '<div class="path-empty">没有找到可自动填入的路径。</div>'
      }
    </div>
  `;
  insightPanel.hidden = false;
}

function renderWorkflowStatus(text) {
  if (!insightPanel) return;
  const steps = parseWorkflowSteps(text);
  const gaps = parseMarkdownListSection(text, "Current Gaps");
  const nextActions = parseMarkdownListSection(text, "Next recommended action");
  const readyCount = steps.filter((step) => step.ready).length;
  const nextAction = nextActions[0] || "Run project check and fix reported gaps.";

  insightPanel.innerHTML = `
    <div class="insight-title">
      <div>
        <h3>任务向导</h3>
        <p>按推荐顺序推进课题，先补最影响下一步的缺口。</p>
      </div>
    </div>
    <div class="next-action-card">
      <span>下一步建议</span>
      <strong>${escapeHtml(nextAction)}</strong>
    </div>
    <div class="workflow-progress">
      <span>${readyCount}/${steps.length || 6} 步已就绪</span>
      <div><i style="width:${steps.length ? Math.round((readyCount / steps.length) * 100) : 0}%"></i></div>
    </div>
    <div class="workflow-step-grid">
      ${steps.map((step, index) => renderWorkflowStep(step, index + 1)).join("")}
    </div>
    <div class="workflow-gap-grid">
      ${gaps.map((gap) => `<div class="workflow-gap-card">${escapeHtml(gap)}</div>`).join("") || '<div class="workflow-gap-card">No gaps reported</div>'}
    </div>
  `;
  insightPanel.hidden = false;
}

function renderWorkflowStep(step, index) {
  const target = workflowTargetForStep(step.name);
  return `
    <div class="workflow-step-card ${step.ready ? "ready" : "todo"}">
      <span>${index}</span>
      <div>
        <strong>${escapeHtml(step.name)}</strong>
        <p>${escapeHtml(step.detail)}</p>
        ${target ? `<button class="workflow-jump-button" type="button" data-target-section="${escapeHtml(target)}">去处理</button>` : ""}
      </div>
    </div>
  `;
}

function workflowTargetForStep(name) {
  const targets = {
    "Project structure": "overview",
    "Literature library": "library",
    "Paper summaries": "notes",
    "Simulation data": "simulation",
    "Figures": "figures",
    "Manuscript draft": "manuscript",
  };
  return targets[name] || "";
}

function parseWorkflowSteps(text) {
  return parseMarkdownListSection(text, "Steps").map((item) => {
    const match = item.match(/^(.+?):\s+(ready|todo)\s+-\s+(.+)$/);
    if (!match) return { name: item, ready: false, detail: "" };
    return { name: match[1], ready: match[2] === "ready", detail: match[3] };
  });
}

function renderSimulationReport(action, text) {
  if (!insightPanel) return;
  const summary = parseTopLevelList(text);
  const rows = parseSimulationReportRows(text);
  const isValidation = action === "simulation_validate";
  const isSummary = action === "simulation_summarize";
  const ok = valueAfterLabel(summary, "OK") || (isValidation ? "False" : "True");
  const missingColumns = valueAfterLabel(summary, "Missing columns") || "None";
  const nonNumeric = valueAfterLabel(summary, "Non-numeric columns") || "None";
  const missingUnits = valueAfterLabel(summary, "Missing unit metadata") || "None";
  const rowsValue = valueAfterLabel(summary, "Rows") || "0";
  const columnsValue = valueAfterLabel(summary, "Columns") || String(rows.length);
  const issueCount = [missingColumns, nonNumeric, missingUnits].filter((value) => value && value !== "None").length;

  insightPanel.innerHTML = `
    <div class="insight-title">
      <div>
        <h3>仿真数据概览</h3>
        <p>先看数据是否可用，再决定是修 CSV、补单位，还是继续画图。</p>
      </div>
    </div>
    <div class="insight-grid">
      ${insightMetric("数据行数", rowsValue)}
      ${insightMetric(isValidation ? "校验状态" : "识别列数", isValidation ? (ok === "True" ? "OK" : "需处理") : columnCount(columnsValue))}
      ${insightMetric("非数字列", nonNumeric === "None" ? "0" : nonNumeric)}
      ${insightMetric("缺口类型", issueCount)}
    </div>
    <div class="simulation-grid">
      <section class="simulation-card ${isValidation && ok !== "True" ? "todo" : "ready"}">
        <h4>${isValidation ? "校验结论" : "数据结构"}</h4>
        <ul>
          <li>缺失列：${escapeHtml(missingColumns)}</li>
          <li>非数字列：${escapeHtml(nonNumeric)}</li>
          <li>缺单位元数据：${escapeHtml(missingUnits)}</li>
        </ul>
      </section>
      <section class="simulation-card">
        <h4>${isSummary ? "数值范围" : "样例/范围"}</h4>
        <ul>
          ${
            rows.length
              ? rows.slice(0, 6).map((row) => `<li>${escapeHtml(row)}</li>`).join("")
              : "<li>没有可展示的表格行</li>"
          }
        </ul>
      </section>
    </div>
  `;
  insightPanel.hidden = false;
}

function parseSimulationReportRows(text) {
  return text
    .split(/\r?\n/)
    .filter((line) => line.includes(" | ") && !line.startsWith("Column |") && !line.startsWith("- "))
    .map((line) => line.trim());
}

function parseTopLevelList(text) {
  const items = [];
  const lines = text.split(/\r?\n/);
  let inTop = false;
  lines.forEach((line) => {
    if (line.startsWith("# ")) {
      inTop = true;
      return;
    }
    if (line.startsWith("## ")) {
      inTop = false;
      return;
    }
    if (inTop && line.startsWith("- ")) items.push(line.slice(2).trim());
  });
  return items;
}

function columnCount(value) {
  if (!value || value === "None") return "0";
  return String(value.split(",").map((item) => item.trim()).filter(Boolean).length);
}

function renderFigureResult(text) {
  if (!insightPanel) return;
  const paths = parseGeneratedPaths(text);
  const figureType = valueOf("figureType") || "trend";
  const size = `${valueOf("figureWidthMm") || "180"} x ${valueOf("figureHeightMm") || "120"} mm`;
  const axes = `${valueOf("xColumn") || "-"} / ${valueOf("yColumns") || "-"}`;
  const ranges = [
    valueOf("xMin") || "auto",
    valueOf("xMax") || "auto",
    valueOf("yMin") || "auto",
    valueOf("yMax") || "auto",
  ].join(" / ");

  insightPanel.innerHTML = `
    <div class="insight-title">
      <div>
        <h3>图形生成结果</h3>
        <p>SVG 可放进论文，JSON 记录参数，便于以后复现。</p>
      </div>
    </div>
    <div class="insight-grid">
      ${insightMetric("图类型", figureType)}
      ${insightMetric("尺寸", size)}
      ${insightMetric("坐标列", axes)}
      ${insightMetric("配色", valueOf("palette") || "default")}
    </div>
    <div class="figure-result-grid">
      <section class="figure-result-card">
        <h4>输出文件</h4>
        <ul>
          ${
            paths.length
              ? paths.map((path) => `<li><code>${escapeHtml(path)}</code></li>`).join("")
              : "<li>没有解析到输出路径</li>"
          }
        </ul>
      </section>
      <section class="figure-result-card">
        <h4>关键参数</h4>
        <ul>
          <li>标题：${escapeHtml(valueOf("figureTitle") || "-")}</li>
          <li>坐标范围：${escapeHtml(ranges)}</li>
          <li>图例/网格：${checkedValueOf("showLegend") === "true" ? "显示" : "隐藏"} / ${checkedValueOf("showGrid") === "true" ? "显示" : "隐藏"}</li>
          <li>字号/线宽：${escapeHtml(valueOf("titleFontSize") || "18")} / ${escapeHtml(valueOf("lineWidth") || "2")}</li>
        </ul>
      </section>
    </div>
  `;
  insightPanel.hidden = false;
}

function parseGeneratedPaths(text) {
  return text
    .split(/\r?\n/)
    .map((line) => line.replace(/^已生成：/, "").trim())
    .filter((line) => line.endsWith(".svg") || line.endsWith(".json"));
}

function renderSavedReportResult(text) {
  if (!insightPanel) return;
  const kind = valueOf("reportKind") || "writing_pack";
  const path = text.replace(/^已保存标准报告：/, "").trim();
  const purpose = savedReportPurpose(kind);

  insightPanel.innerHTML = `
    <div class="insight-title">
      <div>
        <h3>报告已保存</h3>
        <p>下次可以直接打开这个 Markdown 文件继续写作或整理材料。</p>
      </div>
    </div>
    <div class="saved-report-card">
      <div>
        <span>报告类型</span>
        <strong>${escapeHtml(purpose.title)}</strong>
      </div>
      <code>${escapeHtml(path || "未解析到保存路径")}</code>
      <p>${escapeHtml(purpose.description)}</p>
    </div>
  `;
  insightPanel.hidden = false;
}

function savedReportPurpose(kind) {
  const purposes = {
    writing_pack: ["写作素材包", "汇总近期文献、关键词、缺口、图表、仿真数据和稿件草稿。"],
    writing_dashboard: ["写作看板", "按背景、方法、结果和缺口整理当前写作准备情况。"],
    literature_table: ["文献对比表", "把论文摘要卡整理成问题、方法、数据、结论和局限对比。"],
    literature_map: ["文献地图", "按年份、来源、作者、关键词、数据库和高引用文献整理文献格局。"],
    literature_tracker: ["追踪清单", "把需要继续检索的主题转换成下一轮检索建议。"],
  };
  const item = purposes[kind] || ["标准报告", "保存一份可复用的 Markdown 报告。"];
  return { title: item[0], description: item[1] };
}

function renderNoteResult(action, text) {
  if (!insightPanel) return;
  const purpose = noteResultPurpose(action);
  const path = text.replace(/^已生成摘要卡：/, "").replace(/^已生成检索记录：/, "").trim();

  insightPanel.innerHTML = `
    <div class="insight-title">
      <div>
        <h3>笔记已生成</h3>
        <p>新笔记已经写入课题 notes 文件夹，后续报告会自动读取。</p>
      </div>
    </div>
    <div class="note-result-card">
      <div>
        <span>${escapeHtml(purpose.label)}</span>
        <strong>${escapeHtml(purpose.title)}</strong>
      </div>
      <code>${escapeHtml(path || "未解析到笔记路径")}</code>
      <p>${escapeHtml(purpose.next)}</p>
    </div>
  `;
  insightPanel.hidden = false;
}

function noteResultPurpose(action) {
  if (action === "note_search_log") {
    return {
      label: "检索记录",
      title: valueOf("searchQuestion") || "Search log",
      next: "下一步：下载候选 PDF，人工确认相关性，再把有价值的论文加入文献库。",
    };
  }
  return {
    label: "论文摘要卡",
    title: valueOf("summaryTitle") || "Paper summary",
    next: "下一步：把这篇论文加入文献库，并在 note-path 里填写这张摘要卡路径。",
  };
}

function renderLibraryResult(action, text) {
  if (!insightPanel) return;
  const entries = parseLibraryEntries(text);
  const countMatch = text.match(/(?:当前文献库共有|共有)\s+(\d+)\s+条/);
  const total = countMatch ? countMatch[1] : String(entries.length);
  const isSearch = ["library_search", "library_recent", "library_source"].includes(action);
  const title = isSearch ? "文献检索结果" : "文献库已更新";
  const description = isSearch ? "先看命中数量和题名，再决定是否生成摘要卡或加入写作素材。" : "文献条目已经写入本地 library-index.json。";

  insightPanel.innerHTML = `
    <div class="insight-title">
      <div>
        <h3>${title}</h3>
        <p>${description}</p>
      </div>
    </div>
    <div class="insight-grid">
      ${insightMetric(isSearch ? "命中条目" : "当前条目", total)}
      ${insightMetric("查询", libraryActionLabel(action))}
      ${insightMetric("缺 PDF 后续", "check-pdfs")}
      ${insightMetric("缺笔记后续", "check-notes")}
    </div>
    <div class="library-result-card">
      <h4>${isSearch ? "前几条结果" : "下一步"}</h4>
      <ul>
        ${
          entries.length
            ? entries.slice(0, 6).map((entry) => `<li>${escapeHtml(entry)}</li>`).join("")
            : `<li>${escapeHtml(isSearch ? "没有匹配条目" : "建议继续检查 PDF 和摘要卡是否齐全。")}</li>`
        }
      </ul>
    </div>
  `;
  insightPanel.hidden = false;
}

function parseLibraryEntries(text) {
  return text
    .split(/\r?\n/)
    .filter((line) => line.startsWith("- Title: "))
    .map((line) => line.replace("- Title: ", "").trim());
}

function libraryActionLabel(action) {
  const labels = {
    library_add: "添加",
    library_import_csv: "导入 CSV",
    library_search: valueOf("libraryQuery") || "关键词",
    library_recent: `>= ${valueOf("sinceYear") || ""}`,
    library_source: valueOf("sourceQuery") || "来源",
  };
  return labels[action] || action.replace("library_", "");
}

function renderLibraryAssetReport(action, text) {
  if (!insightPanel) return;
  const top = parseTopLevelList(text);
  const present = parseInventorySection(text, "Present");
  const missing = parseInventorySection(text, "Missing");
  const total = valueAfterLabel(top, "Total entries") || "-";
  const missingPdfs = valueAfterLabel(top, "Missing PDFs") || (action === "library_check_pdfs" ? String(missing.length) : "-");
  const missingNotes = valueAfterLabel(top, "Missing notes") || (action === "library_check_notes" ? String(missing.length) : "-");

  insightPanel.innerHTML = `
    <div class="insight-title">
      <div>
        <h3>文献资产概览</h3>
        <p>先看缺 PDF、缺摘要卡和资产列表，再决定补哪些材料。</p>
      </div>
    </div>
    <div class="insight-grid">
      ${insightMetric("文献总数", total)}
      ${insightMetric("缺 PDF", missingPdfs)}
      ${insightMetric("缺笔记", missingNotes)}
      ${insightMetric("已找到资产", present.length)}
    </div>
    <div class="library-asset-grid">
      <section class="library-asset-card ${missing.length ? "todo" : "ready"}">
        <h4>${missing.length ? "缺失项" : "缺失项"}</h4>
        <ul>${(missing.length ? missing : ["没有缺失项"]).slice(0, 8).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
      </section>
      <section class="library-asset-card ready">
        <h4>已找到</h4>
        <ul>${(present.length ? present : ["没有可列出的已找到资产"]).slice(0, 8).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
      </section>
    </div>
  `;
  insightPanel.hidden = false;
}

function parseInventorySection(text, heading) {
  return parseMarkdownListSection(text, heading).filter((item) => item !== "None");
}

function renderPlanningReport(action, text) {
  if (!insightPanel) return;
  const sections = planningReportSections(text);
  const listItems = text.split(/\r?\n/).filter((line) => line.startsWith("- ") || line.startsWith("|")).length;
  const purpose = planningReportPurpose(action);

  insightPanel.innerHTML = `
    <div class="insight-title">
      <div>
        <h3>${escapeHtml(purpose.title)}</h3>
        <p>${escapeHtml(purpose.description)}</p>
      </div>
    </div>
    <div class="insight-grid">
      ${insightMetric("报告区块", sections.length)}
      ${insightMetric("可用条目", listItems)}
      ${insightMetric("建议用途", purpose.use)}
      ${insightMetric("后续", purpose.next)}
    </div>
    <div class="planning-report-card">
      <h4>主要区块</h4>
      <ul>${(sections.length ? sections : ["没有解析到区块"]).slice(0, 8).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
    </div>
  `;
  insightPanel.hidden = false;
}

function planningReportSections(text) {
  return text
    .split(/\r?\n/)
    .filter((line) => line.startsWith("## "))
    .map((line) => line.replace(/^##\s+/, "").trim());
}

function planningReportPurpose(action) {
  const purposes = {
    writing_pack: ["写作素材概览", "把能用于正文写作的文献、笔记、图表、仿真数据和草稿集中起来。", "写正文", "补缺口"],
    writing_dashboard: ["写作看板概览", "快速判断背景、方法、结果和稿件材料是否够用。", "排优先级", "补材料"],
    literature_map: ["文献地图概览", "查看年份、来源、作者、关键词、数据库和高引用文献分布。", "定综述结构", "筛重点"],
    literature_table: ["文献对比表概览", "比较多篇论文的问题、方法、数据、结论、局限和复用价值。", "写综述", "挑证据"],
    literature_tracker: ["追踪清单概览", "把后续检索主题转换成下一轮检索建议。", "继续检索", "记 search-log"],
  };
  const item = purposes[action] || ["规划报告概览", "用于整理当前课题的下一步动作。", "规划", "执行"];
  return { title: item[0], description: item[1], use: item[2], next: item[3] };
}

function renderProjectReport(text) {
  if (!insightPanel) return;
  const metrics = parseProjectReportMetrics(text);
  const libraryEntries = metrics["Library entries"] || "0";
  const noteFiles = metrics["Note files"] || "0";
  const figureBundles = metrics["Figure bundles"] || "0";
  const simulationExports = metrics["Simulation exports"] || "0";
  const manuscriptFiles = metrics["Manuscript files"] || "0";
  const nextStep = projectReportNextStep(metrics);

  insightPanel.innerHTML = `
    <div class="insight-title">
      <div>
        <h3>项目总览</h3>
        <p>把当前课题的文献、笔记、图表、仿真和稿件资产先汇总成一屏。</p>
      </div>
    </div>
    <div class="insight-grid">
      ${insightMetric("文献条目", libraryEntries)}
      ${insightMetric("笔记文件", noteFiles)}
      ${insightMetric("图表包", figureBundles)}
      ${insightMetric("仿真导出 / 稿件", `${simulationExports} / ${manuscriptFiles}`)}
    </div>
    <div class="project-report-card">
      <div>
        <span>项目目录</span>
        <code>${escapeHtml(metrics.Root || valueOf("projectRoot") || "未解析到目录")}</code>
      </div>
      <div>
        <span>下一步建议</span>
        <strong>${escapeHtml(nextStep)}</strong>
      </div>
    </div>
  `;
  insightPanel.hidden = false;
}

function parseProjectReportMetrics(text) {
  const metrics = {};
  parseTopLevelList(text).forEach((item) => {
    const splitAt = item.indexOf(":");
    if (splitAt === -1) return;
    metrics[item.slice(0, splitAt).trim()] = item.slice(splitAt + 1).trim();
  });
  return metrics;
}

function projectReportNextStep(metrics) {
  const numberValue = (label) => Number(metrics[label] || 0);
  if (!numberValue("Library entries")) return "先添加或导入文献，再做文献洞察。";
  if (!numberValue("Note files")) return "给核心论文生成摘要卡，方便后续写作。";
  if (!numberValue("Simulation exports")) return "把仿真 CSV/JSON 放到 simulation 文件夹。";
  if (!numberValue("Figure bundles")) return "用仿真或实验数据生成论文图。";
  if (!numberValue("Manuscript files")) return "在 manuscript 文件夹放入论文草稿，再运行稿件检查。";
  return "运行项目体检，优先处理缺 PDF、缺笔记和稿件问题。";
}

function renderProjectInitResult(text) {
  if (!insightPanel) return;
  const path = parseCreatedProjectPath(text);
  insightPanel.innerHTML = `
    <div class="insight-title">
      <div>
        <h3>课题已创建</h3>
        <p>新课题目录和基础文件夹已经生成，可以直接把它填入项目根目录继续操作。</p>
      </div>
    </div>
    <div class="project-init-card">
      <div>
        <span>新项目路径</span>
        <code>${escapeHtml(path || "未解析到创建路径")}</code>
      </div>
      <button class="path-fill-button" type="button" data-fill-id="projectRoot" data-fill-value="${escapeHtml(path)}">填入项目根目录</button>
      <p>下一步：点击“流程状态”或“扫描可用文件”，再按任务向导补文献、笔记、仿真数据和稿件。</p>
    </div>
  `;
  insightPanel.hidden = false;
}

function parseCreatedProjectPath(text) {
  const match = text.match(/已创建课题：(.+)/);
  return match ? match[1].trim() : text.trim();
}

function renderManuscriptCheck(text) {
  if (!insightPanel) return;
  const citations = parseMarkdownListSection(text, "Citations");
  const figures = parseMarkdownListSection(text, "Figures");
  const issues = parseManuscriptIssues(text);
  const warningCount = issues.filter((issue) => issue.level === "warning").length;
  const infoCount = issues.filter((issue) => issue.level === "info").length;
  const citationIssues = issues.filter((issue) => issue.category === "citation").length;
  const figureIssues = issues.filter((issue) => issue.category === "figure").length;
  const structureIssues = issues.filter((issue) => issue.category === "structure").length;
  const topIssues = issues.slice(0, 6);

  insightPanel.innerHTML = `
    <div class="insight-title">
      <div>
        <h3>稿件检查概览</h3>
        <p>先看严重缺口和高频问题，完整检查报告仍在下方。</p>
      </div>
    </div>
    <div class="insight-grid">
      ${insightMetric("问题总数", issues.length)}
      ${insightMetric("警告 / 提醒", `${warningCount} / ${infoCount}`)}
      ${insightMetric("引用 / 图表", `${citationIssues} / ${figureIssues}`)}
      ${insightMetric("结构问题", structureIssues)}
    </div>
    <div class="manuscript-summary-grid">
      <section class="manuscript-card">
        <h4>已识别内容</h4>
        <ul>
          <li>引用标记：${escapeHtml(citations.length)}</li>
          <li>图号标记：${escapeHtml(figures.length)}</li>
        </ul>
      </section>
      <section class="manuscript-card">
        <h4>优先处理</h4>
        <ul>
          ${
            topIssues.length
              ? topIssues.map((issue) => `<li><span class="issue-chip ${issue.level}">${escapeHtml(issue.label)}</span>${escapeHtml(issue.message)}</li>`).join("")
              : '<li><span class="issue-chip ready">就绪</span>未发现稿件问题</li>'
          }
        </ul>
      </section>
    </div>
  `;
  insightPanel.hidden = false;
}

function parseManuscriptIssues(text) {
  return parseMarkdownListSection(text, "Issues")
    .filter((item) => item !== "None")
    .map((item) => {
      const match = item.match(/^(warning|info):\s+(.+)$/i);
      const level = match ? match[1].toLowerCase() : "info";
      const message = match ? match[2] : item;
      return {
        level,
        label: level === "warning" ? "警告" : "提醒",
        category: manuscriptIssueCategory(message),
        message,
      };
    });
}

function manuscriptIssueCategory(message) {
  const text = message.toLowerCase();
  if (text.includes("citation") || text.includes("reference") || text.includes("library")) return "citation";
  if (text.includes("figure") || text.includes("table") || text.includes("caption")) return "figure";
  if (text.includes("section") || text.includes("heading")) return "structure";
  return "other";
}

function renderProjectCheck(text) {
  if (!insightPanel) return;
  const cards = parseProjectCheckCards(text);
  insightPanel.innerHTML = `
    <div class="insight-title">
      <div>
        <h3>体检概览</h3>
        <p>优先处理有缺口或有问题的模块，完整报告仍在下方。</p>
      </div>
    </div>
    <div class="health-grid">
      ${cards.map((card) => renderHealthCard(card)).join("")}
    </div>
  `;
  insightPanel.hidden = false;
}

function parseProjectCheckCards(text) {
  const literature = parseMarkdownListSection(text, "Literature");
  const simulation = parseMarkdownListSection(text, "Simulation");
  const manuscript = parseMarkdownListSection(text, "Manuscript");
  const summary = parseMarkdownListSection(text, "Project Summary");
  const missingPdfs = valueAfterLabel(literature, "Missing PDFs") || "None";
  const missingNotes = valueAfterLabel(literature, "Missing notes") || "None";
  const simulationIssues = simulation.filter((item) => item !== "None");
  const manuscriptIssues = manuscript.filter((item) => item !== "None");
  return [
    {
      title: "文献",
      status: missingPdfs === "None" && missingNotes === "None" ? "ready" : "todo",
      lines: [`条目 ${valueAfterLabel(literature, "Library entries") || "0"}`, `缺 PDF ${missingPdfs}`, `缺笔记 ${missingNotes}`],
    },
    {
      title: "仿真",
      status: simulationIssues.length ? "todo" : "ready",
      lines: simulationIssues.length ? simulationIssues.slice(0, 3) : ["未发现仿真问题"],
    },
    {
      title: "稿件",
      status: manuscriptIssues.length ? "todo" : "ready",
      lines: manuscriptIssues.length ? manuscriptIssues.slice(0, 3) : ["未发现稿件问题"],
    },
    {
      title: "资产",
      status: "ready",
      lines: summary,
    },
  ];
}

function renderHealthCard(card) {
  return `
    <section class="health-card ${card.status}">
      <div>
        <h4>${escapeHtml(card.title)}</h4>
        <span>${card.status === "ready" ? "就绪" : "需处理"}</span>
      </div>
      <ul>${card.lines.map((line) => `<li>${escapeHtml(line)}</li>`).join("")}</ul>
    </section>
  `;
}

function renderPathCard(label, targetId, path) {
  return `
    <div class="path-card">
      <span>${escapeHtml(label)}</span>
      <code>${escapeHtml(path)}</code>
      <button class="path-fill-button" type="button" data-fill-id="${escapeHtml(targetId)}" data-fill-value="${escapeHtml(path)}">填入</button>
    </div>
  `;
}

function parseSuggestedPaths(text) {
  const suggestions = {};
  text.split(/\r?\n/).forEach((line) => {
    const match = line.match(/^-\s+([a-z_]+):\s+(.+)$/);
    if (match) suggestions[match[1]] = match[2].trim();
  });
  return suggestions;
}

function insightMetric(label, value) {
  return `<div class="insight-card"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value || "0")}</strong></div>`;
}

function renderInsightList(title, items, className) {
  const content = items.length
    ? items.slice(0, 8).map((item) => `<li>${escapeHtml(item)}</li>`).join("")
    : "<li>None</li>";
  return `<section class="insight-section"><h4>${escapeHtml(title)}</h4><ul class="${className}">${content}</ul></section>`;
}

function parseMarkdownListSection(text, heading) {
  const lines = text.split(/\r?\n/);
  const items = [];
  let active = false;
  lines.forEach((line) => {
    if (line === `## ${heading}`) {
      active = true;
      return;
    }
    if (active && line.startsWith("## ")) {
      active = false;
      return;
    }
    if (active && line.startsWith("- ")) {
      items.push(line.slice(2).trim());
    }
  });
  return items.filter((item) => item && item !== "None");
}

function valueAfterLabel(items, label) {
  const prefix = `${label}:`;
  const item = items.find((entry) => entry.startsWith(prefix));
  return item ? item.slice(prefix.length).trim() : "";
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function joinPath(root, child) {
  return root.replace(/[\\/]$/, "") + "\\" + child;
}

function fillCommonPaths() {
  const root = valueOf("projectRoot");
  if (!root) {
    showToast("请先填写项目根目录");
    return;
  }
  setValue("csvPath", joinPath(root, "papers.csv"));
  setValue("dataPath", joinPath(root, "simulation\\fixture-stress.csv"));
  setValue("figureDataPath", joinPath(root, "simulation\\fixture-stress.csv"));
  setValue("figureOutDir", joinPath(root, "figures"));
  setValue("figureStem", "stress-response");
  setValue("figureTitle", "Stress response");
  setValue("xColumn", "time");
  setValue("yColumns", "stress");
  setValue("xLabel", "Time (s)");
  setValue("yLabel", "Stress (MPa)");
  setValue("figureWidthMm", "180");
  setValue("figureHeightMm", "120");
  setValue("palette", "default");
  setValue("titleFontSize", "18");
  setValue("labelFontSize", "15");
  setValue("tickFontSize", "14");
  setValue("lineWidth", "2");
  setValue("tickCount", "5");
  setChecked("showLegend", true);
  setChecked("showGrid", true);
  setValue("manuscriptPath", joinPath(root, "manuscript\\chapter.md"));
  setValue("requiredSections", "Introduction,Method,Results");
  setValue("expectedFigures", "Figure 1");
  showToast("常用路径已填充");
}

document.getElementById("loadDemoProject").addEventListener("click", () => {
  projectRoot.value = demoProjectRoot;
  window.localStorage.setItem(storageKey, demoProjectRoot);
  fillCommonPaths();
  showToast("已加载示例课题");
});

document.getElementById("fillCommonPaths").addEventListener("click", fillCommonPaths);

if (insightPanel) {
  insightPanel.addEventListener("click", (event) => {
    const fillButton = event.target.closest(".path-fill-button");
    if (fillButton) {
      forceValue(fillButton.dataset.fillId, fillButton.dataset.fillValue);
      showToast("路径已填入");
      return;
    }
    const jumpButton = event.target.closest(".workflow-jump-button");
    if (!jumpButton) return;
    const section = document.getElementById(jumpButton.dataset.targetSection);
    if (!section) return;
    section.open = true;
    highlightTargetSection(section);
    section.scrollIntoView({ behavior: "smooth", block: "start" });
    showToast("已跳到对应步骤");
  });
}

function highlightTargetSection(section) {
  section.classList.remove("section-highlight");
  window.requestAnimationFrame(() => {
    section.classList.add("section-highlight");
    window.setTimeout(() => section.classList.remove("section-highlight"), 1800);
  });
}
