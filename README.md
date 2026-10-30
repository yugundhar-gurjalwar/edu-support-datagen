# Education Support Workflow - Synthetic Data Generator

Deterministic, seed-controlled generator for a student/faculty support workflow
(routing, policy-grounded answers, SLA tracking, escalation) with labelled
anomalies, a separate ground-truth file and a validation suite.

**Status:** Phase 1 complete (schema, data dictionary, ID helpers, tests). Generator phases in progress.

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m edusupport.docs_builder   # regenerates sql/ and docs/ from the schema
pytest -q
```

## Layout
- `src/edusupport/config.py` - seed, scale presets, enums, lifecycle rules
- `src/edusupport/ids.py` - deterministic ID builders + regex patterns
- `src/edusupport/schema.py` - single source of truth for all entities
- `docs/DATA_DICTIONARY.md`, `docs/ER_DIAGRAM.md`, `sql/schema.sql` - generated from the schema
- `ASSUMPTIONS.md`, `docs/AI_USAGE.md`, `prompts/PROMPT_LOG.md` - submission artifacts

## Roadmap
- [x] Phase 0-1: repo, config, IDs, schema, dictionary, tests
- [ ] Phase 2: master data + rules + calendar
- [ ] Phase 3: policies, versions, articles
- [ ] Phase 4: tickets, messages, events, SLA, feedback
- [ ] Phase 5: anomaly injection + ground truth
- [ ] Phase 6: validator + reproducibility check
- [ ] Phase 7: export (CSV/JSON/SQL) + manifest
- [ ] Phase 8 (stretch): router + retrieval + grounding checker + evaluation
