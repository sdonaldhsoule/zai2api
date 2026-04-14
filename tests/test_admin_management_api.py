from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from zai2api.account_pool import AccountPool
from zai2api.db import Database
from zai2api.server import create_app
from zai2api.zai_client import SessionState, UpstreamResult

from conftest import make_settings


class FakeManagedClient:
    def __init__(self, *, identity: str):
        self.identity = identity

    async def ensure_session(self, force_refresh: bool = False) -> SessionState:
        return SessionState(
            token=f"session-{self.identity}",
            user_id=f"user-{self.identity}",
            name=self.identity,
            email=f"{self.identity}@example.com",
            role="user",
        )

    async def verify_completion_version(self) -> int:
        return 2

    async def collect_prompt(
        self,
        *,
        prompt: str,
        model: str,
        enable_thinking: bool,
        auto_web_search: bool,
    ) -> UpstreamResult:
        return UpstreamResult(
            answer_text=f"ok:{prompt}",
            reasoning_text="reasoning",
            usage={"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            finish_reason="stop",
        )

    async def stream_prompt(self, **_: object):
        if False:
            yield None

    async def aclose(self) -> None:
        return None


def build_client(tmp_path: Path) -> TestClient:
    settings = make_settings(tmp_path, account_poll_interval_seconds=0)
    db = Database(settings.database_path)
    pool = AccountPool(
        settings,
        db,
        client_factory=lambda jwt, session_token: FakeManagedClient(
            identity=(jwt or session_token or "fallback").replace("jwt-", "")
        ),
    )
    app = create_app(settings, account_pool=pool)
    return TestClient(app)


def login(client: TestClient) -> None:
    response = client.post("/api/admin/login", json={"password": "123456"})
    assert response.status_code == 200


def test_admin_can_add_list_and_toggle_accounts(tmp_path: Path) -> None:
    with build_client(tmp_path) as client:
        login(client)

        added = client.post("/api/admin/accounts", json={"jwt": "jwt-alpha"})
        assert added.status_code == 200
        account = added.json()["account"]
        assert account["email"] == "alpha@example.com"
        assert account["masked_jwt"] != "jwt-alpha"
        assert account["masked_jwt"] is not None

        listed = client.get("/api/admin/accounts")
        assert listed.status_code == 200
        assert len(listed.json()["accounts"]) == 1
        assert listed.json()["accounts"][0]["request_count"] == 0

        disabled = client.post(f"/api/admin/accounts/{account['id']}/disable")
        assert disabled.status_code == 200
        assert disabled.json()["account"]["enabled"] is False

        checked = client.post(f"/api/admin/accounts/{account['id']}/check")
        assert checked.status_code == 200
        assert checked.json()["account"]["status"] == "active"


def test_admin_add_account_requires_jwt_with_chinese_detail(tmp_path: Path) -> None:
    with build_client(tmp_path) as client:
        login(client)

        response = client.post("/api/admin/accounts", json={"jwt": ""})
        assert response.status_code == 400
        assert response.json()["detail"] == "缺少 JWT"


def test_admin_can_update_security_settings_and_read_logs(tmp_path: Path) -> None:
    with build_client(tmp_path) as client:
        login(client)

        updated = client.post(
            "/api/admin/settings/security",
            json={
                "panel_password": "new-panel",
                "api_password": "api-secret",
                "log_retention_days": 14,
            },
        )
        assert updated.status_code == 200
        payload = updated.json()
        assert payload["panel_password"]["source"] == "database"
        assert payload["api_password"]["enabled"] is True
        assert payload["log_retention"]["days"] == 14
        assert payload["log_retention"]["source"] == "database"

        client.post("/api/admin/logout")
        relogin = client.post("/api/admin/login", json={"password": "new-panel"})
        assert relogin.status_code == 200

        logs = client.get("/api/admin/logs?limit=20")
        assert logs.status_code == 200
        messages = [item["message"] for item in logs.json()["logs"]]
        assert "已更新安全设置" in messages


def test_openai_requests_are_written_to_audit_logs(tmp_path: Path) -> None:
    with build_client(tmp_path) as client:
        login(client)
        added = client.post("/api/admin/accounts", json={"jwt": "jwt-alpha"})
        assert added.status_code == 200

        models = client.get("/v1/models")
        assert models.status_code == 200

        completion = client.post(
            "/v1/chat/completions",
            json={"model": "glm-5", "messages": [{"role": "user", "content": "hello"}]},
        )
        assert completion.status_code == 200

        response_api = client.post(
            "/v1/responses",
            json={"model": "glm-5", "input": "hello"},
        )
        assert response_api.status_code == 200

        accounts = client.get("/api/admin/accounts")
        assert accounts.status_code == 200
        assert accounts.json()["accounts"][0]["request_count"] == 2

        logs = client.get("/api/admin/logs?limit=50")
        assert logs.status_code == 200
        messages = [item["message"] for item in logs.json()["logs"]]
        assert "已列出可用模型" in messages
        assert "聊天补全请求已完成" in messages
        assert "Responses 请求已完成" in messages
