"""Schema = single source of truth.

The SQL DDL, the data dictionary, the ER diagram and (later) the validator
are all generated from the ENTITIES list below, so they cannot disagree.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import config as C
from . import ids as I


@dataclass(frozen=True)
class Field:
    name: str
    type: str  # TEXT | INTEGER | REAL | BOOLEAN | DATE | TIMESTAMP
    required: bool = True
    allowed: tuple = ()
    unit: str = ""
    unique: bool = False
    rule: str = ""
    fk: str = ""  # "table.column"
    pk: bool = False
    pattern: str = ""


@dataclass(frozen=True)
class Entity:
    table: str
    description: str
    fields: tuple
    cardinality: tuple = ()
    lifecycle: str = ""
    ground_truth: bool = False  # kept in a separate DDL/file, never an input feature


def F(name, type="TEXT", req=True, allowed=(), unit="", unique=False, rule="", fk="", pk=False, pattern=""):
    return Field(name, type, req, tuple(allowed), unit, unique, rule, fk, pk, pattern)


TS = "TIMESTAMP"
ENTITIES: tuple[Entity, ...] = (
    Entity("role", "The five actor roles.",
        (F("role_id", pk=True, rule="'ROLE-' + role_code", pattern=r"^ROLE-[A-Z_]+$"),
         F("role_code", allowed=C.ROLE_CODES, unique=True),
         F("can_submit_tickets", "BOOLEAN", rule="learner/instructor/acad_admin = 1"),
         F("can_resolve_tickets", "BOOLEAN", rule="support_staff/acad_admin/platform_admin = 1")),
        ("Role 1:N Requester", "Role 1:N StaffMember")),
    Entity("term", "Academic term; drives deadline logic (add/drop, fee payment).",
        (F("term_id", pk=True, pattern=r"^TERM-2026-(SPR|SUM|FAL)$"),
         F("term_name"),
         F("start_date", "DATE"), F("end_date", "DATE", rule="> start_date"),
         F("add_drop_deadline", "DATE", rule="between start_date and end_date"),
         F("fee_payment_deadline", "DATE", rule="<= add_drop_deadline"),
         F("status", allowed=C.TERM_STATUSES)),
        ("Term 1:N Ticket",), "PLANNED -> ACTIVE -> CLOSED"),
    Entity("team", "Support team that can own tickets.",
        (F("team_id", pk=True, pattern=r"^TEAM-[A-Z]+$"),
         F("team_name", unique=True),
         F("domain", allowed=C.DOMAINS + ("GENERAL",)),
         F("is_triage", "BOOLEAN", rule="exactly one triage team (GENERAL)")),
        ("Team 1:N StaffMember", "Team N:M Category via team_category_authorization", "Team 1:N Assignment")),
    Entity("staff_member", "Support staff / admins who work tickets.",
        (F("staff_id", pk=True, pattern=I.P_STAFF),
         F("team_id", fk="team.team_id"),
         F("role_id", fk="role.role_id", rule="role must have can_resolve_tickets=1"),
         F("full_name", rule="synthetic name"),
         F("email", unique=True, rule="synthetic, @example.edu only"),
         F("active", "BOOLEAN")),
        ("StaffMember 1:N Assignment",)),
    Entity("requester", "Learners, instructors and admins who raise tickets (synthetic people).",
        (F("requester_id", pk=True, pattern=I.P_REQUESTER),
         F("role_id", fk="role.role_id", rule="role.can_submit_tickets = 1"),
         F("full_name", rule="synthetic name"),
         F("email", unique=True, rule="synthetic, reserved @example.edu domain; no real PII"),
         F("program_level", req=False, allowed=("UG", "PG", "PHD"), rule="only for LEARNER"),
         F("created_at", TS),
         F("status", allowed=("ACTIVE", "INACTIVE"))),
        ("Requester 1:N Ticket",)),
    Entity("category", "Ticket category; one per domain in the baseline.",
        (F("category_id", pk=True, pattern=r"^CAT-[A-Z]+$"),
         F("category_name", unique=True),
         F("domain", allowed=C.DOMAINS),
         F("default_team_id", fk="team.team_id")),
        ("Category 1:N Ticket", "Category 1:N RoutingRule")),
    Entity("team_category_authorization",
        "Bridge: which team may legally own which category (basis for 'unauthorized team').",
        (F("team_id", fk="team.team_id", pk=True),
         F("category_id", fk="category.category_id", pk=True),
         F("effective_from", "DATE"),
         F("effective_to", "DATE", req=False, rule="NULL = open-ended; > effective_from")),
        ("Team N:M Category",)),
    Entity("business_calendar", "Business days/hours used by every SLA computation.",
        (F("calendar_date", "DATE", pk=True),
         F("is_business_day", "BOOLEAN", rule="0 on weekends and holidays"),
         F("open_time", req=False, rule="HH:MM:SS; NULL when closed"),
         F("close_time", req=False, rule="> open_time; NULL when closed"),
         F("holiday_name", req=False)),
        ("BusinessCalendar 1:N SLA (implicit by date)",)),
    Entity("sla_policy", "SLA targets per priority, measured in BUSINESS hours.",
        (F("sla_policy_id", pk=True, pattern=r"^SLAP-(LOW|NORMAL|HIGH|URGENT)$"),
         F("priority", allowed=C.PRIORITIES, unique=True),
         F("first_response_business_hours", "REAL", unit="business hours", rule="> 0"),
         F("resolution_business_hours", "REAL", unit="business hours", rule=">= first_response"),
         F("effective_from", "DATE")),
        ("SLAPolicy 1:N SLA",)),
    Entity("routing_rule", "Documented rule: category (+ minimum priority) -> team.",
        (F("routing_rule_id", pk=True, pattern=r"^RR-\d{3}$"),
         F("category_id", fk="category.category_id"),
         F("target_team_id", fk="team.team_id", rule="team must be authorized for category"),
         F("rule_order", "INTEGER", rule="lower = evaluated first; unique per category"),
         F("effective_from", "DATE"),
         F("effective_to", "DATE", req=False)),
        ("RoutingRule 1:N Assignment (optional)",)),
    Entity("escalation_rule", "Documented rule: when a ticket MUST be escalated to a human.",
        (F("escalation_rule_id", pk=True, pattern=r"^ESC-\d{3}$"),
         F("trigger_type", allowed=C.ESCALATION_TRIGGERS, unique=True),
         F("threshold_value", "REAL", req=False, rule="trigger-specific, see description"),
         F("threshold_unit", req=False, allowed=("DAYS", "REOPENS", "PERCENT")),
         F("target_team_id", fk="team.team_id"),
         F("description")),
        ()),
    Entity("policy_document", "A policy identified by domain; versions hold the content.",
        (F("policy_id", pk=True, pattern=I.P_POLICY),
         F("domain", allowed=C.DOMAINS),
         F("title"),
         F("owner_team_id", fk="team.team_id"),
         F("created_at", "DATE")),
        ("PolicyDocument 1:N PolicyVersion",)),
    Entity("policy_version", "Immutable policy version with effective window.",
        (F("policy_version_id", pk=True, pattern=I.P_POLICY_VERSION),
         F("policy_id", fk="policy_document.policy_id"),
         F("version_no", "INTEGER", rule=">= 1; unique per policy"),
         F("effective_from", "DATE"),
         F("effective_to", "DATE", req=False, rule="NULL = still in force; > effective_from"),
         F("lifecycle_status", allowed=C.POLICY_STATUSES,
           rule="CURRENT iff effective_to is NULL or in future"),
         F("summary_text"),
         F("supersedes_version_id", fk="policy_version.policy_version_id", req=False,
           rule="previous version of same policy")),
        ("PolicyVersion 1:N KnowledgeArticle",), "DRAFT -> CURRENT -> SUPERSEDED/EXPIRED"),
    Entity("knowledge_article", "Answerable article derived from one policy version.",
        (F("article_id", pk=True, pattern=I.P_ARTICLE),
         F("policy_version_id", fk="policy_version.policy_version_id"),
         F("article_version", "INTEGER", rule=">= 1; recorded on every citation"),
         F("domain", allowed=C.DOMAINS, rule="equals policy domain"),
         F("title"), F("body"),
         F("audience_role_id", fk="role.role_id", req=False),
         F("status", allowed=C.ARTICLE_STATUSES),
         F("effective_from", "DATE", rule="not before policy_version.effective_from"),
         F("effective_to", "DATE", req=False, rule="not after policy_version.effective_to"),
         F("supersedes_article_id", fk="knowledge_article.article_id", req=False)),
        ("KnowledgeArticle N:M Message via message_citation",), "DRAFT -> PUBLISHED -> RETIRED"),
    Entity("ticket", "A support request. Only OBSERVABLE fields; labels live in ground_truth.",
        (F("ticket_id", pk=True, pattern=I.P_TICKET),
         F("requester_id", fk="requester.requester_id"),
         F("category_id", fk="category.category_id", rule="category assigned at triage (may be wrong)"),
         F("term_id", fk="term.term_id", req=False),
         F("channel", allowed=C.CHANNELS),
         F("priority", allowed=C.PRIORITIES),
         F("subject"),
         F("created_at", TS),
         F("deadline_date", "DATE", req=False, rule="requester-stated or term deadline; >= date(created_at)"),
         F("current_status", allowed=C.TICKET_STATUSES, rule="DERIVED: to_status of latest ticket_status_event"),
         F("closed_at", TS, req=False, rule="set iff current_status = CLOSED; = that event's event_at")),
        ("Requester 1:N Ticket", "Ticket 1:N Message", "Ticket 1:N Assignment",
         "Ticket 1:N TicketStatusEvent", "Ticket 1:1 SLA", "Ticket 0..1 ResolutionFeedback"),
        "see TRANSITIONS in config.py"),
    Entity("ticket_status_event", "Append-only history of every state change.",
        (F("event_id", pk=True, pattern=I.P_EVENT),
         F("ticket_id", fk="ticket.ticket_id"),
         F("seq", "INTEGER", rule="1..n contiguous per ticket"),
         F("from_status", req=False, allowed=C.TICKET_STATUSES, rule="NULL only for first event"),
         F("to_status", allowed=C.TICKET_STATUSES, rule="(from,to) in TRANSITIONS"),
         F("event_at", TS, rule="non-decreasing per ticket"),
         F("actor_ref", rule="staff_id, requester_id or 'SYSTEM'"),
         F("reason", req=False)),
        ("Ticket 1:N TicketStatusEvent",)),
    Entity("message", "Conversation history. Append-only.",
        (F("message_id", pk=True, pattern=I.P_MESSAGE),
         F("ticket_id", fk="ticket.ticket_id"),
         F("seq", "INTEGER", rule="1..n contiguous per ticket; matches suffix of message_id"),
         F("sender_type", allowed=C.SENDER_TYPES),
         F("sender_ref", req=False, rule="requester_id/staff_id (polymorphic, no FK); NULL for SYSTEM/AI"),
         F("message_type", allowed=C.MESSAGE_TYPES),
         F("body"),
         F("sent_at", TS, rule="non-decreasing per ticket; >= ticket.created_at")),
        ("Ticket 1:N Message", "Message N:M KnowledgeArticle via message_citation")),
    Entity("message_citation", "Bridge: which article version a response cites.",
        (F("message_id", fk="message.message_id", pk=True),
         F("article_id", fk="knowledge_article.article_id", pk=True),
         F("citation_order", "INTEGER", rule=">= 1"),
         F("article_version_cited", "INTEGER", rule="= knowledge_article.article_version")),
        ("Message N:M KnowledgeArticle",)),
    Entity("assignment", "Append-only ownership history of a ticket.",
        (F("assignment_id", pk=True, pattern=I.P_ASSIGNMENT),
         F("ticket_id", fk="ticket.ticket_id"),
         F("seq", "INTEGER", rule="1..n contiguous per ticket"),
         F("team_id", fk="team.team_id"),
         F("staff_id", fk="staff_member.staff_id", req=False, rule="staff must belong to team_id"),
         F("assignment_type", allowed=C.ASSIGNMENT_TYPES),
         F("routing_rule_id", fk="routing_rule.routing_rule_id", req=False),
         F("assigned_at", TS),
         F("ended_at", TS, req=False, rule="NULL for current owner; > assigned_at")),
        ("Ticket 1:N Assignment",)),
    Entity("sla", "One SLA clock per ticket, computed in business hours.",
        (F("sla_id", pk=True, pattern=I.P_SLA),
         F("ticket_id", fk="ticket.ticket_id", unique=True),
         F("sla_policy_id", fk="sla_policy.sla_policy_id", rule="matches ticket.priority"),
         F("start_at", TS, rule="= ticket.created_at"),
         F("first_response_due_at", TS, rule="DERIVED via business calendar from start_at"),
         F("resolution_due_at", TS, rule="DERIVED via business calendar from start_at"),
         F("first_response_at", TS, req=False, rule="= first STAFF/AI answer message sent_at"),
         F("resolved_at", TS, req=False, rule="= first RESOLVED event_at"),
         F("first_response_breached", "BOOLEAN", rule="DERIVED"),
         F("resolution_breached", "BOOLEAN", rule="DERIVED")),
        ("Ticket 1:1 SLA",)),
    Entity("resolution_feedback", "Requester feedback after resolution.",
        (F("feedback_id", pk=True, pattern=I.P_FEEDBACK),
         F("ticket_id", fk="ticket.ticket_id", unique=True, rule="ticket must have a RESOLVED event"),
         F("rating", "INTEGER", allowed=(1, 2, 3, 4, 5)),
         F("resolved_first_contact", "BOOLEAN", rule="DERIVED: ticket has <= 1 staff answer"),
         F("comment", req=False),
         F("submitted_at", TS, rule="> RESOLVED event_at")),
        ("Ticket 0..1 ResolutionFeedback",)),
    Entity("ground_truth", "Expected labels and injected anomalies. NEVER an input feature.",
        (F("ground_truth_id", pk=True, pattern=I.P_GROUND_TRUTH),
         F("entity_type", allowed=("ticket", "message", "assignment", "sla", "message_citation")),
         F("entity_id", rule="ID of the affected row (message_citation: 'message_id|article_id')"),
         F("issue_type", allowed=C.GROUND_TRUTH_ISSUE_TYPES),
         F("is_injected", "BOOLEAN", rule="1 for the five injected anomalies"),
         F("violated_rule", req=False, rule="documented rule id/text"),
         F("expected_value", req=False),
         F("observed_value", req=False),
         F("notes", req=False)),
        (), ground_truth=True),
)

BY_TABLE = {e.table: e for e in ENTITIES}


def input_entities() -> tuple[Entity, ...]:
    return tuple(e for e in ENTITIES if not e.ground_truth)


def _sql_type(t: str) -> str:
    return {"TEXT": "TEXT", "INTEGER": "INTEGER", "REAL": "REAL", "BOOLEAN": "INTEGER",
            "DATE": "TEXT", "TIMESTAMP": "TEXT"}[t]


def _lit(v) -> str:
    return str(v) if isinstance(v, int) else "'" + str(v).replace("'", "''") + "'"


def ddl(entity: Entity) -> str:
    cols, pks, tail = [], [], []
    for f in entity.fields:
        parts = [f.name, _sql_type(f.type)]
        if f.required:
            parts.append("NOT NULL")
        if f.unique:
            parts.append("UNIQUE")
        if f.type == "BOOLEAN":
            parts.append(f"CHECK ({f.name} IN (0,1))")
        if f.allowed:
            parts.append(f"CHECK ({f.name} IN ({', '.join(_lit(v) for v in f.allowed)}))")
        cols.append("  " + " ".join(parts))
        if f.pk:
            pks.append(f.name)
        if f.fk:
            t, c = f.fk.split(".")
            tail.append(f"  FOREIGN KEY ({f.name}) REFERENCES {t}({c})")
    tail.insert(0, f"  PRIMARY KEY ({', '.join(pks)})")
    return f"CREATE TABLE {entity.table} (\n" + ",\n".join(cols + tail) + "\n);"


def ordered(entities) -> list[Entity]:
    """Topological order: parents before children (self-references ignored)."""
    pending = {e.table: e for e in entities}
    done: list[Entity] = []
    placed: set[str] = set()
    while pending:
        progressed = False
        for t, e in list(pending.items()):
            deps = {f.fk.split(".")[0] for f in e.fields if f.fk} - {t}
            if deps <= placed:
                done.append(e)
                placed.add(t)
                del pending[t]
                progressed = True
        if not progressed:
            raise RuntimeError(f"circular FK dependency among {list(pending)}")
    return done


def full_ddl(include_ground_truth: bool = False) -> str:
    ents = ENTITIES if include_ground_truth else input_entities()
    return "\n\n".join(ddl(e) for e in ordered(ents)) + "\n"
