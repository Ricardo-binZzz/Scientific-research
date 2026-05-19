from __future__ import annotations

import json
from pathlib import Path


DEFAULT_DIRECTORIES = [
    "data",
    "exports",
    "figures",
    "literature",
    "manuscript",
    "notes",
    "simulation",
    "templates",
]

DEFAULT_TEMPLATE_CONTENT = {
    "search-log.md": "# Search Log\n",
    "paper-summary.md": "# Paper Summary\n",
    "outline.md": "# Outline\n",
    "literature-review.md": "# Literature Review\n",
    "figure-spec.md": "# Figure Spec\n",
    "sim-runbook.md": "# Simulation Runbook\n",
    "simulation-metadata.json": "{\n  \"columns\": {\n    \"time\": \"s\",\n    \"stress\": \"MPa\"\n  }\n}\n",
}


def bootstrap_workspace(base_dir: Path, *, project_slug: str, project_name: str) -> Path:
    root = base_dir / project_slug
    root.mkdir(parents=True, exist_ok=True)
    for name in DEFAULT_DIRECTORIES:
        (root / name).mkdir(exist_ok=True)
    _write_readme(root / "README.md", project_name=project_name, project_slug=project_slug)
    _write_templates(root / "templates")
    _write_library_index(root / "literature")
    _write_project_check_config(root / "project-check.json")
    _write_literature_tracker(root / "literature-tracker.json")
    return root


def _write_readme(path: Path, *, project_name: str, project_slug: str) -> None:
    content = (
        f"# {project_name}\n\n"
        f"Project slug: {project_slug}\n\n"
        "## Layout\n\n"
        "- literature: PDFs and metadata\n"
        "- notes: summary cards and reading notes\n"
        "- manuscript: writing drafts and exports\n"
        "- figures: generated figures\n"
        "- simulation: solver inputs and outputs\n"
        "- templates: reusable working templates\n"
    )
    path.write_text(content, encoding="utf-8")


def _write_templates(template_dir: Path) -> None:
    template_dir.mkdir(exist_ok=True)
    for name, content in DEFAULT_TEMPLATE_CONTENT.items():
        (template_dir / name).write_text(content, encoding="utf-8")


def _write_library_index(literature_dir: Path) -> None:
    literature_dir.mkdir(exist_ok=True)
    index_path = literature_dir / "library-index.json"
    if not index_path.exists():
        index_path.write_text("{\n  \"entries\": []\n}\n", encoding="utf-8")


def _write_project_check_config(path: Path) -> None:
    if path.exists():
        return
    payload = {
        "manuscript": {
            "required_sections": ["Introduction", "Method"],
            "expected_figures": ["Figure 1"],
        },
        "simulation": {
            "required_columns": ["time", "stress"],
            "numeric_columns": ["time", "stress"],
            "metadata": "templates/simulation-metadata.json",
            "ranges": {
                "stress": [0, 1000],
            },
        },
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_literature_tracker(path: Path) -> None:
    if path.exists():
        return
    payload = {
        "topics": [
            {
                "name": "Adaptive fixtures",
                "keywords": ["adaptive fixture", "clamping force optimization"],
                "sources": ["Google Scholar", "Web of Science", "Scopus"],
                "last_checked": "",
            }
        ]
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
