from __future__ import annotations

import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from prospect_audit.cli import main


FIXTURES = Path(__file__).parent / "fixtures"


class CliTests(unittest.TestCase):
    def test_html_command_is_offline_and_machine_readable(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            exit_code = main(["html", str(FIXTURES / "sample_site.html"), "--elapsed-ms", "120"])
        payload = json.loads(output.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["verdict"], "strong")
        self.assertTrue(payload["mobile_ready"])

    def test_line_command_classifies_local_fixture(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            exit_code = main(["line", "+12025550100", str(FIXTURES / "mobile_line.json")])
        payload = json.loads(output.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["line_type"], "mobile")


if __name__ == "__main__":
    unittest.main()
