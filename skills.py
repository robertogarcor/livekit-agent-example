"""
Agent-Live - Descubrimiento y carga de skills locales.

Las skills viven como archivos Markdown en `.agents/.skills/<name>/SKILL.md`.
Cada archivo incluye front matter YAML entre --- y --- con los campos:
  - name: identificador de la skill (opcional, por defecto el nombre del dir)
  - description: descripcion corta (obligatorio)

Expone:
  - build_skills_block(): genera el bloque que se inyecta en el prompt.
  - get_skill_content(name): lee el SKILL.md bajo demanda con cache.
  - list_available_skills(): devuelve los nombres de skills en disco.
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger("Agent_Live.skills")

SKILLS_DIR: Path = Path(__file__).resolve().parent / ".agents" / ".skills"
_content_cache: dict[str, str] = {}


def _parse_front_matter(text: str) -> dict[str, str]:
    """Extrae front matter YAML ``key: value`` entre --- y ---."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    end = 1
    while end < len(lines) and lines[end].strip() != "---":
        end += 1
    if end >= len(lines):
        return {}

    result: dict[str, str] = {}
    for line in lines[1:end]:
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if key and value:
            result[key] = value
    return result


def list_available_skills() -> list[str]:
    """Devuelve los nombres de las skills en disco."""
    if not SKILLS_DIR.is_dir():
        return []
    return sorted(
        entry.name
        for entry in SKILLS_DIR.iterdir()
        if entry.is_dir() and (entry / "SKILL.md").is_file()
    )


def get_skill_content(name: str) -> str | None:
    """
    Lee el contenido de SKILL.md de la skill solicitada.

    Cachea en memoria para evitar I/O en cada tool call.
    """
    if name in _content_cache:
        return _content_cache[name]

    skill_path = SKILLS_DIR / name / "SKILL.md"
    if not skill_path.is_file():
        logger.warning(f"Skill '{name}' no encontrada en {skill_path}")
        return None

    try:
        text = skill_path.read_text(encoding="utf-8")
    except OSError as e:
        logger.error(f"Error leyendo skill '{name}': {e}")
        return None

    _content_cache[name] = text
    logger.info(f"Skill '{name}' cargada ({len(text)} chars)")
    return text


def build_skills_block() -> str:
    """
    Construye el bloque 'SKILLS DISPONIBLES' que se inyecta
    al final del system prompt del agente.
    """
    if not SKILLS_DIR.is_dir():
        return ""

    skills: list[tuple[str, str]] = []
    for entry in sorted(SKILLS_DIR.iterdir()):
        if not entry.is_dir():
            continue
        skill_path = entry / "SKILL.md"
        if not skill_path.is_file():
            continue
        try:
            raw = skill_path.read_text(encoding="utf-8")
        except OSError:
            continue
        fm = _parse_front_matter(raw)
        name = entry.name
        description = fm.get("description", name)
        skills.append((name, description))

    if not skills:
        return ""

    lines = ["## SKILLS DISPONIBLES"]
    for name, desc in skills:
        lines.append(f"- {name}: {desc}")
    lines.append("")
    lines.append(
        "Si la consulta del usuario encaja con una skill, usa la "
        "herramienta get_skill(name) para cargar el manual completo "
        "antes de responder."
    )
    logger.info(f"Skills descubiertas: {[s[0] for s in skills]}")
    return "\n".join(lines)
