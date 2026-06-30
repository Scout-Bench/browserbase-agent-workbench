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


## How it works

1. Agent downloads resume from `%resumeUrl%`
2. Parses PDF, opens `%applicationUrl%`
3. Fills fields, uploads resume, submits application
4. Returns JSON: `submitted`, `confirmationMessage`, `notes`, etc.

Watch the run in the Browserbase dashboard via the printed **Live View** URL.

## Docs

- [Agents overview](https://docs.browserbase.com/platform/agents/overview)
- [Integrating agents](https://docs.browserbase.com/platform/agents/integrate-api-sdk)
