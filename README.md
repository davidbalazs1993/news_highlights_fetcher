# News Highlights Fetcher

Fetches highlights from curated RSS feeds for the last _X_ days (or longer), then summarizes by domain.

## Why no LangChain/LangGraph?

This is a deterministic pipeline: fetch feeds → filter by date → extract text → summarize. A lightweight custom flow is easier to debug, cheaper to run, and simpler to deploy. You can add LangGraph later if you need complex orchestration or tool-calling.

## Quickstart (UV)

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

Run:

```bash
news-highlights --days 7
news-highlights --days 30 --domains cncf,gcp
news-highlights --config ./config/custom.yaml --days 14
```

## Configuration

Default config: `config/defaults.yaml`

```yaml
domains:
  cncf:
    feeds:
      - https://www.cncf.io/feed/
  aws_ai_services:
    feeds:
      - https://aws.amazon.com/blogs/machine-learning/feed/
```

You can override by providing `--config` with your own YAML.

## Environment

Set your OpenAI-compatible key in `.env` (loaded automatically if present).
A template is available at `env.example`:

```bash
OPENAI_API_KEY="..."
OPENAI_MODEL="gpt-4o-mini"
```

Run with UV:

```bash
uv run news-highlights
```

## AWS (later deployment idea)

- **EventBridge** scheduled rule (every Monday 8am).
- **Lambda** runs this package, writes summary.
- **SES** to email the summary to you.
- Optional **S3** for storing historical runs.

## Notes

- `--days` supports longer windows; pass `30` for “last month.”
- The summarizer is prompt-based and can be swapped to any OpenAI-compatible API.
