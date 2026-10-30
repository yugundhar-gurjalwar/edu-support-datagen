"""Generate sql/schema*.sql, docs/DATA_DICTIONARY.md and docs/ER_DIAGRAM.md
from the schema definition.  Run:  python -m edusupport.docs_builder
"""
from __future__ import annotations

from pathlib import Path

from . import config as C
from .schema import BY_TABLE, ENTITIES, ddl, full_ddl, ordered

ROOT = Path(__file__).resolve().parents[2]


def _cell(s: str) -> str:
    return str(s).replace("|", "\\|") if s else ""


def data_dictionary() -> str:
    out = [
        "# Data Dictionary",
        "",
        "_Generated from `src/edusupport/schema.py` by `python -m edusupport.docs_builder`. Do not edit by hand._",
        "",
        f"- Timestamps: ISO `YYYY-MM-DD HH:MM:SS`, {C.TIMEZONE_NOTE}.",
        "- Types: TEXT, INTEGER, REAL, BOOLEAN (0/1), DATE (`YYYY-MM-DD`), TIMESTAMP.",
        "- IDs are immutable and zero-padded; patterns are enforced by the validator.",
        "- `ground_truth` is stored separately and must never be used as an input feature.",
        "",
        "## Ticket lifecycle (allowed transitions)",
        "",
        "| From | Allowed next states |", "|---|---|",
    ]
    for k, v in C.TRANSITIONS.items():
        out.append(f"| {k} | {', '.join(v) or '(terminal)'} |")
    out.append("")
    for e in ordered(ENTITIES):
        out += [f"## `{e.table}`" + ("  (GROUND TRUTH, separate file)" if e.ground_truth else ""), "", e.description, ""]
        if e.cardinality:
            out.append("**Cardinality:** " + "; ".join(e.cardinality) + "  ")
        if e.lifecycle:
            out.append(f"**Lifecycle:** {e.lifecycle}  ")
        out += ["", "| Field | Type | Req | Allowed values / pattern | Unit | Unique | FK | Validation rule |",
                "|---|---|---|---|---|---|---|---|"]
        for f in e.fields:
            allowed = ", ".join(str(a) for a in f.allowed) if f.allowed else (f"`{f.pattern}`" if f.pattern else "")
            key = "PK " if f.pk else ""
            out.append(
                f"| {key}`{f.name}` | {f.type} | {'Y' if f.required else 'N'} | {_cell(allowed)} | {_cell(f.unit)} | "
                f"{'Y' if (f.unique or f.pk) else ''} | {_cell(f.fk)} | {_cell(f.rule)} |"
            )
        out.append("")
    return "\n".join(out)


def er_diagram() -> str:
    lines = ["# ER Diagram", "", "_Generated. Optional FKs use `|o`; bridge tables show 1:N from both parents._", "",
             "```mermaid", "erDiagram"]
    for e in ENTITIES:
        if e.ground_truth:
            continue
        for f in e.fields:
            if f.fk:
                parent = f.fk.split(".")[0]
                left = "||" if f.required else "|o"
                right = "o|" if f.unique else "o{"
                lines.append(f"    {parent} {left}--{right} {e.table} : \"{f.name}\"")
    lines += ["```", ""]
    return "\n".join(lines)


def build() -> list[Path]:
    targets = {
        ROOT / "sql" / "schema.sql": full_ddl(False),
        ROOT / "sql" / "schema_ground_truth.sql": ddl(BY_TABLE["ground_truth"]) + "\n",
        ROOT / "docs" / "DATA_DICTIONARY.md": data_dictionary(),
        ROOT / "docs" / "ER_DIAGRAM.md": er_diagram(),
    }
    for path, text in targets.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return list(targets)


if __name__ == "__main__":
    for p in build():
        print("wrote", p.relative_to(ROOT))
