from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Iterable

TEXT_BLOCK_TYPES = {"text", "input_text", "output_text"}
IMAGE_MARKDOWN_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


@dataclass(slots=True)
class PromptMessage:
    role: str
    content: str


def assemble_prompt(messages: Iterable[dict[str, Any]]) -> str:
    normalized = normalize_messages(messages)
    merged = merge_adjacent_same_role(normalized)
    return render_prompt(merged)


def normalize_messages(messages: Iterable[dict[str, Any]]) -> list[PromptMessage]:
    normalized: list[PromptMessage] = []
    tool_call_fallback_index = 1

    for message in messages:
        role = normalize_role(message.get("role"))
        text_content = normalize_markdown_images(extract_text_content(message.get("content")))

        if role == "assistant":
            parts: list[str] = []
            if text_content:
                parts.append(text_content)
            for tool_call in iter_assistant_tool_calls(message):
                parts.append(format_tool_call_history(tool_call, tool_call_fallback_index))
                tool_call_fallback_index += 1
            if parts:
                normalized.append(PromptMessage(role="assistant", content="\n\n".join(parts)))
            continue

        if role in {"tool", "function"}:
            normalized.append(
                PromptMessage(role="user", content=format_tool_result_history(message, text_content))
            )
            continue

        if text_content:
            normalized.append(PromptMessage(role=role, content=text_content))

    return normalized


def merge_adjacent_same_role(messages: Iterable[PromptMessage]) -> list[PromptMessage]:
    merged: list[PromptMessage] = []
    for message in messages:
        if merged and merged[-1].role == message.role:
            merged[-1] = PromptMessage(
                role=message.role,
                content=f"{merged[-1].content}\n\n{message.content}",
            )
        else:
            merged.append(message)
    return merged


def render_prompt(messages: Iterable[PromptMessage]) -> str:
    rendered: list[str] = []
    first_non_assistant = True

    for message in messages:
        if message.role == "assistant":
            rendered.append(f"<｜Assistant｜>{message.content}<｜end▁of▁sentence｜>")
            continue

        if first_non_assistant:
            rendered.append(message.content)
            first_non_assistant = False
        else:
            rendered.append(f"<｜User｜>{message.content}")

    return "\n\n".join(part for part in rendered if part).strip()


def normalize_role(role: Any) -> str:
    role_str = str(role or "user").strip().lower()
    if role_str == "developer":
        return "system"
    if role_str in {"system", "user", "assistant", "tool", "function"}:
        return role_str
    return "user"


def extract_text_content(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") not in TEXT_BLOCK_TYPES:
                continue
            value = block.get("text")
            if value is None:
                value = block.get("content")
            if value is not None:
                parts.append(str(value))
        return "\n".join(parts)
    return str(content)


def iter_assistant_tool_calls(message: dict[str, Any]) -> list[dict[str, Any]]:
    tool_calls = message.get("tool_calls")
    if isinstance(tool_calls, list):
        return [call for call in tool_calls if isinstance(call, dict)]

    function_call = message.get("function_call")
    if isinstance(function_call, dict):
        return [{"id": message.get("id"), "type": "function", "function": function_call}]
    return []


def format_tool_call_history(tool_call: dict[str, Any], fallback_index: int) -> str:
    function = tool_call.get("function") if isinstance(tool_call.get("function"), dict) else {}
    tool_call_id = tool_call.get("id") or f"call_{fallback_index}"
    name = function.get("name") or tool_call.get("name") or "unknown"
    raw_arguments = function.get("arguments")
    if raw_arguments is None:
        raw_arguments = tool_call.get("arguments")
    if raw_arguments is None:
        raw_arguments = tool_call.get("input")
    arguments = normalize_argument_string(raw_arguments)
    return (
        "[TOOL_CALL_HISTORY]\n"
        "status: already_called\n"
        "origin: assistant\n"
        "not_user_input: true\n"
        f"tool_call_id: {tool_call_id}\n"
        f"function.name: {name}\n"
        f"function.arguments: {arguments}\n"
        "[/TOOL_CALL_HISTORY]"
    )


def format_tool_result_history(message: dict[str, Any], text_content: str) -> str:
    tool_call_id = message.get("tool_call_id") or message.get("id") or "unknown"
    name = message.get("name") or message.get("tool_name") or "unknown"
    content = text_content if text_content else "null"
    return (
        "[TOOL_RESULT_HISTORY]\n"
        "status: already_returned\n"
        "origin: tool_runtime\n"
        "not_user_input: true\n"
        f"tool_call_id: {tool_call_id}\n"
        f"name: {name}\n"
        f"content: {content}\n"
        "[/TOOL_RESULT_HISTORY]"
    )


def normalize_argument_string(value: Any) -> str:
    if value is None:
        return "{}"
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return "{}"
        if _looks_like_concatenated_json_fragments(stripped):
            return value
        return stripped
    if isinstance(value, (dict, list, int, float, bool)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def _looks_like_concatenated_json_fragments(value: str) -> bool:
    return value.startswith("{") and value.endswith("}") and "}{" in value


def normalize_markdown_images(text: str) -> str:
    return IMAGE_MARKDOWN_RE.sub(r"[\1](\2)", text)
