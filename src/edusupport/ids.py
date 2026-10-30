"""Deterministic, zero-padded, immutable ID builders and their format patterns.

Mandated by the brief:
  TKT-2026-000001 | MSG-<ticket-id>-001 | KB-000001 | POL-<domain>-2026-001 | SLA-<ticket-id>
All other IDs follow the same style (documented in ASSUMPTIONS.md).
"""
from __future__ import annotations

import re

from .config import DATA_YEAR, DOMAINS

# ---- regex patterns (used by the data dictionary AND the validator) ----
P_TICKET = r"^TKT-2026-\d{6}$"
P_MESSAGE = r"^MSG-TKT-2026-\d{6}-\d{3}$"
P_ARTICLE = r"^KB-\d{6}$"
P_POLICY = r"^POL-(FINAID|REG|IT|ACC)-2026-\d{3}$"
P_POLICY_VERSION = r"^POL-(FINAID|REG|IT|ACC)-2026-\d{3}-V\d{2}$"
P_SLA = r"^SLA-TKT-2026-\d{6}$"
P_REQUESTER = r"^REQ-\d{6}$"
P_STAFF = r"^STF-\d{4}$"
P_ASSIGNMENT = r"^ASG-TKT-2026-\d{6}-\d{2}$"
P_EVENT = r"^EVT-TKT-2026-\d{6}-\d{2}$"
P_FEEDBACK = r"^FBK-TKT-2026-\d{6}$"
P_GROUND_TRUTH = r"^GT-\d{6}$"


def ticket_id(n: int) -> str:
    return f"TKT-{DATA_YEAR}-{n:06d}"


def message_id(tkt: str, seq: int) -> str:
    return f"MSG-{tkt}-{seq:03d}"


def article_id(n: int) -> str:
    return f"KB-{n:06d}"


def policy_id(domain: str, n: int) -> str:
    if domain not in DOMAINS:
        raise ValueError(f"unknown domain {domain!r}")
    return f"POL-{domain}-{DATA_YEAR}-{n:03d}"


def policy_version_id(pol: str, version_no: int) -> str:
    return f"{pol}-V{version_no:02d}"


def sla_id(tkt: str) -> str:
    return f"SLA-{tkt}"


def requester_id(n: int) -> str:
    return f"REQ-{n:06d}"


def staff_id(n: int) -> str:
    return f"STF-{n:04d}"


def assignment_id(tkt: str, seq: int) -> str:
    return f"ASG-{tkt}-{seq:02d}"


def event_id(tkt: str, seq: int) -> str:
    return f"EVT-{tkt}-{seq:02d}"


def feedback_id(tkt: str) -> str:
    return f"FBK-{tkt}"


def ground_truth_id(n: int) -> str:
    return f"GT-{n:06d}"


def matches(pattern: str, value: str) -> bool:
    return re.match(pattern, value) is not None
