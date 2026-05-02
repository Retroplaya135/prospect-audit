"""Generic phone-line normalization and provider-response classification."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping

E164_RE = re.compile(r"^\+[1-9]\d{7,14}$")

PROVIDER_TYPE_MAP = {
    "mobile": ("mobile", "yes"),
    "nonfixedvoip": ("voip_nonfixed", "likely"),
    "fixedvoip": ("voip_fixed", "likely"),
    "landline": ("landline", "no"),
    "tollfree": ("toll_free", "no"),
    "premium": ("premium_rate", "no"),
    "sharedcost": ("shared_cost", "no"),
    "personal": ("personal_number", "unknown"),
    "uan": ("uan", "unknown"),
    "voicemail": ("voicemail", "no"),
    "pager": ("pager", "no"),
    "unknown": ("unknown", "unknown"),
}


@dataclass(frozen=True)
class LineTypeResult:
    e164: str
    status: str
    line_type: str = ""
    textable: str = "unknown"
    carrier: str = ""
    error: str = ""


def normalize_e164(raw: str | None) -> str:
    """Normalize separators while requiring an explicit international prefix."""

    compact = re.sub(r"[\s().-]", "", str(raw or "").strip())
    if not E164_RE.fullmatch(compact):
        raise ValueError("phone value must be an E.164 number with an explicit country code")
    return compact


def classify_provider_payload(e164: str, payload: Mapping[str, Any]) -> LineTypeResult:
    """Map a provider response into a small provider-neutral result."""

    normalized = normalize_e164(e164)
    if not isinstance(payload, Mapping):
        return LineTypeResult(normalized, "provider_error", error="provider response was not an object")
    if payload.get("valid") is False:
        return LineTypeResult(normalized, "invalid", error="provider marked the number invalid")
    intelligence = payload.get("line_type_intelligence")
    if not isinstance(intelligence, Mapping):
        return LineTypeResult(normalized, "provider_error", error="line type intelligence was missing")
    if intelligence.get("error_code"):
        return LineTypeResult(normalized, "provider_error", error=f"provider error {intelligence['error_code']}")

    raw_type = str(intelligence.get("type") or "unknown").replace("_", "").lower()
    line_type, textable = PROVIDER_TYPE_MAP.get(raw_type, ("unknown", "unknown"))
    carrier = str(intelligence.get("carrier_name") or "")[:120]
    return LineTypeResult(normalized, "resolved", line_type, textable, carrier)


def enrich_rows(
    rows: Iterable[Mapping[str, Any]],
    lookup: Callable[[str], Mapping[str, Any]],
    *,
    phone_field: str = "phone",
) -> list[dict[str, Any]]:
    """Return copies of rows enriched by a caller-supplied lookup function."""

    enriched: list[dict[str, Any]] = []
    for source in rows:
        row = dict(source)
        try:
            e164 = normalize_e164(str(row.get(phone_field) or ""))
            result = classify_provider_payload(e164, lookup(e164))
        except ValueError as exc:
            result = LineTypeResult("", "invalid", error=str(exc))
        row.update(
            {
                "phone_e164": result.e164,
                "line_type_status": result.status,
                "line_type": result.line_type,
                "is_textable": result.textable,
                "carrier_name": result.carrier,
                "line_type_error": result.error,
            }
        )
        enriched.append(row)
    return enriched
