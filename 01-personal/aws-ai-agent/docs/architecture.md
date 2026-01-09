# Architecture - AWS AI Agent

## Overview

This document describes the architecture of the AWS AI Agent project.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Agent Controller                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Reasoning  │  │   Action    │  │    Observation      │ │
│  │   Engine    │──│   Handler   │──│     Processor       │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼──────┐  ┌───────▼──────┐  ┌───────▼──────┐
│    Tools     │  │   Memory     │  │  Knowledge   │
│              │  │              │  │    Base      │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Components

### Agent Controller

The main orchestration layer that manages the agent loop:
- **Reasoning Engine**: Uses Bedrock Claude for decision making
- **Action Handler**: Executes tool calls
- **Observation Processor**: Processes results and updates context

### Tools

Custom capabilities the agent can invoke:
- API integrations
- Database queries
- File operations
- External service calls

### Memory

Conversation history and context management:
- Short-term: Current conversation
- Long-term: Persistent user context (future)

### Knowledge Base

RAG implementation using:
- Amazon OpenSearch for vector storage
- S3 for document storage
- Bedrock embeddings for document processing

## Data Flow

1. User sends query
2. Agent controller receives input
3. Reasoning engine decides next action
4. Action handler executes (tool call or response)
5. Observation processor updates context
6. Loop until task complete

## AWS Services

| Service | Purpose |
|---------|---------|
| Bedrock | Foundation models |
| Lambda | Agent runtime |
| OpenSearch | Vector store |
| S3 | Document storage |
| IAM | Access control |
