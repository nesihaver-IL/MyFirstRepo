# Architectural Decisions — Garmin Health

## ADR-001: AWS Lambda over always-on server
**Decision**: Use Lambda for data ingestion rather than an EC2 or container.
**Reason**: Garmin webhooks are infrequent; Lambda is cost-optimal for event-driven ingestion.
**Status**: Active

## ADR-002: Streamlit for dashboard (not React/Vue)
**Decision**: Python Streamlit rather than a JavaScript frontend.
**Reason**: Data science workflow; faster iteration; same language as data processing.
**Status**: Active

## ADR-003: DynamoDB for activity storage
**Decision**: DynamoDB over RDS/PostgreSQL.
**Reason**: No fixed schema for different Garmin activity types; serverless fits Lambda model.
**Status**: Active

## ADR-004: Claude AI for insights (not fine-tuned model)
**Decision**: Anthropic Claude API with RAG (research summaries as context).
**Reason**: Athlete-specific research docs provide grounded, personalized recommendations.
**Status**: Active

## ADR-005: Consolidate Garmin code into garmin-health/ (2026-02-27)
**Decision**: Move garmin-integration and garmin-analytics out of aws-ai-agent and into a unified garmin-health/ project.
**Reason**: Code was fragmented across 3 directories; hard for agents to reason about as a whole.
**Status**: Active
