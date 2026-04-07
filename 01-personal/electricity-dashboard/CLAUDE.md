# electricity-dashboard — Email & Electricity Cost Analyzer

## Project Overview
Personal utility for tracking electricity costs and analyzing email patterns. Fetches data from Gmail and generates HTML visualizations.

## Tech Stack
- **Backend**: Python 3.12.3
- **Frontend**: HTML + inline CSS/JS
- **Dependencies**: See `requirements.txt`

## Quick Start
```bash
cd 01-personal/electricity-dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python fetch_gmail.py
```

## Key Files
- `fetch_gmail.py` — Gmail API integration and data fetch
- `index.html` — Dashboard visualization
- `requirements.txt` — Python dependencies
- `SECURITY.md` — Gmail OAuth setup and authentication

## Configuration
Before running, set up Gmail API credentials:
1. Follow steps in `SECURITY.md`
2. Place credentials in `~/.gmail_credentials.json`

## Notes for Migration
- This folder moved from repo root → `01-personal/` for organization
- `.env.example` exists but `.env` is not tracked (security)
- Venv (`venv/`) is not committed — rebuild on new machine

## Related
- See global `CLAUDE.md` for workspace standards and Python venv conventions
