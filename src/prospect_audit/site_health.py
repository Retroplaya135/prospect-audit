"""Bounded website observations for URLs supplied by the operator."""

from __future__ import annotations

import ipaddress
import re
import socket
from dataclasses import dataclass, field
from typing import Callable, Iterable
from urllib.parse import urlsplit, urlunsplit

USER_AGENT = "ProspectAudit/0.1"
PARKED_MARKERS = (
    "domain is for sale",
    "buy this domain",
    "this domain is parked",
    "sedo domain",
    "hugedomains",
    "afternic",
    "under construction",
    "coming soon",
    "site not published",
)
PHONE_ON_PAGE = re.compile(r"(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}")
SCRIPT_STYLE_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.I | re.S)
TAG_RE = re.compile(r"<[^>]+>")
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
VIEWPORT_RE = re.compile(r"<meta[^>]+name=[\"']?viewport[\"']?[^>]*>", re.I)

Resolver = Callable[..., Iterable[tuple]]


class UnsafeURL(ValueError):
    """Raised when a URL can address a non-public network destination."""


@dataclass(frozen=True)
class SiteObservation:
    requested_url: str
    final_url: str
    status: int
    body_bytes: int
    elapsed_ms: int
    https: bool
    mobile_ready: bool
    has_phone: bool
    title: str
    text_chars: int
    verdict: str
    score: int
    findings: tuple[str, ...] = field(default_factory=tuple)


def _is_public(address: str) -> bool:
    value = address.split("%", 1)[0]
    return ipaddress.ip_address(value).is_global


def validate_public_url(url: str, resolver: Resolver = socket.getaddrinfo) -> str:
    """Return a normalized public HTTP(S) URL or raise ``UnsafeURL``."""

    parsed = urlsplit(str(url).strip())
    if parsed.scheme.lower() not in {"http", "https"}:
        raise UnsafeURL("only http and https URLs are accepted")
    if not parsed.hostname:
        raise UnsafeURL("URL must include a hostname")
    if parsed.username or parsed.password:
        raise UnsafeURL("embedded credentials are not accepted")

    port = parsed.port or (443 if parsed.scheme.lower() == "https" else 80)
    try:
        addresses = [str(ipaddress.ip_address(parsed.hostname.strip("[]")))]
    except ValueError:
        try:
            answers = resolver(parsed.hostname, port, type=socket.SOCK_STREAM)
        except OSError as exc:
            raise UnsafeURL(f"hostname did not resolve: {exc}") from exc
        addresses = sorted({answer[4][0] for answer in answers})

    if not addresses:
        raise UnsafeURL("hostname did not resolve")
    if any(not _is_public(address) for address in addresses):
        raise UnsafeURL("URL resolves to a non-public network address")

    return urlunsplit((parsed.scheme.lower(), parsed.netloc, parsed.path or "/", parsed.query, ""))


def analyse_html(
    requested_url: str,
    final_url: str,
    status: int,
    body: str,
    *,
    body_bytes: int | None = None,
    elapsed_ms: int = 0,
) -> SiteObservation:
    """Produce neutral, observable page-quality signals from one HTML response."""

    lowered = body.lower()
    stripped = TAG_RE.sub(" ", SCRIPT_STYLE_RE.sub(" ", body))
    compact_text = " ".join(stripped.split())
    title_match = TITLE_RE.search(body)
    title = " ".join(title_match.group(1).split())[:120] if title_match else ""
    mobile_ready = bool(VIEWPORT_RE.search(body))
    has_phone = bool(PHONE_ON_PAGE.search(compact_text))
    parked = any(marker in lowered for marker in PARKED_MARKERS)
    findings: list[str] = []

    if status >= 500:
        verdict, score = "unavailable", 0
        findings.append(f"server error HTTP {status}")
    elif status >= 400:
        verdict, score = "unavailable", 0
        findings.append(f"HTTP {status}")
    elif parked:
        verdict, score = "placeholder", 5
        findings.append("parked or placeholder page")
    else:
        score = 100
        if not final_url.lower().startswith("https://"):
            score -= 25
            findings.append("response did not use HTTPS")
        if not mobile_ready:
            score -= 25
            findings.append("viewport metadata not observed")
        if not has_phone:
            score -= 15
            findings.append("phone number not observed in page text")
        if len(compact_text) < 900:
            score -= 15
            findings.append(f"limited visible text ({len(compact_text)} characters)")
        if not title:
            score -= 10
            findings.append("page title not observed")
        if elapsed_ms >= 6_000:
            score -= 25
            findings.append(f"HTML response took {elapsed_ms} ms")
        elif elapsed_ms >= 3_000:
            score -= 15
            findings.append(f"HTML response took {elapsed_ms} ms")
        score = max(0, min(100, score))
        verdict = "strong" if score >= 80 else "review" if score >= 60 else "weak"

    return SiteObservation(
        requested_url=requested_url,
        final_url=final_url,
        status=status,
        body_bytes=len(body.encode("utf-8")) if body_bytes is None else body_bytes,
        elapsed_ms=elapsed_ms,
        https=final_url.lower().startswith("https://"),
        mobile_ready=mobile_ready,
        has_phone=has_phone,
        title=title,
        text_chars=len(compact_text),
        verdict=verdict,
        score=score,
        findings=tuple(findings),
    )
