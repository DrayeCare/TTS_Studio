"""Filesystem persistence, backup and recovery tests."""

import json

import pytest

from core.game_controller import GameController
from models.question import Question
from services import session_service
from services.session_service import (
    SessionError,
    archive_current_session,
    load_session,
    save_session,
    serialize_session,
)


def state_with(title="Awal", team_name="Alpha", score=10):
    controller = GameController()
    controller.load_question_set(
        title,
        [Question(id="q1", number=1, category="Umum", question="Q?", answer="A")],
    )
    controller.add_team(team_name, score)
    return controller.state


def write_json(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


def test_save_creates_parent_directory_and_primary(tmp_path):
    path = tmp_path / "nested" / "session.json"

    save_session(path, state_with())

    assert path.exists()
    assert load_session(path).source == "primary"
    assert list(tmp_path.rglob("*.tmp")) == []


def test_second_save_keeps_previous_valid_session_as_backup(tmp_path):
    path = tmp_path / "session.json"

    save_session(path, state_with(title="Pertama", score=10))
    save_session(path, state_with(title="Kedua", score=20))

    result = load_session(path)
    assert result.state.title == "Kedua"
    backup = load_session(path.with_name("session.backup.json"))
    assert backup.source == "primary"
    assert backup.state.title == "Pertama"


def test_missing_primary_and_backup_returns_fresh(tmp_path):
    result = load_session(tmp_path / "session.json")

    assert result.source == "none"
    assert result.state is None
    assert "baru" in result.message.lower()


def test_corrupt_primary_recovers_from_backup_and_preserves_damage(tmp_path):
    path = tmp_path / "session.json"
    save_session(path, state_with(title="Pertama", score=10))
    save_session(path, state_with(title="Kedua", score=20))
    path.write_text("{ rusak", encoding="utf-8")

    result = load_session(path)

    assert result.source == "backup"
    assert result.state.title == "Pertama"
    assert "cadangan" in result.message.lower()
    assert len(result.damaged) == 1
    assert ".damaged-" in result.damaged[0].name
    assert result.damaged[0].exists()
    assert "{ rusak" in result.damaged[0].read_text(encoding="utf-8")


def test_both_files_corrupt_falls_back_to_fresh_and_preserves_both(tmp_path):
    path = tmp_path / "session.json"
    backup = path.with_name("session.backup.json")
    path.write_text("{ rusak", encoding="utf-8")
    backup.write_text("[]", encoding="utf-8")

    result = load_session(path)

    assert result.source == "none"
    assert result.state is None
    assert len(result.damaged) == 2
    assert all(item.exists() for item in result.damaged)


def test_invalid_schema_version_is_treated_as_corrupt(tmp_path):
    path = tmp_path / "session.json"
    data = json.loads(json.dumps(serialize_session(state_with())))
    data["schema_version"] = 99
    write_json(path, data)

    result = load_session(path)

    assert result.source == "none"
    assert "tidak didukung" in result.message.lower() or "rusak" in result.message.lower()


def test_load_survives_permission_error_on_primary(monkeypatch, tmp_path):
    path = tmp_path / "session.json"
    save_session(path, state_with(title="Pertama", score=10))
    save_session(path, state_with(title="Kedua", score=20))

    original_read_text = session_service.Path.read_text

    def denied(self, *args, **kwargs):
        if self == path:
            raise PermissionError("akses ditolak")
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(session_service.Path, "read_text", denied)

    result = load_session(path)

    assert result.source == "backup"
    assert result.state.title == "Pertama"
    assert len(result.damaged) == 1


def test_failed_replace_preserves_existing_session_and_backup(monkeypatch, tmp_path):
    path = tmp_path / "session.json"
    backup = path.with_name("session.backup.json")
    save_session(path, state_with(title="Awal", score=10))
    save_session(path, state_with(title="Kedua", score=11))
    before_primary = path.read_bytes()
    before_backup = backup.read_bytes()

    def denied(source, target):
        raise OSError("akses ditolak")

    monkeypatch.setattr(session_service.os, "replace", denied)

    with pytest.raises(SessionError, match="mengganti"):
        save_session(path, state_with(title="Baru", score=50))

    assert path.read_bytes() == before_primary
    assert backup.read_bytes() == before_backup
    assert list(tmp_path.rglob("*.tmp")) == []


def test_failed_backup_write_aborts_primary_replacement(monkeypatch, tmp_path):
    path = tmp_path / "session.json"
    save_session(path, state_with(title="Awal", score=10))
    before_primary = path.read_bytes()

    real_write = session_service._write_and_sync

    def selective_write(target, data):
        if target.name == "session.backup.json":
            raise SessionError("gagal menulis cadangan")
        return real_write(target, data)

    monkeypatch.setattr(session_service, "_write_and_sync", selective_write)

    with pytest.raises(SessionError, match="cadangan"):
        save_session(path, state_with(title="Baru", score=50))

    assert path.read_bytes() == before_primary
    assert list(tmp_path.rglob("*.tmp")) == []


def test_failed_new_write_does_not_touch_existing_files(monkeypatch, tmp_path):
    path = tmp_path / "session.json"
    save_session(path, state_with(title="Awal", score=10))
    before = path.read_bytes()

    monkeypatch.setattr(
        session_service,
        "_write_and_sync",
        lambda target, data: (_ for _ in ()).throw(SessionError("disk penuh")),
    )

    with pytest.raises(SessionError, match="disk penuh"):
        save_session(path, state_with(title="Baru", score=50))

    assert path.read_bytes() == before


def test_archive_keeps_recoverable_copy_before_fresh_session(tmp_path):
    path = tmp_path / "session.json"
    save_session(path, state_with(title="Penting", score=33))

    archive = archive_current_session(path)

    assert archive is not None
    assert archive.exists()
    assert ".previous-" in archive.name
    assert load_session(archive).state.title == "Penting"


def test_archive_ignores_corrupt_primary(tmp_path):
    path = tmp_path / "session.json"
    path.write_text("{ rusak", encoding="utf-8")

    assert archive_current_session(path) is None


def test_custom_backup_path_is_used(monkeypatch, tmp_path):
    path = tmp_path / "primary.json"
    backup = tmp_path / "custom_backup.json"

    save_session(path, state_with(title="Satu", score=1), backup_path=backup)
    save_session(path, state_with(title="Dua", score=2), backup_path=backup)

    result = load_session(path, backup_path=backup)
    assert result.state.title == "Dua"
    assert load_session(path, backup_path=backup).source == "primary"
    assert load_session(backup, backup_path=backup).state.title == "Satu"
