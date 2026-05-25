import unittest

from workflow.mobile_responses import (
    build_mobile_cards,
    build_mobile_summary,
    mobile_response,
)


PROJECT_CHECK_MARKDOWN = """# Project Check Report

## Literature
- Missing PDFs: 1
- Missing notes: 2

## Simulation
- Simulation issues: 0

## Manuscript
- Manuscript issues: 1

## Next Actions
- Fill missing reading notes.
"""


WORKFLOW_STATUS_MARKDOWN = """# Workflow Status

## Current Gaps
- Missing PDFs: 1
- Missing notes: 2
- Simulation issues: 0
- Manuscript issues: 1

## Next recommended action
- Fill missing reading notes.
"""


REALISH_PROJECT_CHECK_MARKDOWN = """# Project Check Report

## Literature
- Missing PDFs: missing.pdf
- Missing PDFs: methods.pdf
- Missing notes: baseline-study.md

## Simulation
- Missing reproducibility seed.
- Simulation output is stale.

## Manuscript
- Abstract still has placeholder text.

## Next Actions
- Attach the missing literature assets.
"""


SINGULAR_GAP_MARKDOWN = """# Project Check Report

## Literature
- Missing PDFs: missing.pdf

## Next Actions
- Attach the missing PDF.
"""


class MobileResponsesTests(unittest.TestCase):
    def test_project_check_summary_uses_soft_next_action_language(self) -> None:
        summary = build_mobile_summary("project_check", PROJECT_CHECK_MARKDOWN)

        self.assertEqual(summary["title"], "Project check complete")
        self.assertEqual(summary["primaryMessage"], "4 items need attention")
        self.assertEqual(summary["nextAction"], "Fill missing reading notes.")

    def test_workflow_status_summary_uses_next_recommended_action(self) -> None:
        summary = build_mobile_summary("workflow_status", WORKFLOW_STATUS_MARKDOWN)

        self.assertEqual(summary["title"], "Workflow status updated")
        self.assertEqual(summary["primaryMessage"], "4 items need attention")
        self.assertEqual(summary["nextAction"], "Fill missing reading notes.")

    def test_build_mobile_cards_extracts_dashboard_cards(self) -> None:
        cards = build_mobile_cards("project_check", PROJECT_CHECK_MARKDOWN)

        self.assertIn(
            {"label": "Literature", "status": "needs_attention", "message": "1 PDF missing, 2 notes missing"},
            cards,
        )
        self.assertIn(
            {"label": "Simulation", "status": "ready", "message": "No simulation issues found"},
            cards,
        )
        self.assertIn(
            {"label": "Manuscript", "status": "needs_attention", "message": "1 manuscript issue found"},
            cards,
        )

    def test_mobile_response_includes_raw_markdown(self) -> None:
        response = mobile_response("project_check", PROJECT_CHECK_MARKDOWN)

        self.assertTrue(response["ok"])
        self.assertEqual(response["action"], "project_check")
        self.assertEqual(response["markdown"], PROJECT_CHECK_MARKDOWN)
        self.assertEqual(response["summary"]["primaryMessage"], "4 items need attention")

    def test_project_check_counts_named_assets_and_section_issue_bullets(self) -> None:
        summary = build_mobile_summary("project_check", REALISH_PROJECT_CHECK_MARKDOWN)
        cards = build_mobile_cards("project_check", REALISH_PROJECT_CHECK_MARKDOWN)

        self.assertEqual(summary["primaryMessage"], "6 items need attention")
        self.assertIn(
            {"label": "Literature", "status": "needs_attention", "message": "2 PDFs missing, 1 note missing"},
            cards,
        )
        self.assertIn(
            {"label": "Simulation", "status": "needs_attention", "message": "2 simulation issues found"},
            cards,
        )
        self.assertIn(
            {"label": "Manuscript", "status": "needs_attention", "message": "1 manuscript issue found"},
            cards,
        )

    def test_summary_pluralizes_single_attention_item(self) -> None:
        summary = build_mobile_summary("project_check", SINGULAR_GAP_MARKDOWN)

        self.assertEqual(summary["primaryMessage"], "1 item needs attention")


if __name__ == "__main__":
    unittest.main()
