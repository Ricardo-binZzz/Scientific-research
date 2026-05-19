const statusText = document.getElementById("statusText");
const resultMeta = document.getElementById("resultMeta");
const output = document.getElementById("output");
const actionButtons = Array.from(document.querySelectorAll("button[data-action]"));

function valueOf(id) {
  const element = document.getElementById(id);
  return element ? element.value : "";
}

function setBusy(button, busy) {
  actionButtons.forEach((item) => {
    item.disabled = busy;
  });
  if (button) button.disabled = busy;
  statusText.textContent = busy ? "运行中" : "就绪";
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
    x_label: valueOf("xLabel"),
    y_label: valueOf("yLabel"),
    manuscript_path: valueOf("manuscriptPath"),
    required_sections: valueOf("requiredSections"),
    expected_figures: valueOf("expectedFigures"),
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
    output.textContent = await response.text();
    statusText.textContent = response.ok ? "完成" : "需要处理";
  } catch (error) {
    output.textContent = "请求失败：" + error;
    statusText.textContent = "请求失败";
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
  resultMeta.textContent = "等待操作";
  statusText.textContent = "就绪";
});

document.querySelectorAll("[data-scroll-output]").forEach((button) => {
  button.addEventListener("click", () => {
    document.getElementById("resultPanel").scrollIntoView({ behavior: "smooth" });
  });
});
