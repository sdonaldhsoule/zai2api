from __future__ import annotations

from pathlib import Path

from zai2api.config import Settings


def make_settings(tmp_path: Path, **overrides: object) -> Settings:
    base = Settings(
        host="127.0.0.1",
        port=8000,
        log_level="info",
        zai_base_url="https://chat.z.ai",
        zai_jwt=None,
        zai_session_token=None,
        default_model="glm-5",
        request_timeout=120.0,
        database_path=str(tmp_path / "state.db"),
        panel_password_env=None,
        api_password_env=None,
        admin_cookie_name="zai2api_admin_session",
        admin_session_ttl_hours=24,
        admin_cookie_secure=False,
    )
    for key, value in overrides.items():
        setattr(base, key, value)
    return base
