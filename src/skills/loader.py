"""Deterministic two-tier skill loader.

The classifier decides the service line AND the engagement type explicitly, so we load
the matching SKILL.md deterministically off those two outputs — auditable and reproducible,
which matters for the readout's provenance and for evals. Path is built directly from the
enum values: skills/<service_line>/<engagement_type>/SKILL.md.

Because ServiceLine.value already equals the folder name (e.g. "audit-advisory"), there's
no translation table — the enum value IS the directory. Adding a service line = adding a
folder, no code change here.
"""
from __future__ import annotations
from pathlib import Path
from ..schemas import ServiceLine

_SKILL_DIR = Path(__file__).parent


def load_skill(service_line: ServiceLine, engagement_type: str) -> str:
    """Return the SKILL.md instruction text for a (service_line, engagement_type) pair.

    Frontmatter is stripped. If the skill file doesn't exist (e.g. a stubbed service line
    we haven't authored yet), return "" so the caller degrades to human review instead of
    crashing — keeping the spine's never-trash-a-real-opportunity posture.
    """
    skill_path = _SKILL_DIR / service_line.value / engagement_type / "SKILL.md"
    if not skill_path.exists():
        return ""
    text = skill_path.read_text(encoding="utf-8")
    # strip YAML frontmatter
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2].strip()
    return text