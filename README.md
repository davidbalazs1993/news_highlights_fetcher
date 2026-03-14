# News Highlights Fetcher

Fetches highlights from curated RSS feeds for the last _X_ days, then summarizes the results and extracts the highlights by domain.


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

## AWS Free Tier Deployment (weekly email)

Use AWS services that are in the free tier for a small weekly job:

- **EventBridge** scheduler (every Monday 9am).
- **Lambda** runs this package and generates the report.
- **SES** sends the email.

### Required environment variables (Lambda)

Set these in your Lambda configuration:

```
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
EMAIL_TO=you@example.com
EMAIL_FROM=you@example.com
AWS_REGION=eu-west-1
```

### Lambda handler (wrapper)

Use the built-in handler at `news_highlights_fetcher.lambda_handler.handler`.

Example Lambda environment variables:

```
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
EMAIL_TO=you@example.com
EMAIL_FROM=you@example.com
AWS_REGION=eu-west-1
DAYS=7
```

If you prefer AWS SSM Parameter Store for secrets, set:

```
OPENAI_API_KEY_SSM_PARAM=/path/to/openai_api_key
SSM_REGION=eu-west-1
```

`OPENAI_API_KEY` still works locally via `.env`. In Lambda, if
`OPENAI_API_KEY` is not set and `OPENAI_API_KEY_SSM_PARAM` is provided,
the handler will fetch the secret from SSM with decryption.

### Lambda packaging (zip)

```
uv venv
source .venv/bin/activate

rm -rf dist/lambda
mkdir -p dist/lambda
uv pip install --target dist/lambda .
cp -r config dist/lambda/
cd dist/lambda
zip -r ../news-highlights-lambda.zip .
```

### EventBridge schedules

- Weekly Monday 08:00: `cron(0 9 ? * MON *)`
- Monthly 1st 08:00: `cron(0 8 1 * ? *)`

## Notes

- `--days` supports longer windows; pass `30` for “last month.”
- The summarizer is prompt-based and can be swapped to any OpenAI-compatible API.
