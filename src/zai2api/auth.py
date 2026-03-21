from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import time
from typing import Literal

from fastapi import Request

from .config import DEFAULT_PANEL_PASSWORD, Settings
from .db import Database

PANEL_PASSWORD_KEY = "panel_password_hash"
API_PASSWORD_KEY = "api_password_hash"
HASH_ITERATIONS = 120_000

PasswordSource = Literal["env", "database", "default", "disabled"]


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, HASH_ITERATIONS)
    return "pbkdf2_sha256${iterations}${salt}${digest}".format(
        iterations=HASH_ITERATIONS,
        salt=base64.urlsafe_b64encode(salt).decode(),
        digest=base64.urlsafe_b64encode(digest).decode(),
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations_text, salt_b64, digest_b64 = stored_hash.split("$", 3)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    try:
        iterations = int(iterations_text)
        salt = base64.urlsafe_b64decode(salt_b64.encode())
        expected = base64.urlsafe_b64decode(digest_b64.encode())
    except Exception:
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return hmac.compare_digest(actual, expected)


class AuthService:
    def __init__(self, settings: Settings, db: Database):
        self.settings = settings
        self.db = db

    def panel_password_source(self) -> PasswordSource:
        if self.settings.panel_password_env:
            return "env"
        if self.db.get_setting(PANEL_PASSWORD_KEY):
            return "database"
        return "default"

    def api_password_source(self) -> PasswordSource:
        if self.settings.api_password_env:
            return "env"
        if self.db.get_setting(API_PASSWORD_KEY):
            return "database"
        return "disabled"

    def is_api_auth_enabled(self) -> bool:
        return self.api_password_source() != "disabled"

    def verify_panel_password(self, password: str) -> bool:
        if self.settings.panel_password_env is not None:
            return hmac.compare_digest(password, self.settings.panel_password_env)
        stored_hash = self.db.get_setting(PANEL_PASSWORD_KEY)
        if stored_hash:
            return verify_password(password, stored_hash)
        return hmac.compare_digest(password, DEFAULT_PANEL_PASSWORD)

    def verify_api_password(self, password: str) -> bool:
        if not self.is_api_auth_enabled():
            return True
        if self.settings.api_password_env is not None:
            return hmac.compare_digest(password, self.settings.api_password_env)
        stored_hash = self.db.get_setting(API_PASSWORD_KEY)
        if not stored_hash:
            return False
        return verify_password(password, stored_hash)

    def update_panel_password(self, password: str) -> None:
        self.db.set_setting(PANEL_PASSWORD_KEY, hash_password(password))

    def update_api_password(self, password: str | None) -> None:
        if password:
            self.db.set_setting(API_PASSWORD_KEY, hash_password(password))
            return
        self.db.delete_setting(API_PASSWORD_KEY)

    def create_admin_session(self) -> tuple[str, int]:
        session_id = secrets.token_urlsafe(32)
        expires_at = int(time.time()) + self.settings.admin_session_ttl_seconds
        self.db.create_admin_session(session_id, expires_at)
        return session_id, expires_at

    def verify_admin_session(self, session_id: str | None) -> bool:
        if not session_id:
            return False
        self.db.delete_expired_admin_sessions()
        session = self.db.get_admin_session(session_id)
        return session is not None

    def delete_admin_session(self, session_id: str | None) -> None:
        if not session_id:
            return
        self.db.delete_admin_session(session_id)

    def extract_api_password(self, request: Request) -> str | None:
        auth_header = request.headers.get("authorization")
        if auth_header:
            scheme, _, value = auth_header.partition(" ")
            if scheme.lower() == "bearer" and value:
                return value.strip()
        x_api_key = request.headers.get("x-api-key")
        if x_api_key:
            return x_api_key.strip()
        return None
