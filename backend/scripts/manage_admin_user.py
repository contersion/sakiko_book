from __future__ import annotations

import argparse
from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core import database
from app.core.config import settings
from app.core.security import get_password_hash
from app.services.auth import get_user_by_username


LEGACY_DEFAULT_ADMIN_USERNAME = "admin"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manage the default admin user by resetting its password or renaming it.",
    )
    parser.add_argument("--old-username", help="Existing admin username to rename")
    parser.add_argument("--new-username", help="Target admin username after rename")
    parser.add_argument("--password", help="Override DEFAULT_ADMIN_PASSWORD")
    return parser.parse_args(argv)



def normalize_username(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip()
    return normalized or None



def resolve_credentials(args: argparse.Namespace) -> tuple[str | None, str | None, str]:
    old_username = normalize_username(args.old_username)
    new_username = normalize_username(args.new_username) or normalize_username(settings.default_admin_username)
    password = args.password if args.password is not None else settings.default_admin_password
    return old_username, new_username, password



def validate_request(args: argparse.Namespace, new_username: str | None, password: str) -> int | None:
    has_old_username = args.old_username is not None
    has_new_username = args.new_username is not None

    if has_old_username != has_new_username:
        print("操作失败：重命名操作需要同时提供 --old-username 和 --new-username")
        return 1

    if not new_username:
        print("操作失败：新管理员用户名为空")
        return 1

    if not password:
        print("操作失败：管理员密码为空")
        return 1

    return None



def reset_password(session, username: str, password: str, *, label: str, success_message: str) -> int:
    user = get_user_by_username(session, username)
    if user is None:
        print(f"操作失败：未找到管理员用户：{username}")
        return 1

    print("操作类型：reset password")
    print(f"已找到{label}：{username}")
    user.password_hash = get_password_hash(password)
    session.commit()
    print(success_message)
    return 0



def rename_admin(session, old_username: str, new_username: str, password: str) -> int:
    print("操作类型：rename admin")

    old_user = get_user_by_username(session, old_username)
    if old_user is None:
        print(f"操作失败：未找到旧管理员用户：{old_username}")
        return 1

    print(f"找到旧管理员用户：{old_username}")

    if old_username == new_username:
        old_user.password_hash = get_password_hash(password)
        session.commit()
        print("管理员用户名未变化，已按原用户名重置密码")
        print("管理员密码已同步更新")
        return 0

    conflicting_user = get_user_by_username(session, new_username)
    if conflicting_user is not None:
        print(f"操作失败：新管理员用户名已存在：{new_username}")
        return 1

    old_user.username = new_username
    old_user.password_hash = get_password_hash(password)
    session.commit()
    print(f"管理员用户名已更新：{old_username} -> {new_username}")
    print("管理员密码已同步更新")
    return 0



def manage_default_admin(session, new_username: str, password: str) -> int:
    current_admin = get_user_by_username(session, new_username)
    if current_admin is not None:
        print("操作类型：reset password")
        print(f"已找到默认管理员：{new_username}")
        current_admin.password_hash = get_password_hash(password)
        session.commit()
        print("默认管理员密码已重置")
        return 0

    if new_username != LEGACY_DEFAULT_ADMIN_USERNAME:
        legacy_admin = get_user_by_username(session, LEGACY_DEFAULT_ADMIN_USERNAME)
        if legacy_admin is not None:
            print("操作类型：rename admin")
            print(f"找到旧默认管理员：{LEGACY_DEFAULT_ADMIN_USERNAME}")
            legacy_admin.username = new_username
            legacy_admin.password_hash = get_password_hash(password)
            session.commit()
            print(f"默认管理员已改名：{LEGACY_DEFAULT_ADMIN_USERNAME} -> {new_username}")
            print("默认管理员密码已同步更新")
            return 0

    print(
        "操作失败：未找到当前默认管理员，"
        f"也未找到可重命名的旧默认管理员：{LEGACY_DEFAULT_ADMIN_USERNAME}"
    )
    return 1



def manage_admin_user(old_username: str | None, new_username: str, password: str) -> int:
    try:
        with database.session_scope() as session:
            if old_username is not None:
                return rename_admin(session, old_username, new_username, password)

            return manage_default_admin(session, new_username, password)
    except Exception as exc:
        print(f"操作失败：{exc}")
        return 1



def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    old_username, new_username, password = resolve_credentials(args)

    validation_error = validate_request(args, new_username, password)
    if validation_error is not None:
        return validation_error

    return manage_admin_user(old_username, new_username or "", password)


if __name__ == "__main__":
    raise SystemExit(main())
