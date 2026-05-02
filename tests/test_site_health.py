from __future__ import annotations

import socket
import unittest

from prospect_audit.site_health import UnsafeURL, analyse_html, validate_public_url


def resolver_for(*addresses: str):
    def resolve(host: str, port: int, *, type: int = socket.SOCK_STREAM):
        del host, type
        return [(socket.AF_INET6 if ":" in address else socket.AF_INET, socket.SOCK_STREAM, 6, "", (address, port)) for address in addresses]

    return resolve


class PublicUrlTests(unittest.TestCase):
    def test_accepts_public_https_url(self) -> None:
        value = validate_public_url("https://example.test/path#fragment", resolver_for("93.184.216.34"))
        self.assertEqual(value, "https://example.test/path")

    def test_rejects_local_and_private_destinations(self) -> None:
        blocked = ("127.0.0.1", "10.0.0.8", "169.254.1.1", "::1", "fc00::1")
        for address in blocked:
            with self.subTest(address=address), self.assertRaises(UnsafeURL):
                validate_public_url("https://example.test/", resolver_for(address))

    def test_rejects_mixed_public_and_private_dns_answers(self) -> None:
        with self.assertRaises(UnsafeURL):
            validate_public_url("https://example.test/", resolver_for("93.184.216.34", "127.0.0.1"))

    def test_rejects_credentials_and_non_http_schemes(self) -> None:
        for value in ("file:///etc/passwd", "https://user:pass@example.test/"):
            with self.subTest(value=value), self.assertRaises(UnsafeURL):
                validate_public_url(value, resolver_for("93.184.216.34"))


class HtmlObservationTests(unittest.TestCase):
    def test_reports_observable_page_characteristics(self) -> None:
        body = """<html><head><title>Example Service</title><meta name='viewport' content='width=device-width'></head>
        <body><p>Call (202) 555-0100.</p><p>{}</p></body></html>""".format("Useful content. " * 80)
        result = analyse_html("https://example.test/", "https://example.test/", 200, body, elapsed_ms=250)
        self.assertEqual(result.verdict, "strong")
        self.assertTrue(result.mobile_ready)
        self.assertTrue(result.has_phone)

    def test_reports_placeholder_without_sales_inference(self) -> None:
        result = analyse_html("https://example.test/", "https://example.test/", 200, "<p>This domain is parked</p>")
        self.assertEqual(result.verdict, "placeholder")
        self.assertIn("parked or placeholder page", result.findings)


if __name__ == "__main__":
    unittest.main()
