import asyncio

from livekit.agents import RunContext

from tools import get_skill, get_time, list_skills


class TestGetTime:
    def test_returns_time_string(self):
        result = asyncio.run(get_time(RunContext()))
        assert "Hora actual:" in result
        assert "Fecha:" in result


class TestListSkills:
    def test_empty(self, monkeypatch):
        monkeypatch.setattr("tools.list_available_skills", lambda: [])
        result = asyncio.run(list_skills(RunContext()))
        assert result == "No hay skills locales disponibles."

    def test_with_skills(self, monkeypatch):
        monkeypatch.setattr("tools.list_available_skills", lambda: ["a", "b"])
        result = asyncio.run(list_skills(RunContext()))
        assert result == "Skills disponibles: a, b"


class TestGetSkill:
    def test_found(self, monkeypatch):
        monkeypatch.setattr("tools.get_skill_content", lambda name: f"Content of {name}")
        result = asyncio.run(get_skill(RunContext(), "test-skill"))
        assert result == "Content of test-skill"

    def test_not_found(self, monkeypatch):
        monkeypatch.setattr("tools.get_skill_content", lambda name: None)
        result = asyncio.run(get_skill(RunContext(), "nonexistent"))
        assert result == "Skill 'nonexistent' no encontrada."
