# AWS Bedrock vs Azure AI Foundry: Agent Comparison

Research comparing agent capabilities between AWS and Azure.

## Overview

| Aspect | AWS Bedrock | Azure AI Foundry |
|--------|-------------|------------------|
| Agent Framework | Bedrock Agents | AI Agent Service |
| Models | Claude, Llama, Titan | GPT-4, Claude, Llama |
| Knowledge Base | Bedrock KB | AI Search |
| Orchestration | Built-in | Semantic Kernel |

## Feature Comparison

### Agent Capabilities

| Feature | AWS Bedrock | Azure AI Foundry |
|---------|-------------|------------------|
| Tool Calling | Yes | Yes |
| Multi-turn | Yes | Yes |
| Memory | Session-based | Flexible |
| Guardrails | Bedrock Guardrails | Content Safety |

### Knowledge Base / RAG

| Feature | AWS Bedrock | Azure AI Foundry |
|---------|-------------|------------------|
| Vector Store | OpenSearch | AI Search |
| Embeddings | Titan, Cohere | Ada, E5 |
| Hybrid Search | Yes | Yes |
| Document Types | PDF, TXT, HTML, etc. | Similar |

### Developer Experience

| Aspect | AWS Bedrock | Azure AI Foundry |
|--------|-------------|------------------|
| SDK | Boto3, bedrock-runtime | azure-ai-* SDKs |
| Console | Good | Excellent |
| Documentation | Good | Good |
| Examples | Moderate | Many |

## Cost Comparison

*Pricing varies by region and usage patterns*

### AWS Bedrock
- Per 1K input/output tokens
- Knowledge base: OpenSearch costs
- No upfront commitment required

### Azure AI Foundry
- Per 1K tokens
- AI Search: Per unit pricing
- Provisioned throughput option

## Recommendations

| Use Case | Recommendation | Rationale |
|----------|---------------|-----------|
| Personal Learning | AWS Bedrock | Simpler setup, good free tier |
| Enterprise | Azure AI Foundry | Better compliance, enterprise support |
| Multi-cloud | Either | Both have good SDKs |

## Conclusion

Both platforms offer robust agent capabilities. Choice should be based on:
- Existing cloud investment
- Team expertise
- Compliance requirements
- Specific model needs

---

*Last updated: 2025-01-09*
