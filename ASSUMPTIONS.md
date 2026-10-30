# Assumptions & Decisions (living document)

| # | Topic | Decision | Why |
|---|---|---|---|
| A1 | Extra tables | Added team, staff_member, team_category_authorization, policy_version, message_citation, ticket_status_event, routing_rule, escalation_rule, sla_policy, business_calendar, ground_truth | The brief's 11 entities cannot express "unauthorized team", "article version recorded", "cites expired policy", event history or SLA rules without them |
| A2 | ID formats | `MSG-TKT-2026-000001-001`, `SLA-TKT-2026-000001` (literal substitution of `<ticket-id>`). Other IDs follow the same zero-padded style | Brief mandates patterns only for 5 IDs |
| A3 | Time zone | All timestamps are campus-local IST, naive `YYYY-MM-DD HH:MM:SS` | Business-hours math stays simple and deterministic |
| A4 | Business hours | Mon-Fri 09:00-17:00 plus a small synthetic holiday list in `business_calendar` | Needed for the "SLA ignores business hours" anomaly |
| A5 | Data provenance | 100% synthetic; no external data, no real PII, emails use `@example.edu` | Avoids licensing/PII risk; source manifest will say "none" |
| A6 | Ticket labels | `ticket` holds only observable fields. True category, ambiguity, urgency and escalation expectation live in `ground_truth` | Prevents label leakage |
| A7 | current_status | Stored on ticket but DERIVED from the latest `ticket_status_event`; validator reconciles | "Do not overwrite history" |
| A8 | Generator uses no LLM | Rule-based + seeded `random.Random` only | Exact reproducibility |
| A9 | Polymorphic sender_ref | `message.sender_ref` has no FK (requester or staff); validator checks it by `sender_type` | One column cannot FK two tables |
| A10 | Anomaly rate | Target ~2-4% of tickets, spread over the 5 types | Realistic: edge cases rare but present |
