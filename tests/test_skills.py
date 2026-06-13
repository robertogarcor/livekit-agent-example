from pathlib import Path

import pytest

from skills import (
    _parse_front_matter,
    build_skills_block,
    get_skill_content,
    list_available_skills,
    SKILLS_DIR,
)


def _make_skill(tmp_path: Path, name: str, content: str) -> None:
    skill_dir = tmp_path / name
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")


class TestParseFrontMatter:
    def test_empty_text(self):
        assert _parse_front_matter("") == {}

    def test_no_front_matter(self):
        assert _parse_front_matter("# Solo contenido") == {}

    def test_unclosed(self):
        assert _parse_front_matter("---\nname: foo") == {}

    def test_basic(self):
        text = "---\nname: test-skill\ndescription: Skill de prueba.\n---"
        assert _parse_front_matter(text) == {
            "name": "test-skill",
            "description": "Skill de prueba.",
        }

    def test_only_dashes(self):
        assert _parse_front_matter("---\n---") == {}

    def test_extra_whitespace(self):
        text = "---\n  name:   test-skill  \n  description:   Skill de prueba  \n---"
        assert _parse_front_matter(text) == {
            "name": "test-skill",
            "description": "Skill de prueba",
        }

    def test_colon_in_value(self):
        text = "---\ndescription: Manual de test-skill.\n---"
        result = _parse_front_matter(text)
        assert result["description"] == "Manual de test-skill."

    def test_unknown_keys_are_returned(self):
        text = "---\nname: foo\nversion: 2\n---"
        result = _parse_front_matter(text)
        assert result == {"name": "foo", "version": "2"}


class TestListAvailableSkills:
    def test_empty_when_no_dir(self, monkeypatch):
        monkeypatch.setattr("skills.SKILLS_DIR", Path("/nonexistent/path"))
        assert list_available_skills() == []

    def test_returns_sorted_names(self, monkeypatch, tmp_path):
        monkeypatch.setattr("skills.SKILLS_DIR", tmp_path)
        _make_skill(tmp_path, "zzz", "---\n---")
        _make_skill(tmp_path, "aaa", "---\n---")
        assert list_available_skills() == ["aaa", "zzz"]

    def test_ignores_non_dirs(self, monkeypatch, tmp_path):
        monkeypatch.setattr("skills.SKILLS_DIR", tmp_path)
        _make_skill(tmp_path, "skill-a", "---\n---")
        (tmp_path / "not-a-dir.md").write_text("")
        assert list_available_skills() == ["skill-a"]

    def test_ignores_dirs_without_skill_md(self, monkeypatch, tmp_path):
        monkeypatch.setattr("skills.SKILLS_DIR", tmp_path)
        d = tmp_path / "empty-dir"
        d.mkdir()
        _make_skill(tmp_path, "real-skill", "---\n---")
        assert list_available_skills() == ["real-skill"]


class TestGetSkillContent:
    def test_returns_none_for_missing(self, monkeypatch, tmp_path):
        monkeypatch.setattr("skills.SKILLS_DIR", tmp_path)
        assert get_skill_content("nonexistent") is None

    def test_returns_content(self, monkeypatch, tmp_path):
        monkeypatch.setattr("skills.SKILLS_DIR", tmp_path)
        _make_skill(tmp_path, "test-skill", "---\nname: test-skill\n---\n# Content")
        content = get_skill_content("test-skill")
        assert content is not None
        assert "# Content" in content

    def test_caches_content(self, monkeypatch, tmp_path):
        monkeypatch.setattr("skills.SKILLS_DIR", tmp_path)
        _make_skill(tmp_path, "cached", "---\n---\nOriginal")
        assert get_skill_content("cached") is not None
        (tmp_path / "cached" / "SKILL.md").write_text("---\n---\nModified", encoding="utf-8")
        assert "Original" in get_skill_content("cached")


class TestBuildSkillsBlock:
    def test_empty_when_no_dir(self, monkeypatch):
        monkeypatch.setattr("skills.SKILLS_DIR", Path("/nonexistent/path"))
        assert build_skills_block() == ""

    def test_empty_when_no_skills(self, monkeypatch, tmp_path):
        monkeypatch.setattr("skills.SKILLS_DIR", tmp_path)
        assert build_skills_block() == ""

    def test_generates_block(self, monkeypatch, tmp_path):
        monkeypatch.setattr("skills.SKILLS_DIR", tmp_path)
        _make_skill(
            tmp_path,
            "test-skill",
            "---\nname: test-skill\ndescription: Skill de prueba.\n---\n# Content",
        )
        result = build_skills_block()
        assert "## SKILLS DISPONIBLES" in result
        assert "test-skill: Skill de prueba." in result
        assert "get_skill(name)" in result

    def test_multiple_skills(self, monkeypatch, tmp_path):
        monkeypatch.setattr("skills.SKILLS_DIR", tmp_path)
        _make_skill(tmp_path, "skill-a", "---\ndescription: First skill\n---")
        _make_skill(tmp_path, "skill-b", "---\ndescription: Second skill\n---")
        result = build_skills_block()
        assert "skill-a: First skill" in result
        assert "skill-b: Second skill" in result

    def test_fallback_description_to_name(self, monkeypatch, tmp_path):
        monkeypatch.setattr("skills.SKILLS_DIR", tmp_path)
        _make_skill(tmp_path, "fallback-skill", "---\n---")
        result = build_skills_block()
        assert "fallback-skill: fallback-skill" in result
