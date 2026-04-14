from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from zai2api.db import Database
from zai2api.server import create_app
from zai2api.zai_client import UpstreamChunk

from conftest import make_settings


class ErroringStreamPool:
    def __init__(self, *, mode: str):
        self.mode = mode

    async def collect_prompt(self, **_: object):
        raise AssertionError("collect_prompt should not be used in streaming tests")

    async def stream_prompt(self, **_: object):
        if self.mode == "chunk_error":
            yield UpstreamChunk(phase=None, text="", error="upstream said no")
            return
        raise RuntimeError("upstream stream exploded")


def test_chat_completion_stream_reports_error_in_band(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    app = create_app(settings, prompt_pool=ErroringStreamPool(mode="chunk_error"))

    with TestClient(app) as client:
        response = client.post(
            "/v1/chat/completions",
            json={"model": "glm-5", "stream": True, "messages": [{"role": "user", "content": "hi"}]},
        )

    assert response.status_code == 200
    assert '"type": "upstream_error"' in response.text
    assert '"message": "upstream said no"' in response.text
    assert "data: [DONE]" in response.text
    logs = Database(settings.database_path).list_logs(limit=20)
    assert any(item.message == "流式聊天补全请求失败" for item in logs)


def test_responses_stream_reports_runtime_error_in_band(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    app = create_app(settings, prompt_pool=ErroringStreamPool(mode="runtime_error"))

    with TestClient(app) as client:
        response = client.post(
            "/v1/responses",
            json={"model": "glm-5", "stream": True, "input": "hi"},
        )

    assert response.status_code == 200
    assert '"type": "response.failed"' in response.text
    assert '"status": "failed"' in response.text
    assert '"message": "upstream stream exploded"' in response.text
    assert "data: [DONE]" in response.text
    logs = Database(settings.database_path).list_logs(limit=20)
    assert any(item.message == "流式 Responses 请求失败" for item in logs)
