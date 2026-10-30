import pytest

from edusupport import ids


def test_mandated_formats():
    t = ids.ticket_id(1)
    assert t == "TKT-2026-000001"
    assert ids.message_id(t, 1) == "MSG-TKT-2026-000001-001"
    assert ids.article_id(1) == "KB-000001"
    assert ids.policy_id("FINAID", 1) == "POL-FINAID-2026-001"
    assert ids.sla_id(t) == "SLA-TKT-2026-000001"


@pytest.mark.parametrize("fn,pat", [
    (lambda: ids.ticket_id(4999), ids.P_TICKET),
    (lambda: ids.message_id(ids.ticket_id(5000), 12), ids.P_MESSAGE),
    (lambda: ids.article_id(200), ids.P_ARTICLE),
    (lambda: ids.policy_id("ACC", 12), ids.P_POLICY),
    (lambda: ids.policy_version_id(ids.policy_id("IT", 3), 2), ids.P_POLICY_VERSION),
    (lambda: ids.sla_id(ids.ticket_id(7)), ids.P_SLA),
    (lambda: ids.assignment_id(ids.ticket_id(7), 2), ids.P_ASSIGNMENT),
    (lambda: ids.event_id(ids.ticket_id(7), 3), ids.P_EVENT),
    (lambda: ids.feedback_id(ids.ticket_id(7)), ids.P_FEEDBACK),
])
def test_patterns_match_builders(fn, pat):
    assert ids.matches(pat, fn())


def test_bad_domain_rejected():
    with pytest.raises(ValueError):
        ids.policy_id("XYZ", 1)
