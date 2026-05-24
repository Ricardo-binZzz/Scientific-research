const statusText = document.getElementById("statusText");
const resultMeta = document.getElementById("resultMeta");
const output = document.getElementById("output");
const projectRoot = document.getElementById("projectRoot");
const toast = document.getElementById("toast");
const insightPanel = document.getElementById("insightPanel");
const resultPanel = document.getElementById("resultPanel");
const rerunLastAction = document.getElementById("rerunLastAction");
const actionButtons = Array.from(document.querySelectorAll("button[data-action]"));
const storageKey = "researchWorkflow.projectRoot";
const successHistoryStorageKey = "researchWorkflow.successHistory";
const demoProjectRoot = __DEMO_PROJECT_ROOT_JSON__;
const successHistory = [];
let lastRunnableAction = null;

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
  setRerunBusyState(busy);
  statusText.textContent = busy ? "运行中" : "就绪";
}

function setResultLoading(loading) {
  if (!resultPanel) return;
  resultPanel.classList.toggle("result-loading", loading);
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
  lastRunnableAction = { action, button };
  updateRerunButton(button ? button.textContent.trim() : action);
  setResultLoading(true);
  const validation = validateActionPayload(action, payload);
  if (!validation.ok) {
    output.textContent = validation.message;
    renderResultFallback(action, false, validation.message);
    statusText.textContent = "需要处理";
    setResultLoading(false);
    showToast(validation.message);
    focusMissingField(validation.fieldId);
    document.getElementById("resultPanel").scrollIntoView({ behavior: "smooth", block: "nearest" });
    return;
  }
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
    if (response.ok) {
      updateLastSuccess(action, button ? button.textContent.trim() : action);
    }
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
    setResultLoading(false);
    setBusy(button, false);
  }
}

actionButtons.forEach((button) => {
  button.addEventListener("click", () => runAction(button.dataset.action, button));
});

function validateActionPayload(action, payload) {
  if (actionNeedsProjectRoot(action) && !payload.project_root.trim()) {
    return { ok: false, fieldId: "projectRoot", message: "请先填写项目根目录。" };
  }
  const pathField = actionPrimaryPath(action);
  if (pathField && !payload[pathField].trim()) {
    const fieldId = payloadFieldToElementId(pathField);
    return { ok: false, fieldId, message: `请先填写${fieldLabelForId(fieldId)}。` };
  }
  const extraField = actionSecondaryRequiredField(action, payload);
  if (extraField) {
    const fieldId = payloadFieldToElementId(extraField);
    return { ok: false, fieldId, message: `请先填写${fieldLabelForId(fieldId)}。` };
  }
  return { ok: true, fieldId: "", message: "" };
}

function actionNeedsProjectRoot(action) {
  return !["init_project", "library_add"].includes(action);
}

function actionPrimaryPath(action) {
  const pathFields = {
    library_import_csv: "csv_path",
    simulation_inspect: "data_path",
    simulation_summarize: "data_path",
    simulation_validate: "data_path",
    figure_from_data: "figure_data_path",
    manuscript_check: "manuscript_path",
  };
  return pathFields[action] || "";
}

function actionSecondaryRequiredField(action, payload) {
  if (action !== "figure_from_data") return "";
  if (!payload.figure_out_dir.trim()) return "figure_out_dir";
  if (!payload.figure_stem.trim()) return "figure_stem";
  return "";
}

function payloadFieldToElementId(field) {
  const fields = {
    csv_path: "csvPath",
    data_path: "dataPath",
    figure_data_path: "figureDataPath",
    figure_out_dir: "figureOutDir",
    figure_stem: "figureStem",
    manuscript_path: "manuscriptPath",
  };
  return fields[field] || "";
}

function fieldLabelForId(id) {
  const element = document.getElementById(id);
  const label = element ? document.querySelector(`label[for="${id}"]`) : null;
  return label ? label.textContent.trim() : "必填字段";
}

function focusMissingField(id) {
  const element = document.getElementById(id);
  if (!element) return;
  const section = element.closest("details.action-group");
  if (section) {
    section.open = true;
    highlightTargetSection(section);
  }
  element.focus({ preventScroll: true });
}

document.getElementById("clearOutput").addEventListener("click", () => {
  output.classList.add("empty-state");
  output.textContent = "结果已清空。选择一个操作继续。";
  hideInsightPanel();
  clearResultState();
  resultMeta.textContent = "等待操作";
  statusText.textContent = "就绪";
});

function clearResultState() {
  setResultLoading(false);
  successHistory.splice(0);
  saveSuccessHistory();
  lastRunnableAction = null;
  updateRerunButton("");
}

if (rerunLastAction) {
  rerunLastAction.addEventListener("click", () => {
    if (!lastRunnableAction) return;
    runAction(lastRunnableAction.action, lastRunnableAction.button);
  });
}

function updateRerunButton(label) {
  if (!rerunLastAction) return;
  rerunLastAction.disabled = !label;
  rerunLastAction.textContent = label ? `重跑：${label}` : "重跑上次";
}

function setRerunBusyState(busy) {
  if (!rerunLastAction) return;
  rerunLastAction.disabled = busy || !lastRunnableAction;
}

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

function updateLastSuccess(action, label) {
  if (!resultMeta) return;
  const time = new Date().toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" });
  successHistory.unshift({ action, label: label || action, time });
  successHistory.splice(3);
  saveSuccessHistory();
  resultMeta.innerHTML = lastSuccessSummary(successHistory);
}

function lastSuccessSummary(history) {
  const latest = history[0];
  const previous = history.slice(1);
  return `
    <span class="last-success">
      <span>最近成功</span>
      <strong>${escapeHtml(latest.label)}</strong>
      <em>${escapeHtml(latest.time)}</em>
    </span>
    ${previous.length ? `<span class="success-history">${previous.map((item) => `<span>${escapeHtml(item.label)} ${escapeHtml(item.time)}</span>`).join("")}</span>` : ""}
  `;
}

function loadSuccessHistory() {
  try {
    const stored = window.localStorage.getItem(successHistoryStorageKey);
    if (!stored) return [];
    const parsed = JSON.parse(stored);
    if (!Array.isArray(parsed)) return [];
    return parsed.map(normalizeSuccessHistoryItem).filter(Boolean).slice(0, 3);
  } catch (error) {
    return [];
  }
}

function saveSuccessHistory() {
  try {
    if (!successHistory.length) {
      window.localStorage.removeItem(successHistoryStorageKey);
      return;
    }
    window.localStorage.setItem(successHistoryStorageKey, JSON.stringify(successHistory.slice(0, 3)));
  } catch (error) {
    return;
  }
}

function normalizeSuccessHistoryItem(item) {
  if (!item || typeof item !== "object") return null;
  const action = typeof item.action === "string" ? item.action : "";
  const label = typeof item.label === "string" ? item.label : action;
  const time = typeof item.time === "string" ? item.time : "";
  if (!action || !label || !time) return null;
  return { action, label, time };
}

successHistory.push(...loadSuccessHistory());
if (successHistory.length && resultMeta) {
  resultMeta.innerHTML = lastSuccessSummary(successHistory);
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

document.getElementById("expandAllSections").addEventListener("click", () => {
  setAllActionGroups(true);
  showToast("已展开全部模块");
});

document.getElementById("collapseAllSections").addEventListener("click", () => {
  setAllActionGroups(false);
  showToast("已收起全部模块");
});

function setAllActionGroups(open) {
  document.querySelectorAll("details.action-group").forEach((section) => {
    section.open = open;
  });
}

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
