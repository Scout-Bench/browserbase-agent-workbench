# browserbase-agent-workbench

Test harness for [Browserbase Agents](https://docs.browserbase.com/platform/agents/overview): download a resume PDF, fill a job application, and submit it.

## Quick start

```bash
cp .env.example .env
# Set BROWSERBASE_API_KEY and RESUME_URL (Supabase signed URL or public PDF link)

pip install -r requirements.txt
python run_test.py
```

`run_test.py` creates or updates the agent, starts a run, polls status, and prints the live session link plus structured result.

## Commands

| Command | What it does |
|---------|----------------|
| `python run_test.py` | Sync agent config + run (default) |
| `python run_test.py setup` | Create/update agent only |
| `python run_test.py run` | Run only (needs `.agent_id`) |
| `python run_test.py --force-setup` | Create a fresh agent |

## Env vars

| Variable | Required | Description |
|----------|----------|-------------|
| `BROWSERBASE_API_KEY` | Yes | From [Browserbase settings](https://www.browserbase.com/settings) |
| `RESUME_URL` | Yes | Direct PDF URL (e.g. Supabase signed URL) |
| `APPLICATION_URL` | No | Defaults to Revise Robotics Ashby form |
| `USE_PROXIES` | No | `true` by default |

## How it works

1. Agent downloads resume from `%resumeUrl%`
2. Parses PDF, opens `%applicationUrl%`
3. Fills fields, uploads resume, submits application
4. Returns JSON: `submitted`, `confirmationMessage`, `notes`, etc.

Watch the run in the Browserbase dashboard via the printed **Live View** URL.

## Docs

- [Agents overview](https://docs.browserbase.com/platform/agents/overview)
- [Integrating agents](https://docs.browserbase.com/platform/agents/integrate-api-sdk)
