# Decision Log - AWS AI Agent

This document records architectural and technical decisions made during the project.

---

## [DECISION-001] Use AWS Bedrock Over Self-Hosted Models

**Date**: 2025-01-09
**Status**: Accepted

### Context

Need to choose between self-hosted open-source models vs managed AI services for the agent.

### Decision

Use AWS Bedrock as the primary AI platform.

### Consequences

**Positive:**
- No infrastructure management for model hosting
- Access to multiple foundation models (Claude, Llama, etc.)
- Built-in agent framework and knowledge bases
- Pay-per-use pricing for learning

**Negative:**
- Vendor lock-in to AWS
- Less control over model behavior
- Costs can accumulate with heavy usage

### Alternatives Considered

1. **Self-hosted LLaMA**: Rejected due to infrastructure complexity for learning project
2. **OpenAI API**: Rejected to focus on AWS ecosystem

---

## [DECISION-002] [Next Decision]

**Date**:
**Status**: Proposed

### Context

[Add next decision here]
