# TODO — Garmin Health

## Active
- [ ] Migrate Garmin JSON exports from `../aws-ai-agent/docs/` → `data/raw/`
- [ ] Verify Streamlit app path references after move to `analytics/`
- [ ] Complete OAuth flow for Garmin Connect API (see `backend/tests/test_oauth_flow.py`)

## Backlog
- [ ] Add CI/CD for backend Lambda deployments
- [ ] Add automated data freshness check (last sync timestamp)
- [ ] Extend dashboard with training load heatmap
- [ ] Add sleep score trend overlay on training load chart

## Done
- [x] Consolidate garmin-integration + garmin-analytics + garmin-rag-dataset into garmin-health/ (2026-02-27)
- [x] Deploy base AWS infrastructure (Lambda + DynamoDB + API Gateway)
- [x] Build Streamlit dashboard MVP with 3 pillars (Running, Swimming, Sleep)
