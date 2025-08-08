# Nightwalker AI – OODA-Loop OSINT Fusion Engine (NOFE)

**Mission:** Automate the generation of daily CHAOS-style intelligence briefs using Nightwalker AI’s 4-Agent Stack (Thinker, Doer, Controller, Pulse) and Truth Vector Model.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m nltk.downloader vader_lexicon
python src/nofe/pipeline.py
```

Reports will be generated in `reports/` as `CHAOS_YYYYMMDD.md`.

## GitHub Actions Automation
A workflow is provided in `.github/workflows/nofe_daily.yml` to automatically run the pipeline daily, commit the results to the repo, and push to the `main` branch.

Adjust the cron schedule to fit your needs.

## Folder Structure
```
src/nofe/
  ingestion.py
  analysis.py
  pipeline.py
  config.yaml
prompts/
  chaos_template.md
reports/
.github/workflows/
  nofe_daily.yml
README.md
requirements.txt
LICENSE
```

## License
MIT
