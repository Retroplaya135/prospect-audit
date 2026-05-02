from __future__ import annotations

import csv
import unittest
from pathlib import Path

from prospect_audit.line_type import classify_provider_payload, enrich_rows, normalize_e164


class LineTypeTests(unittest.TestCase):
    def test_normalizes_explicit_e164_separators(self) -> None:
        self.assertEqual(normalize_e164("+1 (202) 555-0100"), "+12025550100")

    def test_rejects_implicit_or_malformed_numbers(self) -> None:
        for value in ("2025550100", "not-a-number", "+01234", ""):
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_e164(value)

    def test_classifies_provider_payload_without_sales_routing(self) -> None:
        result = classify_provider_payload(
            "+12025550100",
            {"valid": True, "line_type_intelligence": {"type": "mobile", "carrier_name": "Example Carrier"}},
        )
        self.assertEqual(result.status, "resolved")
        self.assertEqual(result.line_type, "mobile")
        self.assertEqual(result.textable, "yes")

    def test_enriches_synthetic_fixture_without_mutating_input(self) -> None:
        fixture = Path(__file__).parent / "fixtures" / "synthetic_prospects.csv"
        with fixture.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        original = [dict(row) for row in rows]

        def lookup(number: str):
            return {"valid": True, "line_type_intelligence": {"type": "landline"}}

        result = enrich_rows(rows, lookup)
        self.assertEqual(rows, original)
        self.assertEqual(result[0]["line_type"], "landline")
        self.assertEqual(result[1]["line_type_status"], "invalid")


if __name__ == "__main__":
    unittest.main()
