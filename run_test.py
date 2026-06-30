#!/usr/bin/env python3
"""Create a Browserbase agent and run a resume-driven application form test."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from browserbase_client import BrowserbaseAgentsClient
from config import (
    AGENT_NAME,
    DEFAULT_APPLICATION_URL,
    DEFAULT_TASK,
    RESULT_SCHEMA,
    SYSTEM_PROMPT,
)

AGENT_ID_FILE = Path(__file__).resolve().parent / ".agent_id"


def load_agent_id() -> str | None:
    env_id = os.environ.get("BROWSERBASE_AGENT_ID")
    if env_id:
        return env_id
    if AGENT_ID_FILE.exists():
        return AGENT_ID_FILE.read_text(encoding="utf-8").strip() or None
    return None


def save_agent_id(agent_id: str) -> None:
    AGENT_ID_FILE.write_text(agent_id, encoding="utf-8")


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        print(f"Missing required environment variable: {name}", file=sys.stderr)
        sys.exit(1)
    return value


def setup_agent(client: BrowserbaseAgentsClient, force: bool = False) -> str:
    existing = load_agent_id()
    if existing and not force:
        print(f"Updating existing agent: {existing}")
        client.update_agent(
            existing,
            name=AGENT_NAME,
            system_prompt=SYSTEM_PROMPT,
            result_schema=RESULT_SCHEMA,
        )
        print("Agent config synced.")
        return existing

    print("Creating Browserbase agent...")
    agent = client.create_agent(
        name=AGENT_NAME,
        system_prompt=SYSTEM_PROMPT,
        result_schema=RESULT_SCHEMA,
    )
    agent_id = agent["agentId"]
    save_agent_id(agent_id)
    print(f"Created agent: {agent_id}")
    return agent_id


def build_variables(resume_url: str, application_url: str) -> dict[str, dict[str, str]]:
    return {
        "resumeUrl": {
            "value": resume_url,
            "description": "Signed or public URL to the candidate resume PDF",
        },
        "applicationUrl": {
            "value": application_url,
            "description": "Ashby job application page to fill out",
        },
    }


def run_test(
    client: BrowserbaseAgentsClient,
    *,
    agent_id: str | None,
    resume_url: str,
    application_url: str,
    task: str,
    use_proxies: bool,
    poll_interval: float,
) -> int:
    print("Starting agent run...")
    run = client.run_agent(
        task=task,
        agent_id=agent_id,
        variables=build_variables(resume_url, application_url),
        result_schema=RESULT_SCHEMA,
        use_proxies=use_proxies,
    )

    run_id = run["runId"]
    agent_id = run.get("agentId") or agent_id
    print(f"Run started: {run_id}")
    if agent_id:
        print(f"Agent: {agent_id}")
    print(f"Dashboard: https://www.browserbase.com/agents")

    final_run = client.poll_run(
        run_id,
        poll_interval=poll_interval,
        stream_messages=True,
    )

    print("\n--- Run finished ---")
    print(f"Status: {final_run.get('status')}")
    if final_run.get("sessionId"):
        print(
            "Session replay: "
            f"https://www.browserbase.com/sessions/{final_run['sessionId']}"
        )

    result = final_run.get("result")
    if result is not None:
        print("\nResult:")
        print(json.dumps(result, indent=2))
    elif final_run.get("cause"):
        print("\nFailure:")
        print(json.dumps(final_run["cause"], indent=2))

    return 0 if final_run.get("status") == "COMPLETED" else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Test Browserbase Agents with a resume PDF and Ashby application form.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=("setup", "run", "all"),
        default="all",
        help="setup: create agent; run: start a run; all: setup then run (default)",
    )
    parser.add_argument(
        "--resume-url",
        help="Override RESUME_URL from the environment",
    )
    parser.add_argument(
        "--application-url",
        help="Override APPLICATION_URL from the environment",
    )
    parser.add_argument(
        "--task",
        default=DEFAULT_TASK,
        help="Natural-language task sent to the agent",
    )
    parser.add_argument(
        "--no-proxies",
        action="store_true",
        help="Disable Browserbase proxies for the session",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=3.0,
        help="Seconds between status polls (default: 3)",
    )
    parser.add_argument(
        "--force-setup",
        action="store_true",
        help="Create a new agent even if .agent_id exists",
    )
    return parser.parse_args()


def main() -> int:
    load_dotenv()
    args = parse_args()

    api_key = require_env("BROWSERBASE_API_KEY")
    client = BrowserbaseAgentsClient(api_key)

    agent_id = load_agent_id()
    if args.command in ("setup", "all"):
        agent_id = setup_agent(client, force=args.force_setup)

    if args.command in ("run", "all"):
        resume_url = args.resume_url or os.environ.get("RESUME_URL", "").strip()
        if not resume_url:
            print(
                "Missing resume URL. Set RESUME_URL in .env or pass --resume-url.",
                file=sys.stderr,
            )
            return 1

        application_url = (
            args.application_url
            or os.environ.get("APPLICATION_URL", "").strip()
            or DEFAULT_APPLICATION_URL
        )
        use_proxies = os.environ.get("USE_PROXIES", "true").lower() != "false"
        if args.no_proxies:
            use_proxies = False

        return run_test(
            client,
            agent_id=agent_id,
            resume_url=resume_url,
            application_url=application_url,
            task=args.task,
            use_proxies=use_proxies,
            poll_interval=args.poll_interval,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
