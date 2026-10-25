# LaunchCodeAgenticEngineer — Module 1

Docker development environment for LaunchCode's **Agentic Programming** course. Provides a consistent, pre-configured Python environment with AI/ML libraries, Anthropic Claude integration, and the Claude Code CLI.

Module 1 also contains two small Python modules used for the parallel agent-session exercise.

## Project Structure

The repository is split into one folder per course module (`module_1/`, `module_2/`, `module_3/`), each with its own Docker image. This README covers `module_1/`:

```
module_1/
├── Dockerfile              # Image definition: Python 3.12, Node.js, Claude Code, OpenCode, ngrok
├── docker-entrypoint.sh    # Restores/persists the Claude login via the claude-auth volume
├── requirements.txt        # Python packages installed in the image
├── settings.json           # Claude Code settings baked into the image (status line)
├── statusline.sh           # Claude Code status line: model, dir, context %, tokens, cost
├── CLAUDE.md               # Guidance for Claude Code when working in this module
├── agent_docker_check.md   # Prompt for an agent to review and test the Docker build
├── module_x.py             # Business-rule utilities ("Session A": write unit tests)
├── module_y.py             # Formatting/reporting utilities ("Session B": improve docs)
└── README.md
```

## Example Python Modules

These modules have no third-party dependencies and are the targets for the parallel agent-session exercise.

**`module_x.py`** — business rules:

| Function | Purpose |
| --- | --- |
| `normalize_name(name)` | Collapse whitespace and title-case a name |
| `calculate_discount(price, customer_tier)` | Apply the discount for `standard`, `silver`, `gold`, or `platinum` |
| `classify_priority(score)` | Map a 0–100 score to `low`, `medium`, `high`, or `urgent` |
| `summarize_order(items)` | Total the item count and subtotal for an order |
| `is_valid_project_code(code)` | Check that a code matches the `AA-1234` format |

**`module_y.py`** — formatting and reporting:

| Function | Purpose |
| --- | --- |
| `format_currency(amount)` | Format a number as `$1,234.50` / `-$42.00` |
| `build_report_title(project_name, version)` | Build `"<project> — <version>"` with sensible defaults |
| `mask_email(email)` | Mask the local part of an email address (`J******e@example.com`) |
| `generate_summary_line(name, status, score)` | Build `"Name: status (score)"` |
| `create_markdown_table(rows, columns)` | Render a list of dicts as a Markdown table |
| `truncate_text(text, max_length=80)` | Collapse whitespace and truncate with `...` |

Each function in `module_y.py` has a docstring with usage examples, which you can run as tests:

```bash
python -m doctest -v module_y.py
```

## Quick Start from GitHub

Clone the repo and build locally:

```bash
git clone https://github.com/LaunchCodeEducation/LaunchCodeAgenticEngineer.git
cd LaunchCodeAgenticEngineer/module_1
docker build -t agentic_engineer_1 .
docker run -it --rm -v claude-auth:/claude-auth -p 8501:8501 -v "$PWD":/workspace agentic_engineer_1
```

Or skip the build entirely and pull the pre-built image from Google Artifact Registry:

```bash
docker run -it --rm -v claude-auth:/claude-auth -p 8501:8501 -v "$PWD":/workspace us-central1-docker.pkg.dev/hire-human/hire-human-ai/agentic_engineer_1:latest
```

> **Claude authentication:** The `-v claude-auth:/claude-auth` mount is a shared named volume that persists your Claude Code login across container runs — and across every course module. You go through Claude's first-run onboarding and log in once; every later container restores your credential and skips onboarding. Only your credential is stored on the volume — skills, agents, settings, the status line, and each image's MCP servers stay baked into the image.

## Build

Run these from the `module_1/` directory, which contains the `Dockerfile`:

```bash
docker build -t agentic_engineer_1 .
```

To force a complete rebuild from scratch (ignoring all cached layers):

```bash
docker build --no-cache -t agentic_engineer_1 .
```

## Run

### With a local workspace (recommended)

Mount your local project folder into the container so your files live on your machine, not inside Docker:

```bash
docker run -it --rm -v claude-auth:/claude-auth -p 8501:8501 -p 8502:8502 -v /path/to/your/workspace:/workspace agentic_engineer_1
```

Replace `/path/to/your/workspace` with the actual path on your machine. To use the current directory, you can use `./` (works on macOS, Linux, and modern Windows):

```bash
docker run -it --rm -v claude-auth:/claude-auth -p 8501:8501 -p 8502:8502 -v ./:/workspace agentic_engineer_1
```

Or with `$PWD` on macOS/Linux:

```bash
docker run -it --rm -v claude-auth:/claude-auth -p 8501:8501 -v "$PWD":/workspace agentic_engineer_1
```

On Windows (Command Prompt):

```cmd
docker run -it --rm -v claude-auth:/claude-auth -p 8501:8501 -v "%cd%":/workspace agentic_engineer_1
```

On Windows (PowerShell):

```powershell
docker run -it --rm -v claude-auth:/claude-auth -p 8501:8501 -v "${PWD}:/workspace" agentic_engineer_1
```

Files you create or edit inside `/workspace` in the container will be saved to your local folder and persist after the container exits.

### Without a local workspace

```bash
docker run -it --rm -v claude-auth:/claude-auth -p 8501:8501 agentic_engineer_1
```

Note: any files created inside the container will be lost when it exits.

## Gmail API Credentials

To use the Gmail API, you need a `credentials.json` file downloaded from the [Google Cloud Console](https://console.cloud.google.com/).

Place `credentials.json` in your workspace directory (the folder you mount as `/workspace`). Inside the container it will be accessible at `/workspace/credentials.json`.

Your code should reference it as:

```python
from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
```

> **Keep `credentials.json` private.** Add it to `.gitignore` so it is never committed to source control:
>
> ```
> credentials.json
> token.json
> ```

On first run, Google will prompt you to authorize access. The resulting `token.json` will be saved in your workspace and reused on subsequent runs.

## Images

Images are built and published automatically by a GitHub Action whenever the main repository (not forks) changes — you don't need to build or push manually.

Students can pull and run the published image directly without building it locally:

```bash
docker run -it --rm -v claude-auth:/claude-auth -p 8501:8501 -v "$PWD":/workspace us-central1-docker.pkg.dev/hire-human/hire-human-ai/agentic_engineer_1:latest
```
