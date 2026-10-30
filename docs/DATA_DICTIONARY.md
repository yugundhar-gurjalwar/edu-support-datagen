# Data Dictionary

_Generated from `src/edusupport/schema.py` by `python -m edusupport.docs_builder`. Do not edit by hand._

- Timestamps: ISO `YYYY-MM-DD HH:MM:SS`, Asia/Kolkata (IST), stored naive as 'YYYY-MM-DD HH:MM:SS'.
- Types: TEXT, INTEGER, REAL, BOOLEAN (0/1), DATE (`YYYY-MM-DD`), TIMESTAMP.
- IDs are immutable and zero-padded; patterns are enforced by the validator.
- `ground_truth` is stored separately and must never be used as an input feature.

## Ticket lifecycle (allowed transitions)

| From | Allowed next states |
|---|---|
| NEW | TRIAGED |
| TRIAGED | ASSIGNED |
| ASSIGNED | IN_PROGRESS, ESCALATED |
| IN_PROGRESS | PENDING_REQUESTER, RESOLVED, ESCALATED |
| PENDING_REQUESTER | IN_PROGRESS, CLOSED |
| ESCALATED | IN_PROGRESS, RESOLVED |
| RESOLVED | CLOSED, REOPENED |
| REOPENED | IN_PROGRESS, ESCALATED |
| CLOSED | (terminal) |

## `role`

The five actor roles.

**Cardinality:** Role 1:N Requester; Role 1:N StaffMember  

| Field | Type | Req | Allowed values / pattern | Unit | Unique | FK | Validation rule |
|---|---|---|---|---|---|---|---|
| PK `role_id` | TEXT | Y | `^ROLE-[A-Z_]+$` |  | Y |  | 'ROLE-' + role_code |
| `role_code` | TEXT | Y | LEARNER, INSTRUCTOR, ACAD_ADMIN, SUPPORT_STAFF, PLATFORM_ADMIN |  | Y |  |  |
| `can_submit_tickets` | BOOLEAN | Y |  |  |  |  | learner/instructor/acad_admin = 1 |
| `can_resolve_tickets` | BOOLEAN | Y |  |  |  |  | support_staff/acad_admin/platform_admin = 1 |

## `term`

Academic term; drives deadline logic (add/drop, fee payment).

**Cardinality:** Term 1:N Ticket  
**Lifecycle:** PLANNED -> ACTIVE -> CLOSED  

| Field | Type | Req | Allowed values / pattern | Unit | Unique | FK | Validation rule |
|---|---|---|---|---|---|---|---|
| PK `term_id` | TEXT | Y | `^TERM-2026-(SPR\|SUM\|FAL)$` |  | Y |  |  |
| `term_name` | TEXT | Y |  |  |  |  |  |
| `start_date` | DATE | Y |  |  |  |  |  |
| `end_date` | DATE | Y |  |  |  |  | > start_date |
| `add_drop_deadline` | DATE | Y |  |  |  |  | between start_date and end_date |
| `fee_payment_deadline` | DATE | Y |  |  |  |  | <= add_drop_deadline |
| `status` | TEXT | Y | PLANNED, ACTIVE, CLOSED |  |  |  |  |

## `team`

Support team that can own tickets.

**Cardinality:** Team 1:N StaffMember; Team N:M Category via team_category_authorization; Team 1:N Assignment  

| Field | Type | Req | Allowed values / pattern | Unit | Unique | FK | Validation rule |
|---|---|---|---|---|---|---|---|
| PK `team_id` | TEXT | Y | `^TEAM-[A-Z]+$` |  | Y |  |  |
| `team_name` | TEXT | Y |  |  | Y |  |  |
| `domain` | TEXT | Y | FINAID, REG, IT, ACC, GENERAL |  |  |  |  |
| `is_triage` | BOOLEAN | Y |  |  |  |  | exactly one triage team (GENERAL) |

## `staff_member`

Support staff / admins who work tickets.

**Cardinality:** StaffMember 1:N Assignment  

| Field | Type | Req | Allowed values / pattern | Unit | Unique | FK | Validation rule |
|---|---|---|---|---|---|---|---|
| PK `staff_id` | TEXT | Y | `^STF-\d{4}$` |  | Y |  |  |
| `team_id` | TEXT | Y |  |  |  | team.team_id |  |
| `role_id` | TEXT | Y |  |  |  | role.role_id | role must have can_resolve_tickets=1 |
| `full_name` | TEXT | Y |  |  |  |  | synthetic name |
| `email` | TEXT | Y |  |  | Y |  | synthetic, @example.edu only |
| `active` | BOOLEAN | Y |  |  |  |  |  |

## `requester`

Learners, instructors and admins who raise tickets (synthetic people).

**Cardinality:** Requester 1:N Ticket  

| Field | Type | Req | Allowed values / pattern | Unit | Unique | FK | Validation rule |
|---|---|---|---|---|---|---|---|
| PK `requester_id` | TEXT | Y | `^REQ-\d{6}$` |  | Y |  |  |
| `role_id` | TEXT | Y |  |  |  | role.role_id | role.can_submit_tickets = 1 |
| `full_name` | TEXT | Y |  |  |  |  | synthetic name |
| `email` | TEXT | Y |  |  | Y |  | synthetic, reserved @example.edu domain; no real PII |
| `program_level` | TEXT | N | UG, PG, PHD |  |  |  | only for LEARNER |
| `created_at` | TIMESTAMP | Y |  |  |  |  |  |
| `status` | TEXT | Y | ACTIVE, INACTIVE |  |  |  |  |

## `category`

Ticket category; one per domain in the baseline.

**Cardinality:** Category 1:N Ticket; Category 1:N RoutingRule  

| Field | Type | Req | Allowed values / pattern | Unit | Unique | FK | Validation rule |
|---|---|---|---|---|---|---|---|
| PK `category_id` | TEXT | Y | `^CAT-[A-Z]+$` |  | Y |  |  |
| `category_name` | TEXT | Y |  |  | Y |  |  |
| `domain` | TEXT | Y | FINAID, REG, IT, ACC |  |  |  |  |
| `default_team_id` | TEXT | Y |  |  |  | team.team_id |  |

## `team_category_authorization`

Bridge: which team may legally own which category (basis for 'unauthorized team').

**Cardinality:** Team N:M Category  

| Field | Type | Req | Allowed values / pattern | Unit | Unique | FK | Validation rule |
|---|---|---|---|---|---|---|---|
| PK `team_id` | TEXT | Y |  |  | Y | team.team_id |  |
| PK `category_id` | TEXT | Y |  |  | Y | category.category_id |  |
| `effective_from` | DATE | Y |  |  |  |  |  |
| `effective_to` | DATE | N |  |  |  |  | NULL = open-ended; > effective_from |

## `business_calendar`

Business days/hours used by every SLA computation.

**Cardinality:** BusinessCalendar 1:N SLA (implicit by date)  

| Field | Type | Req | Allowed values / pattern | Unit | Unique | FK | Validation rule |
|---|---|---|---|---|---|---|---|
| PK `calendar_date` | DATE | Y |  |  | Y |  |  |
| `is_business_day` | BOOLEAN | Y |  |  |  |  | 0 on weekends and holidays |
| `open_time` | TEXT | N |  |  |  |  | HH:MM:SS; NULL when closed |
| `close_time` | TEXT | N |  |  |  |  | > open_time; NULL when closed |
| `holiday_name` | TEXT | N |  |  |  |  |  |

## `sla_policy`

SLA targets per priority, measured in BUSINESS hours.

**Cardinality:** SLAPolicy 1:N SLA  

| Field | Type | Req | Allowed values / pattern | Unit | Unique | FK | Validation rule |
|---|---|---|---|---|---|---|---|
| PK `sla_policy_id` | TEXT | Y | `^SLAP-(LOW\|NORMAL\|HIGH\|URGENT)$` |  | Y |  |  |
| `priority` | TEXT | Y | LOW, NORMAL, HIGH, URGENT |  | Y |  |  |
| `first_response_business_hours` | REAL | Y |  | business hours |  |  | > 0 |
| `resolution_business_hours` | REAL | Y |  | business hours |  |  | >= first_response |
| `effective_from` | DATE | Y |  |  |  |  |  |

## `routing_rule`

Documented rule: category (+ minimum priority) -> team.

**Cardinality:** RoutingRule 1:N Assignment (optional)  

| Field | Type | Req | Allowed values / pattern | Unit | Unique | FK | Validation rule |
|---|---|---|---|---|---|---|---|
| PK `routing_rule_id` | TEXT | Y | `^RR-\d{3}$` |  | Y |  |  |
| `category_id` | TEXT | Y |  |  |  | category.category_id |  |
| `target_team_id` | TEXT | Y |  |  |  | team.team_id | team must be authorized for category |
| `rule_order` | INTEGER | Y |  |  |  |  | lower = evaluated first; unique per category |
| `effective_from` | DATE | Y |  |  |  |  |  |
| `effective_to` | DATE | N |  |  |  |  |  |

## `escalation_rule`

Documented rule: when a ticket MUST be escalated to a human.


| Field | Type | Req | Allowed values / pattern | Unit | Unique | FK | Validation rule |
|---|---|---|---|---|---|---|---|
| PK `escalation_rule_id` | TEXT | Y | `^ESC-\d{3}$` |  | Y |  |  |
| `trigger_type` | TEXT | Y | AMBIGUOUS_UNRESOLVED, URGENT_DEADLINE, NO_APPLICABLE_POLICY, REPEATED_REOPEN, SLA_BREACH_IMMINENT |  | Y |  |  |
| `threshold_value` | REAL | N |  |  |  |  | trigger-specific, see description |
| `threshold_unit` | TEXT | N | DAYS, REOPENS, PERCENT |  |  |  |  |
| `target_team_id` | TEXT | Y |  |  |  | team.team_id |  |
| `description` | TEXT | Y |  |  |  |  |  |

## `policy_document`

A policy identified by domain; versions hold the content.

**Cardinality:** PolicyDocument 1:N PolicyVersion  

| Field | Type | Req | Allowed values / pattern | Unit | Unique | FK | Validation rule |
|---|---|---|---|---|---|---|---|
| PK `policy_id` | TEXT | Y | `^POL-(FINAID\|REG\|IT\|ACC)-2026-\d{3}$` |  | Y |  |  |
| `domain` | TEXT | Y | FINAID, REG, IT, ACC |  |  |  |  |
| `title` | TEXT | Y |  |  |  |  |  |
| `owner_team_id` | TEXT | Y |  |  |  | team.team_id |  |
| `created_at` | DATE | Y |  |  |  |  |  |

## `policy_version`

Immutable policy version with effective window.

**Cardinality:** PolicyVersion 1:N KnowledgeArticle  
**Lifecycle:** DRAFT -> CURRENT -> SUPERSEDED/EXPIRED  

| Field | Type | Req | Allowed values / pattern | Unit | Unique | FK | Validation rule |
|---|---|---|---|---|---|---|---|
| PK `policy_version_id` | TEXT | Y | `^POL-(FINAID\|REG\|IT\|ACC)-2026-\d{3}-V\d{2}$` |  | Y |  |  |
| `policy_id` | TEXT | Y |  |  |  | policy_document.policy_id |  |
| `version_no` | INTEGER | Y |  |  |  |  | >= 1; unique per policy |
| `effective_from` | DATE | Y |  |  |  |  |  |
| `effective_to` | DATE | N |  |  |  |  | NULL = still in force; > effective_from |
| `lifecycle_status` | TEXT | Y | DRAFT, CURRENT, SUPERSEDED, EXPIRED |  |  |  | CURRENT iff effective_to is NULL or in future |
| `summary_text` | TEXT | Y |  |  |  |  |  |
| `supersedes_version_id` | TEXT | N |  |  |  | policy_version.policy_version_id | previous version of same policy |

## `knowledge_article`

Answerable article derived from one policy version.

**Cardinality:** KnowledgeArticle N:M Message via message_citation  
**Lifecycle:** DRAFT -> PUBLISHED -> RETIRED  

| Field | Type | Req | Allowed values / pattern | Unit | Unique | FK | Validation rule |
|---|---|---|---|---|---|---|---|
| PK `article_id` | TEXT | Y | `^KB-\d{6}$` |  | Y |  |  |
| `policy_version_id` | TEXT | Y |  |  |  | policy_version.policy_version_id |  |
| `article_version` | INTEGER | Y |  |  |  |  | >= 1; recorded on every citation |
| `domain` | TEXT | Y | FINAID, REG, IT, ACC |  |  |  | equals policy domain |
| `title` | TEXT | Y |  |  |  |  |  |
| `body` | TEXT | Y |  |  |  |  |  |
| `audience_role_id` | TEXT | N |  |  |  | role.role_id |  |
| `status` | TEXT | Y | DRAFT, PUBLISHED, RETIRED |  |  |  |  |
| `effective_from` | DATE | Y |  |  |  |  | not before policy_version.effective_from |
| `effective_to` | DATE | N |  |  |  |  | not after policy_version.effective_to |
| `supersedes_article_id` | TEXT | N |  |  |  | knowledge_article.article_id |  |

## `ticket`

A support request. Only OBSERVABLE fields; labels live in ground_truth.

**Cardinality:** Requester 1:N Ticket; Ticket 1:N Message; Ticket 1:N Assignment; Ticket 1:N TicketStatusEvent; Ticket 1:1 SLA; Ticket 0..1 ResolutionFeedback  
**Lifecycle:** see TRANSITIONS in config.py  

| Field | Type | Req | Allowed values / pattern | Unit | Unique | FK | Validation rule |
|---|---|---|---|---|---|---|---|
| PK `ticket_id` | TEXT | Y | `^TKT-2026-\d{6}$` |  | Y |  |  |
| `requester_id` | TEXT | Y |  |  |  | requester.requester_id |  |
| `category_id` | TEXT | Y |  |  |  | category.category_id | category assigned at triage (may be wrong) |
| `term_id` | TEXT | N |  |  |  | term.term_id |  |
| `channel` | TEXT | Y | PORTAL, EMAIL, CHAT, PHONE |  |  |  |  |
| `priority` | TEXT | Y | LOW, NORMAL, HIGH, URGENT |  |  |  |  |
| `subject` | TEXT | Y |  |  |  |  |  |
| `created_at` | TIMESTAMP | Y |  |  |  |  |  |
| `deadline_date` | DATE | N |  |  |  |  | requester-stated or term deadline; >= date(created_at) |
| `current_status` | TEXT | Y | NEW, TRIAGED, ASSIGNED, IN_PROGRESS, PENDING_REQUESTER, ESCALATED, RESOLVED, REOPENED, CLOSED |  |  |  | DERIVED: to_status of latest ticket_status_event |
| `closed_at` | TIMESTAMP | N |  |  |  |  | set iff current_status = CLOSED; = that event's event_at |

## `ticket_status_event`

Append-only history of every state change.

**Cardinality:** Ticket 1:N TicketStatusEvent  

| Field | Type | Req | Allowed values / pattern | Unit | Unique | FK | Validation rule |
|---|---|---|---|---|---|---|---|
| PK `event_id` | TEXT | Y | `^EVT-TKT-2026-\d{6}-\d{2}$` |  | Y |  |  |
| `ticket_id` | TEXT | Y |  |  |  | ticket.ticket_id |  |
| `seq` | INTEGER | Y |  |  |  |  | 1..n contiguous per ticket |
| `from_status` | TEXT | N | NEW, TRIAGED, ASSIGNED, IN_PROGRESS, PENDING_REQUESTER, ESCALATED, RESOLVED, REOPENED, CLOSED |  |  |  | NULL only for first event |
| `to_status` | TEXT | Y | NEW, TRIAGED, ASSIGNED, IN_PROGRESS, PENDING_REQUESTER, ESCALATED, RESOLVED, REOPENED, CLOSED |  |  |  | (from,to) in TRANSITIONS |
| `event_at` | TIMESTAMP | Y |  |  |  |  | non-decreasing per ticket |
| `actor_ref` | TEXT | Y |  |  |  |  | staff_id, requester_id or 'SYSTEM' |
| `reason` | TEXT | N |  |  |  |  |  |

## `message`

Conversation history. Append-only.

**Cardinality:** Ticket 1:N Message; Message N:M KnowledgeArticle via message_citation  

| Field | Type | Req | Allowed values / pattern | Unit | Unique | FK | Validation rule |
|---|---|---|---|---|---|---|---|
| PK `message_id` | TEXT | Y | `^MSG-TKT-2026-\d{6}-\d{3}$` |  | Y |  |  |
| `ticket_id` | TEXT | Y |  |  |  | ticket.ticket_id |  |
| `seq` | INTEGER | Y |  |  |  |  | 1..n contiguous per ticket; matches suffix of message_id |
| `sender_type` | TEXT | Y | REQUESTER, STAFF, AI_ASSISTANT, SYSTEM |  |  |  |  |
| `sender_ref` | TEXT | N |  |  |  |  | requester_id/staff_id (polymorphic, no FK); NULL for SYSTEM/AI |
| `message_type` | TEXT | Y | QUESTION, CLARIFICATION_REQUEST, CLARIFICATION_REPLY, ANSWER, INTERNAL_NOTE, ESCALATION_NOTICE, RESOLUTION, FOLLOW_UP |  |  |  |  |
| `body` | TEXT | Y |  |  |  |  |  |
| `sent_at` | TIMESTAMP | Y |  |  |  |  | non-decreasing per ticket; >= ticket.created_at |

## `message_citation`

Bridge: which article version a response cites.

**Cardinality:** Message N:M KnowledgeArticle  

| Field | Type | Req | Allowed values / pattern | Unit | Unique | FK | Validation rule |
|---|---|---|---|---|---|---|---|
| PK `message_id` | TEXT | Y |  |  | Y | message.message_id |  |
| PK `article_id` | TEXT | Y |  |  | Y | knowledge_article.article_id |  |
| `citation_order` | INTEGER | Y |  |  |  |  | >= 1 |
| `article_version_cited` | INTEGER | Y |  |  |  |  | = knowledge_article.article_version |

## `assignment`

Append-only ownership history of a ticket.

**Cardinality:** Ticket 1:N Assignment  

| Field | Type | Req | Allowed values / pattern | Unit | Unique | FK | Validation rule |
|---|---|---|---|---|---|---|---|
| PK `assignment_id` | TEXT | Y | `^ASG-TKT-2026-\d{6}-\d{2}$` |  | Y |  |  |
| `ticket_id` | TEXT | Y |  |  |  | ticket.ticket_id |  |
| `seq` | INTEGER | Y |  |  |  |  | 1..n contiguous per ticket |
| `team_id` | TEXT | Y |  |  |  | team.team_id |  |
| `staff_id` | TEXT | N |  |  |  | staff_member.staff_id | staff must belong to team_id |
| `assignment_type` | TEXT | Y | INITIAL, REROUTE, ESCALATION |  |  |  |  |
| `routing_rule_id` | TEXT | N |  |  |  | routing_rule.routing_rule_id |  |
| `assigned_at` | TIMESTAMP | Y |  |  |  |  |  |
| `ended_at` | TIMESTAMP | N |  |  |  |  | NULL for current owner; > assigned_at |

## `sla`

One SLA clock per ticket, computed in business hours.

**Cardinality:** Ticket 1:1 SLA  

| Field | Type | Req | Allowed values / pattern | Unit | Unique | FK | Validation rule |
|---|---|---|---|---|---|---|---|
| PK `sla_id` | TEXT | Y | `^SLA-TKT-2026-\d{6}$` |  | Y |  |  |
| `ticket_id` | TEXT | Y |  |  | Y | ticket.ticket_id |  |
| `sla_policy_id` | TEXT | Y |  |  |  | sla_policy.sla_policy_id | matches ticket.priority |
| `start_at` | TIMESTAMP | Y |  |  |  |  | = ticket.created_at |
| `first_response_due_at` | TIMESTAMP | Y |  |  |  |  | DERIVED via business calendar from start_at |
| `resolution_due_at` | TIMESTAMP | Y |  |  |  |  | DERIVED via business calendar from start_at |
| `first_response_at` | TIMESTAMP | N |  |  |  |  | = first STAFF/AI answer message sent_at |
| `resolved_at` | TIMESTAMP | N |  |  |  |  | = first RESOLVED event_at |
| `first_response_breached` | BOOLEAN | Y |  |  |  |  | DERIVED |
| `resolution_breached` | BOOLEAN | Y |  |  |  |  | DERIVED |

## `resolution_feedback`

Requester feedback after resolution.

**Cardinality:** Ticket 0..1 ResolutionFeedback  

| Field | Type | Req | Allowed values / pattern | Unit | Unique | FK | Validation rule |
|---|---|---|---|---|---|---|---|
| PK `feedback_id` | TEXT | Y | `^FBK-TKT-2026-\d{6}$` |  | Y |  |  |
| `ticket_id` | TEXT | Y |  |  | Y | ticket.ticket_id | ticket must have a RESOLVED event |
| `rating` | INTEGER | Y | 1, 2, 3, 4, 5 |  |  |  |  |
| `resolved_first_contact` | BOOLEAN | Y |  |  |  |  | DERIVED: ticket has <= 1 staff answer |
| `comment` | TEXT | N |  |  |  |  |  |
| `submitted_at` | TIMESTAMP | Y |  |  |  |  | > RESOLVED event_at |

## `ground_truth`  (GROUND TRUTH, separate file)

Expected labels and injected anomalies. NEVER an input feature.


| Field | Type | Req | Allowed values / pattern | Unit | Unique | FK | Validation rule |
|---|---|---|---|---|---|---|---|
| PK `ground_truth_id` | TEXT | Y | `^GT-\d{6}$` |  | Y |  |  |
| `entity_type` | TEXT | Y | ticket, message, assignment, sla, message_citation |  |  |  |  |
| `entity_id` | TEXT | Y |  |  |  |  | ID of the affected row (message_citation: 'message_id\|article_id') |
| `issue_type` | TEXT | Y | EXPIRED_POLICY_CITED, UNAUTHORIZED_ROUTING, UNSUPPORTED_CLAIM, SLA_IGNORES_BUSINESS_HOURS, ESCALATION_NOT_TRIGGERED, AMBIGUOUS_REQUEST, URGENT_DEADLINE, NEEDS_HUMAN_ESCALATION, TRUE_CATEGORY |  |  |  |  |
| `is_injected` | BOOLEAN | Y |  |  |  |  | 1 for the five injected anomalies |
| `violated_rule` | TEXT | N |  |  |  |  | documented rule id/text |
| `expected_value` | TEXT | N |  |  |  |  |  |
| `observed_value` | TEXT | N |  |  |  |  |  |
| `notes` | TEXT | N |  |  |  |  |  |
