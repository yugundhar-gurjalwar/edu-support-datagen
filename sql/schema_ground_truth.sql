CREATE TABLE ground_truth (
  ground_truth_id TEXT NOT NULL,
  entity_type TEXT NOT NULL CHECK (entity_type IN ('ticket', 'message', 'assignment', 'sla', 'message_citation')),
  entity_id TEXT NOT NULL,
  issue_type TEXT NOT NULL CHECK (issue_type IN ('EXPIRED_POLICY_CITED', 'UNAUTHORIZED_ROUTING', 'UNSUPPORTED_CLAIM', 'SLA_IGNORES_BUSINESS_HOURS', 'ESCALATION_NOT_TRIGGERED', 'AMBIGUOUS_REQUEST', 'URGENT_DEADLINE', 'NEEDS_HUMAN_ESCALATION', 'TRUE_CATEGORY')),
  is_injected INTEGER NOT NULL CHECK (is_injected IN (0,1)),
  violated_rule TEXT,
  expected_value TEXT,
  observed_value TEXT,
  notes TEXT,
  PRIMARY KEY (ground_truth_id)
);
