"""Central configuration: seed, scale presets, enums and lifecycle rules.

Everything the generator AND the validator both need lives here, so the
documented rules and the generated data can never drift apart.
"""
from __future__ import annotations

from dataclasses import dataclass

DEFAULT_SEED = 20261022
DATA_YEAR = 2026

# ---------------------------------------------------------------- scale
@dataclass(frozen=True)
class Scale:
    tickets: int
    articles: int
    messages: int
    requesters: int
    seed: int = DEFAULT_SEED

    @staticmethod
    def full(seed: int = DEFAULT_SEED) -> "Scale":
        return Scale(tickets=5000, articles=200, messages=20000, requesters=1200, seed=seed)

    @staticmethod
    def starter(seed: int = DEFAULT_SEED) -> "Scale":
        return Scale(tickets=200, articles=40, messages=800, requesters=60, seed=seed)


# ---------------------------------------------------------------- enums
DOMAINS = ("FINAID", "REG", "IT", "ACC")  # domain codes used in IDs
ROLE_CODES = ("LEARNER", "INSTRUCTOR", "ACAD_ADMIN", "SUPPORT_STAFF", "PLATFORM_ADMIN")
PRIORITIES = ("LOW", "NORMAL", "HIGH", "URGENT")
CHANNELS = ("PORTAL", "EMAIL", "CHAT", "PHONE")
TICKET_STATUSES = (
    "NEW", "TRIAGED", "ASSIGNED", "IN_PROGRESS", "PENDING_REQUESTER",
    "ESCALATED", "RESOLVED", "REOPENED", "CLOSED",
)
SENDER_TYPES = ("REQUESTER", "STAFF", "AI_ASSISTANT", "SYSTEM")
MESSAGE_TYPES = (
    "QUESTION", "CLARIFICATION_REQUEST", "CLARIFICATION_REPLY", "ANSWER",
    "INTERNAL_NOTE", "ESCALATION_NOTICE", "RESOLUTION", "FOLLOW_UP",
)
ASSIGNMENT_TYPES = ("INITIAL", "REROUTE", "ESCALATION")
POLICY_STATUSES = ("DRAFT", "CURRENT", "SUPERSEDED", "EXPIRED")
ARTICLE_STATUSES = ("DRAFT", "PUBLISHED", "RETIRED")
TERM_STATUSES = ("PLANNED", "ACTIVE", "CLOSED")
ESCALATION_TRIGGERS = (
    "AMBIGUOUS_UNRESOLVED", "URGENT_DEADLINE", "NO_APPLICABLE_POLICY",
    "REPEATED_REOPEN", "SLA_BREACH_IMMINENT",
)

# Allowed ticket lifecycle transitions (validator rejects anything else).
TRANSITIONS: dict[str, tuple[str, ...]] = {
    "NEW": ("TRIAGED",),
    "TRIAGED": ("ASSIGNED",),
    "ASSIGNED": ("IN_PROGRESS", "ESCALATED"),
    "IN_PROGRESS": ("PENDING_REQUESTER", "RESOLVED", "ESCALATED"),
    "PENDING_REQUESTER": ("IN_PROGRESS", "CLOSED"),
    "ESCALATED": ("IN_PROGRESS", "RESOLVED"),
    "RESOLVED": ("CLOSED", "REOPENED"),
    "REOPENED": ("IN_PROGRESS", "ESCALATED"),
    "CLOSED": (),
}

# Injected anomalies (the 5 required) + generation labels, all in ground truth.
ANOMALY_TYPES = (
    "EXPIRED_POLICY_CITED",
    "UNAUTHORIZED_ROUTING",
    "UNSUPPORTED_CLAIM",
    "SLA_IGNORES_BUSINESS_HOURS",
    "ESCALATION_NOT_TRIGGERED",
)
LABEL_TYPES = ("AMBIGUOUS_REQUEST", "URGENT_DEADLINE", "NEEDS_HUMAN_ESCALATION", "TRUE_CATEGORY")
GROUND_TRUTH_ISSUE_TYPES = ANOMALY_TYPES + LABEL_TYPES

# Business calendar (all timestamps are campus-local time, Asia/Kolkata, naive).
BUSINESS_OPEN = "09:00:00"
BUSINESS_CLOSE = "17:00:00"
TIMEZONE_NOTE = "Asia/Kolkata (IST), stored naive as 'YYYY-MM-DD HH:MM:SS'"
