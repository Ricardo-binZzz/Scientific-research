import tempfile
import unittest
from io import BytesIO, StringIO
from pathlib import Path
from contextlib import redirect_stdout
from unittest.mock import patch

from workflow.cli import main
from workflow.library import LibraryEntry, LibraryIndex, load_index
from workflow.literature_discovery import discover_crossref, download_pdf_from_url


class _FakeResponse:
    def __init__(self, body: bytes, content_type: str = "application/json") -> None:
        self._body = body
        self.headers = {"Content-Type": content_type}

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc, _tb):
        return False

    def read(self) -> bytes:
        return self._body


class LiteratureDiscoveryTests(unittest.TestCase):
    def test_discover_crossref_maps_open_metadata_to_library_entries(self) -> None:
        payload = b"""
        {
          "message": {
            "items": [
              {
                "title": ["Adaptive fixture design"],
                "author": [{"family": "Zhang"}, {"family": "Li"}],
                "published-print": {"date-parts": [[2024]]},
                "container-title": ["Journal of Manufacturing Systems"],
                "DOI": "10.1000/fixture",
                "URL": "https://doi.org/10.1000/fixture",
                "abstract": "<jats:p>Fixture method.</jats:p>"
              }
            ]
          }
        }
        """

        index = discover_crossref("adaptive fixture", limit=1, opener=lambda _request, timeout=20: _FakeResponse(payload))

        self.assertEqual(len(index.entries), 1)
        entry = index.entries[0]
        self.assertEqual(entry.title, "Adaptive fixture design")
        self.assertEqual(entry.authors, ["Zhang", "Li"])
        self.assertEqual(entry.year, 2024)
        self.assertEqual(entry.source, "Journal of Manufacturing Systems")
        self.assertEqual(entry.doi, "10.1000/fixture")
        self.assertEqual(entry.database_source, "Crossref")
        self.assertIn("Fixture method.", entry.abstract)

    def test_download_pdf_from_url_writes_pdf_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)

            path = download_pdf_from_url(
                "https://example.org/paper.pdf",
                out_dir,
                filename="paper.pdf",
                opener=lambda _request, timeout=30: _FakeResponse(b"%PDF-1.4\nbody", "application/pdf"),
            )
            content = path.read_bytes()

        self.assertEqual(path.name, "paper.pdf")
        self.assertEqual(content, b"%PDF-1.4\nbody")

    def test_cli_library_discover_can_merge_results(self) -> None:
        entry = LibraryEntry(
            title="Adaptive fixture design",
            authors=["Zhang"],
            year=2024,
            source="Journal",
            doi="10.1000/fixture",
            pdf_name="",
            note_path="",
            database_source="Crossref",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            output = StringIO()
            with patch("workflow.commands.discover_crossref", return_value=LibraryIndex(entries=[entry])):
                with redirect_stdout(output):
                    exit_code = main(["library", "discover", tmpdir, "--query", "fixture", "--limit", "1", "--merge"])

            saved = load_index(Path(tmpdir))

        self.assertEqual(exit_code, 0)
        self.assertEqual(len(saved.entries), 1)
        self.assertIn("Adaptive fixture design", output.getvalue())

    def test_cli_library_download_pdf_writes_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = StringIO()
            with patch("workflow.commands.download_pdf_from_url", return_value=Path(tmpdir) / "paper.pdf"):
                with redirect_stdout(output):
                    exit_code = main([
                        "library",
                        "download-pdf",
                        tmpdir,
                        "https://example.org/paper.pdf",
                        "--filename",
                        "paper.pdf",
                    ])

        self.assertEqual(exit_code, 0)
        self.assertIn("paper.pdf", output.getvalue())


if __name__ == "__main__":
    unittest.main()
