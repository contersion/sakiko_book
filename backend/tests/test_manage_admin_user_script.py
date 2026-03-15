import os
from pathlib import Path
import subprocess
import sys

from sqlalchemy import select
from sqlalchemy.orm import Session

import app.models  # noqa: F401 - ensure models are imported before create_all
from app.core.database import Base, build_engine
from app.core.security import get_password_hash, verify_password
from app.models import User


BACKEND_DIR = Path(__file__).resolve().parents[1]
SCRIPT_PATH = BACKEND_DIR / "scripts" / "manage_admin_user.py"


def _create_database(tmp_path: Path):
    db_path = tmp_path / "reader.db"
    engine = build_engine(f"sqlite:///{db_path.as_posix()}")
    Base.metadata.create_all(bind=engine)
    return db_path, engine


def _insert_user(engine, username: str, password: str) -> None:
    with Session(bind=engine) as session:
        session.add(User(username=username, password_hash=get_password_hash(password)))
        session.commit()


def _load_user(engine, username: str) -> User | None:
    with Session(bind=engine) as session:
        return session.execute(select(User).where(User.username == username)).scalar_one_or_none()


def _run_script(
    db_path: Path,
    *,
    env_username: str,
    env_password: str,
    args: list[str] | None = None,
):
    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
    env["DEFAULT_ADMIN_USERNAME"] = env_username
    env["DEFAULT_ADMIN_PASSWORD"] = env_password

    command = [sys.executable, str(SCRIPT_PATH)]
    if args:
        command.extend(args)

    return subprocess.run(
        command,
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_manage_admin_user_resets_current_default_admin_password(tmp_path):
    db_path, engine = _create_database(tmp_path)
    _insert_user(engine, username="contersion", password="old-password")

    result = _run_script(
        db_path,
        env_username="contersion",
        env_password="env-password",
        args=["--password", "cli-password"],
    )

    assert result.returncode == 0
    assert "操作类型：reset password" in result.stdout
    assert "已找到默认管理员：contersion" in result.stdout
    assert "默认管理员密码已重置" in result.stdout

    user = _load_user(engine, "contersion")
    assert user is not None
    assert verify_password("cli-password", user.password_hash)
    assert not verify_password("old-password", user.password_hash)


def test_manage_admin_user_renames_legacy_admin_by_default_settings(tmp_path):
    db_path, engine = _create_database(tmp_path)
    _insert_user(engine, username="admin", password="old-password")

    result = _run_script(
        db_path,
        env_username="contersion",
        env_password="new-password-from-env",
    )

    assert result.returncode == 0
    assert "操作类型：rename admin" in result.stdout
    assert "找到旧默认管理员：admin" in result.stdout
    assert "默认管理员已改名：admin -> contersion" in result.stdout
    assert "默认管理员密码已同步更新" in result.stdout

    assert _load_user(engine, "admin") is None
    renamed_user = _load_user(engine, "contersion")
    assert renamed_user is not None
    assert verify_password("new-password-from-env", renamed_user.password_hash)
    assert not verify_password("old-password", renamed_user.password_hash)


def test_manage_admin_user_renames_admin_with_explicit_usernames(tmp_path):
    db_path, engine = _create_database(tmp_path)
    _insert_user(engine, username="admin", password="old-password")

    result = _run_script(
        db_path,
        env_username="ignored-env-user",
        env_password="ignored-env-password",
        args=[
            "--old-username",
            "admin",
            "--new-username",
            "contersion",
            "--password",
            "cli-password",
        ],
    )

    assert result.returncode == 0
    assert "操作类型：rename admin" in result.stdout
    assert "找到旧管理员用户：admin" in result.stdout
    assert "管理员用户名已更新：admin -> contersion" in result.stdout
    assert "管理员密码已同步更新" in result.stdout

    assert _load_user(engine, "admin") is None
    renamed_user = _load_user(engine, "contersion")
    assert renamed_user is not None
    assert verify_password("cli-password", renamed_user.password_hash)


def test_manage_admin_user_rejects_conflicting_new_username(tmp_path):
    db_path, engine = _create_database(tmp_path)
    _insert_user(engine, username="admin", password="old-password")
    _insert_user(engine, username="contersion", password="existing-password")

    result = _run_script(
        db_path,
        env_username="ignored-env-user",
        env_password="ignored-env-password",
        args=[
            "--old-username",
            "admin",
            "--new-username",
            "contersion",
            "--password",
            "cli-password",
        ],
    )

    assert result.returncode == 1
    assert "操作类型：rename admin" in result.stdout
    assert "操作失败：新管理员用户名已存在：contersion" in result.stdout

    original_user = _load_user(engine, "admin")
    assert original_user is not None
    assert verify_password("old-password", original_user.password_hash)

    existing_user = _load_user(engine, "contersion")
    assert existing_user is not None
    assert verify_password("existing-password", existing_user.password_hash)


def test_manage_admin_user_reports_missing_old_admin(tmp_path):
    db_path, _engine = _create_database(tmp_path)

    result = _run_script(
        db_path,
        env_username="ignored-env-user",
        env_password="ignored-env-password",
        args=[
            "--old-username",
            "admin",
            "--new-username",
            "contersion",
            "--password",
            "cli-password",
        ],
    )

    assert result.returncode == 1
    assert "操作类型：rename admin" in result.stdout
    assert "操作失败：未找到旧管理员用户：admin" in result.stdout
