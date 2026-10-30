CREATE TABLE role (
  role_id TEXT NOT NULL,
  role_code TEXT NOT NULL UNIQUE CHECK (role_code IN ('LEARNER', 'INSTRUCTOR', 'ACAD_ADMIN', 'SUPPORT_STAFF', 'PLATFORM_ADMIN')),
  can_submit_tickets INTEGER NOT NULL CHECK (can_submit_tickets IN (0,1)),
  can_resolve_tickets INTEGER NOT NULL CHECK (can_resolve_tickets IN (0,1)),
  PRIMARY KEY (role_id)
);

CREATE TABLE term (
  term_id TEXT NOT NULL,
  term_name TEXT NOT NULL,
  start_date TEXT NOT NULL,
  end_date TEXT NOT NULL,
  add_drop_deadline TEXT NOT NULL,
  fee_payment_deadline TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('PLANNED', 'ACTIVE', 'CLOSED')),
  PRIMARY KEY (term_id)
);

CREATE TABLE team (
  team_id TEXT NOT NULL,
  team_name TEXT NOT NULL UNIQUE,
  domain TEXT NOT NULL CHECK (domain IN ('FINAID', 'REG', 'IT', 'ACC', 'GENERAL')),
  is_triage INTEGER NOT NULL CHECK (is_triage IN (0,1)),
  PRIMARY KEY (team_id)
);

CREATE TABLE staff_member (
  staff_id TEXT NOT NULL,
  team_id TEXT NOT NULL,
  role_id TEXT NOT NULL,
  full_name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  active INTEGER NOT NULL CHECK (active IN (0,1)),
  PRIMARY KEY (staff_id),
  FOREIGN KEY (team_id) REFERENCES team(team_id),
  FOREIGN KEY (role_id) REFERENCES role(role_id)
);

CREATE TABLE requester (
  requester_id TEXT NOT NULL,
  role_id TEXT NOT NULL,
  full_name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  program_level TEXT CHECK (program_level IN ('UG', 'PG', 'PHD')),
  created_at TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('ACTIVE', 'INACTIVE')),
  PRIMARY KEY (requester_id),
  FOREIGN KEY (role_id) REFERENCES role(role_id)
);

CREATE TABLE category (
  category_id TEXT NOT NULL,
  category_name TEXT NOT NULL UNIQUE,
  domain TEXT NOT NULL CHECK (domain IN ('FINAID', 'REG', 'IT', 'ACC')),
  default_team_id TEXT NOT NULL,
  PRIMARY KEY (category_id),
  FOREIGN KEY (default_team_id) REFERENCES team(team_id)
);

CREATE TABLE team_category_authorization (
  team_id TEXT NOT NULL,
  category_id TEXT NOT NULL,
  effective_from TEXT NOT NULL,
  effective_to TEXT,
  PRIMARY KEY (team_id, category_id),
  FOREIGN KEY (team_id) REFERENCES team(team_id),
  FOREIGN KEY (category_id) REFERENCES category(category_id)
);

CREATE TABLE business_calendar (
  calendar_date TEXT NOT NULL,
  is_business_day INTEGER NOT NULL CHECK (is_business_day IN (0,1)),
  open_time TEXT,
  close_time TEXT,
  holiday_name TEXT,
  PRIMARY KEY (calendar_date)
);

CREATE TABLE sla_policy (
  sla_policy_id TEXT NOT NULL,
  priority TEXT NOT NULL UNIQUE CHECK (priority IN ('LOW', 'NORMAL', 'HIGH', 'URGENT')),
  first_response_business_hours REAL NOT NULL,
  resolution_business_hours REAL NOT NULL,
  effective_from TEXT NOT NULL,
  PRIMARY KEY (sla_policy_id)
);

CREATE TABLE routing_rule (
  routing_rule_id TEXT NOT NULL,
  category_id TEXT NOT NULL,
  target_team_id TEXT NOT NULL,
  rule_order INTEGER NOT NULL,
  effective_from TEXT NOT NULL,
  effective_to TEXT,
  PRIMARY KEY (routing_rule_id),
  FOREIGN KEY (category_id) REFERENCES category(category_id),
  FOREIGN KEY (target_team_id) REFERENCES team(team_id)
);

CREATE TABLE escalation_rule (
  escalation_rule_id TEXT NOT NULL,
  trigger_type TEXT NOT NULL UNIQUE CHECK (trigger_type IN ('AMBIGUOUS_UNRESOLVED', 'URGENT_DEADLINE', 'NO_APPLICABLE_POLICY', 'REPEATED_REOPEN', 'SLA_BREACH_IMMINENT')),
  threshold_value REAL,
  threshold_unit TEXT CHECK (threshold_unit IN ('DAYS', 'REOPENS', 'PERCENT')),
  target_team_id TEXT NOT NULL,
  description TEXT NOT NULL,
  PRIMARY KEY (escalation_rule_id),
  FOREIGN KEY (target_team_id) REFERENCES team(team_id)
);

CREATE TABLE policy_document (
  policy_id TEXT NOT NULL,
  domain TEXT NOT NULL CHECK (domain IN ('FINAID', 'REG', 'IT', 'ACC')),
  title TEXT NOT NULL,
  owner_team_id TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY (policy_id),
  FOREIGN KEY (owner_team_id) REFERENCES team(team_id)
);

CREATE TABLE policy_version (
  policy_version_id TEXT NOT NULL,
  policy_id TEXT NOT NULL,
  version_no INTEGER NOT NULL,
  effective_from TEXT NOT NULL,
  effective_to TEXT,
  lifecycle_status TEXT NOT NULL CHECK (lifecycle_status IN ('DRAFT', 'CURRENT', 'SUPERSEDED', 'EXPIRED')),
  summary_text TEXT NOT NULL,
  supersedes_version_id TEXT,
  PRIMARY KEY (policy_version_id),
  FOREIGN KEY (policy_id) REFERENCES policy_document(policy_id),
  FOREIGN KEY (supersedes_version_id) REFERENCES policy_version(policy_version_id)
);

CREATE TABLE knowledge_article (
  article_id TEXT NOT NULL,
  policy_version_id TEXT NOT NULL,
  article_version INTEGER NOT NULL,
  domain TEXT NOT NULL CHECK (domain IN ('FINAID', 'REG', 'IT', 'ACC')),
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  audience_role_id TEXT,
  status TEXT NOT NULL CHECK (status IN ('DRAFT', 'PUBLISHED', 'RETIRED')),
  effective_from TEXT NOT NULL,
  effective_to TEXT,
  supersedes_article_id TEXT,
  PRIMARY KEY (article_id),
  FOREIGN KEY (policy_version_id) REFERENCES policy_version(policy_version_id),
  FOREIGN KEY (audience_role_id) REFERENCES role(role_id),
  FOREIGN KEY (supersedes_article_id) REFERENCES knowledge_article(article_id)
);

CREATE TABLE ticket (
  ticket_id TEXT NOT NULL,
  requester_id TEXT NOT NULL,
  category_id TEXT NOT NULL,
  term_id TEXT,
  channel TEXT NOT NULL CHECK (channel IN ('PORTAL', 'EMAIL', 'CHAT', 'PHONE')),
  priority TEXT NOT NULL CHECK (priority IN ('LOW', 'NORMAL', 'HIGH', 'URGENT')),
  subject TEXT NOT NULL,
  created_at TEXT NOT NULL,
  deadline_date TEXT,
  current_status TEXT NOT NULL CHECK (current_status IN ('NEW', 'TRIAGED', 'ASSIGNED', 'IN_PROGRESS', 'PENDING_REQUESTER', 'ESCALATED', 'RESOLVED', 'REOPENED', 'CLOSED')),
  closed_at TEXT,
  PRIMARY KEY (ticket_id),
  FOREIGN KEY (requester_id) REFERENCES requester(requester_id),
  FOREIGN KEY (category_id) REFERENCES category(category_id),
  FOREIGN KEY (term_id) REFERENCES term(term_id)
);

CREATE TABLE ticket_status_event (
  event_id TEXT NOT NULL,
  ticket_id TEXT NOT NULL,
  seq INTEGER NOT NULL,
  from_status TEXT CHECK (from_status IN ('NEW', 'TRIAGED', 'ASSIGNED', 'IN_PROGRESS', 'PENDING_REQUESTER', 'ESCALATED', 'RESOLVED', 'REOPENED', 'CLOSED')),
  to_status TEXT NOT NULL CHECK (to_status IN ('NEW', 'TRIAGED', 'ASSIGNED', 'IN_PROGRESS', 'PENDING_REQUESTER', 'ESCALATED', 'RESOLVED', 'REOPENED', 'CLOSED')),
  event_at TEXT NOT NULL,
  actor_ref TEXT NOT NULL,
  reason TEXT,
  PRIMARY KEY (event_id),
  FOREIGN KEY (ticket_id) REFERENCES ticket(ticket_id)
);

CREATE TABLE message (
  message_id TEXT NOT NULL,
  ticket_id TEXT NOT NULL,
  seq INTEGER NOT NULL,
  sender_type TEXT NOT NULL CHECK (sender_type IN ('REQUESTER', 'STAFF', 'AI_ASSISTANT', 'SYSTEM')),
  sender_ref TEXT,
  message_type TEXT NOT NULL CHECK (message_type IN ('QUESTION', 'CLARIFICATION_REQUEST', 'CLARIFICATION_REPLY', 'ANSWER', 'INTERNAL_NOTE', 'ESCALATION_NOTICE', 'RESOLUTION', 'FOLLOW_UP')),
  body TEXT NOT NULL,
  sent_at TEXT NOT NULL,
  PRIMARY KEY (message_id),
  FOREIGN KEY (ticket_id) REFERENCES ticket(ticket_id)
);

CREATE TABLE message_citation (
  message_id TEXT NOT NULL,
  article_id TEXT NOT NULL,
  citation_order INTEGER NOT NULL,
  article_version_cited INTEGER NOT NULL,
  PRIMARY KEY (message_id, article_id),
  FOREIGN KEY (message_id) REFERENCES message(message_id),
  FOREIGN KEY (article_id) REFERENCES knowledge_article(article_id)
);

CREATE TABLE assignment (
  assignment_id TEXT NOT NULL,
  ticket_id TEXT NOT NULL,
  seq INTEGER NOT NULL,
  team_id TEXT NOT NULL,
  staff_id TEXT,
  assignment_type TEXT NOT NULL CHECK (assignment_type IN ('INITIAL', 'REROUTE', 'ESCALATION')),
  routing_rule_id TEXT,
  assigned_at TEXT NOT NULL,
  ended_at TEXT,
  PRIMARY KEY (assignment_id),
  FOREIGN KEY (ticket_id) REFERENCES ticket(ticket_id),
  FOREIGN KEY (team_id) REFERENCES team(team_id),
  FOREIGN KEY (staff_id) REFERENCES staff_member(staff_id),
  FOREIGN KEY (routing_rule_id) REFERENCES routing_rule(routing_rule_id)
);

CREATE TABLE sla (
  sla_id TEXT NOT NULL,
  ticket_id TEXT NOT NULL UNIQUE,
  sla_policy_id TEXT NOT NULL,
  start_at TEXT NOT NULL,
  first_response_due_at TEXT NOT NULL,
  resolution_due_at TEXT NOT NULL,
  first_response_at TEXT,
  resolved_at TEXT,
  first_response_breached INTEGER NOT NULL CHECK (first_response_breached IN (0,1)),
  resolution_breached INTEGER NOT NULL CHECK (resolution_breached IN (0,1)),
  PRIMARY KEY (sla_id),
  FOREIGN KEY (ticket_id) REFERENCES ticket(ticket_id),
  FOREIGN KEY (sla_policy_id) REFERENCES sla_policy(sla_policy_id)
);

CREATE TABLE resolution_feedback (
  feedback_id TEXT NOT NULL,
  ticket_id TEXT NOT NULL UNIQUE,
  rating INTEGER NOT NULL CHECK (rating IN (1, 2, 3, 4, 5)),
  resolved_first_contact INTEGER NOT NULL CHECK (resolved_first_contact IN (0,1)),
  comment TEXT,
  submitted_at TEXT NOT NULL,
  PRIMARY KEY (feedback_id),
  FOREIGN KEY (ticket_id) REFERENCES ticket(ticket_id)
);
