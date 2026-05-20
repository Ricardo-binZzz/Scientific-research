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
  if (action === "workflow_status" && ok) {
    renderWorkflowStatus(text);
    return;
  }
  hideInsightPanel();
}

function hideInsightPanel() {
  if (!insightPanel) return;
  insightPanel.hidden = true;
  insightPanel.innerHTML = "";
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
    section.scrollIntoView({ behavior: "smooth", block: "start" });
    showToast("已跳到对应步骤");
  });
}
