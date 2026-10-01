# LaunchCodeAgenticEngineer

LaunchCode Agentic Engineer Course.

Each module is a self-contained Docker development environment that builds on the
one before it. Modules share a `claude-auth` named volume, so you log in to Claude
Code once and every later container reuses that credential.

## Project Structure

```
.
├── module_1/    Base Python 3.12 + Claude Code environment
├── module_2/    Adds MCP servers, skills, and sub-agents
└── module_3/    Adds custom MCP servers, memory, and an eval harness
```

Each module directory holds its own `README.md` with full setup and run
instructions, plus a `CLAUDE.md` with guidance for Claude Code, a `Dockerfile`,
`requirements.txt`, and a `settings.json` baked into the image at build time.

### `module_1/` — base environment

Python 3.12 with the Anthropic SDK, Streamlit, and the Claude Code CLI
pre-installed. Also contains the sample modules used in the parallel
agent-session exercise:

- `module_x.py` — business-rule helpers (the "write unit tests" task)
- `module_y.py` — formatting and reporting helpers (the "improve docs" task)

### `module_2/` — MCP servers, skills, and agents

Extends module 1 with the Slack and Gmail MCP servers, plus:

- `skills/` — slash commands (`/send-slack-message`, `/check-gmail`,
  `/send-email`, `/summarize-session`)
- `agents/` — sub-agent definitions (`code-reviewer`, `email-summarize`)
- `sample_docs/` and `sample_review.py` — material for the review exercises

### `module_3/` — orchestration, memory, and evals

Extends module 2 with a larger agent roster and the tooling to measure it:

- `mcp/` — custom MCP servers written for the course: `coursetools_server.py`
  for the tool-scoping exercise (role-checked against `roles.allowlist.json`),
  plus `retrieval/` and `storage/` servers
- `eval/` — orchestrator and regression, holdout, and rubric suites
- `.memory/` — reference notes the retrieval server indexes
- `.eval-artifacts/` — recorded baselines and run output
- `docs/` — PRD, routing and tool-grant map, and calibration/iteration logs
- `scripts/` — helpers to start the MCP servers and compare retrieval runs

## Getting Started

Pick the module you are working through and follow its README. To start from the
beginning:

```bash
cd module_1
docker build -t agentic_engineer_1 .
docker run -it --rm -v claude-auth:/claude-auth -p 8501:8501 -v "$PWD":/workspace agentic_engineer_1
```

Pre-built images are published automatically for each module and can be pulled
instead of built — see the module README for the image path.

## Credentials

`credentials.json` and `token.json` (Google Cloud Console, for the Gmail API)
belong in the directory you mount as `/workspace`, and must never be committed.
`.gitignore` currently covers `credentials.json`; add `token.json` to it before
you run the OAuth flow, since that file is written into your workspace.
