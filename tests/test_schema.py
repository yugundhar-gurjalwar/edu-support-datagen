import sqlite3

import pytest

from edusupport import config as C
from edusupport.schema import BY_TABLE, ENTITIES, full_ddl, ordered

REQUIRED_CORE = {"requester", "role", "term", "policy_document", "knowledge_article", "ticket",
                 "message", "category", "assignment", "sla", "resolution_feedback"}


def test_core_entities_present():
    assert REQUIRED_CORE <= set(BY_TABLE)


def test_every_entity_has_pk_and_unique_field_names():
    assert len(BY_TABLE) == len(ENTITIES)
    for e in ENTITIES:
        assert any(f.pk for f in e.fields), e.table
        names = [f.name for f in e.fields]
        assert len(names) == len(set(names)), e.table


def test_every_fk_target_exists_and_is_a_pk():
    for e in ENTITIES:
        for f in e.fields:
            if f.fk:
                t, c = f.fk.split(".")
                assert t in BY_TABLE, f"{e.table}.{f.name}"
                assert any(x.name == c and x.pk for x in BY_TABLE[t].fields), f"{e.table}.{f.name}->{f.fk}"


def test_ground_truth_not_referenced_by_input_tables():
    for e in ENTITIES:
        for f in e.fields:
            assert not f.fk.startswith("ground_truth"), e.table


def test_ddl_loads_with_foreign_keys_on():
    con = sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys=ON")
    con.executescript(full_ddl(include_ground_truth=True))
    names = {r[0] for r in con.execute("select name from sqlite_master where type='table'")}
    assert names == set(BY_TABLE)
    assert con.execute("PRAGMA foreign_key_check").fetchall() == []


def test_parents_ordered_before_children():
    seen = set()
    for e in ordered(ENTITIES):
        for f in e.fields:
            if f.fk and f.fk.split(".")[0] != e.table:
                assert f.fk.split(".")[0] in seen
        seen.add(e.table)


def test_enum_constraint_enforced():
    con = sqlite3.connect(":memory:")
    con.executescript(full_ddl())
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO role VALUES ('ROLE-X','NOPE',1,1)")


def test_lifecycle_closed_over_statuses():
    assert set(C.TRANSITIONS) == set(C.TICKET_STATUSES)
    for nxt in C.TRANSITIONS.values():
        assert set(nxt) <= set(C.TICKET_STATUSES)


def test_scale_presets():
    full = C.Scale.full()
    assert (full.tickets, full.articles, full.messages, full.seed) == (5000, 200, 20000, 20261022)
    assert C.Scale.starter().tickets < full.tickets
