// Action payload collection and preflight validation for the local workbench.

function valueOf(id) {
  const element = document.getElementById(id);
  return element ? element.value : "";
}

function checkedValueOf(id) {
  const element = document.getElementById(id);
  return element && element.checked ? "true" : "false";
}

function collectActionPayload(action) {
  return {
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
}

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
