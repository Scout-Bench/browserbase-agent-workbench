from __future__ import annotations

import time
from typing import Any

import requests

from config import API_BASE, TERMINAL_STATUSES


class BrowserbaseAgentsClient:
    def __init__(self, api_key: str) -> None:
        self._session = requests.Session()
        self._session.headers.update(
            {
                "x-bb-api-key": api_key,
                "Content-Type": "application/json",
            }
        )

    def create_agent(
        self,
        name: str,
        system_prompt: str,
        result_schema: dict[str, Any],
    ) -> dict[str, Any]:
        response = self._session.post(
            f"{API_BASE}/agents",
            json={
                "name": name,
                "systemPrompt": system_prompt,
                "resultSchema": result_schema,
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def update_agent(
        self,
        agent_id: str,
        *,
        name: str | None = None,
        system_prompt: str | None = None,
        result_schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if system_prompt is not None:
            payload["systemPrompt"] = system_prompt
        if result_schema is not None:
            payload["resultSchema"] = result_schema

        response = self._session.patch(
            f"{API_BASE}/agents/{agent_id}",
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def run_agent(
        self,
        *,
        task: str,
        agent_id: str | None = None,
        variables: dict[str, dict[str, str]] | None = None,
        result_schema: dict[str, Any] | None = None,
        use_proxies: bool = True,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"task": task}
        if agent_id:
            payload["agentId"] = agent_id
        if variables:
            payload["variables"] = variables
        if result_schema:
            payload["resultSchema"] = result_schema
        if use_proxies:
            payload["browserSettings"] = {"proxies": True}

        response = self._session.post(
            f"{API_BASE}/agents/runs",
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def get_run(self, run_id: str) -> dict[str, Any]:
        response = self._session.get(
            f"{API_BASE}/agents/runs/{run_id}",
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def list_messages(
        self,
        run_id: str,
        *,
        since: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit}
        if since:
            params["since"] = since
        response = self._session.get(
            f"{API_BASE}/agents/runs/{run_id}/messages",
            params=params,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def poll_run(
        self,
        run_id: str,
        *,
        poll_interval: float = 3.0,
        stream_messages: bool = True,
    ) -> dict[str, Any]:
        since: str | None = None
        last_status: str | None = None

        while True:
            run = self.get_run(run_id)
            status = run.get("status", "UNKNOWN")

            if status != last_status:
                session_id = run.get("sessionId")
                session_link = (
                    f"https://www.browserbase.com/sessions/{session_id}"
                    if session_id
                    else None
                )
                print(f"[status] {status}")
                if session_link:
                    print(f"[live view] {session_link}")
                last_status = status

            if stream_messages:
                since = self._print_new_messages(run_id, since)

            if status in TERMINAL_STATUSES:
                return run

            time.sleep(poll_interval)

    def _print_new_messages(self, run_id: str, since: str | None) -> str | None:
        page = self.list_messages(run_id, since=since, limit=50)
        messages = page.get("data", [])
        for entry in messages:
            self._print_message(entry.get("message", {}))
        return page.get("nextSince", since)

    @staticmethod
    def _print_message(message: dict[str, Any]) -> None:
        role = message.get("role", "unknown")
        parts = message.get("parts", [])
        for part in parts:
            part_type = part.get("type")
            if part_type == "text" and part.get("text"):
                text = part["text"].strip()
                if text:
                    print(f"[{role}] {text[:500]}")
            elif part_type == "tool-invocation":
                tool_name = part.get("toolName") or part.get("toolInvocationId", "tool")
                print(f"[{role}] tool: {tool_name}")
