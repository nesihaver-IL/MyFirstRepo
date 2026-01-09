# AI Agent Skills

This directory contains specialized skills for AI coding agents. These skills enhance Claude Code and other AI agents with domain-specific expertise.

## Available Skills

### Cloud Platforms

#### Azure AI Foundry
Build AI agents and automation with Azure AI Foundry platform (formerly Azure AI Studio). Comprehensive platform for production AI applications with multi-agent orchestration, Prompt Flow, and RAG capabilities.

**Use when:**
- Developing AI agents on Azure infrastructure
- Implementing Prompt Flow orchestrations
- Building RAG applications with Azure AI Search
- Creating multi-agent systems on Azure
- Deploying production AI applications with MLOps

**Triggers:** Azure AI Foundry, Azure AI Studio, Prompt Flow, Azure OpenAI agents, Azure agents

**Key Capabilities:**
- AI Agent Service with tools and memory
- Prompt Flow visual orchestration
- 1,800+ models in Model Catalog
- Vector search and RAG with Azure AI Search
- Built-in evaluation and monitoring
- Content Safety guardrails
- MLOps and CI/CD integration

**Resources:**
- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [Azure AI Agent Service](https://learn.microsoft.com/azure/ai-services/agents/)
- [Prompt Flow](https://microsoft.github.io/promptflow/)
- [Azure AI Samples](https://github.com/Azure-Samples/azure-ai-samples)

---

### AWS Cloud

#### aws-agentcore
Build AI agents with AWS Bedrock AgentCore. Includes tool-use patterns, agent orchestration, Lambda integration, and production-ready use cases.

**Use when:**
- Developing agents on AWS infrastructure
- Implementing tool-use patterns
- Creating agent orchestration systems
- Integrating with Bedrock models

**Triggers:** AgentCore, Bedrock Agent, AWS agent, Lambda tools

**Resources:**
- [AWS AgentCore Samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples)
- [Official Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)

---

#### aws-strands
Build model-agnostic AI agents with the Strands framework. Supports ReAct patterns, multi-agent systems, and works with any LLM.

**Use when:**
- Developing model-agnostic agents
- Implementing ReAct (Reasoning + Acting) patterns
- Creating multi-agent systems
- Building production agents on AWS

**Triggers:** Strands, Strands SDK, model-agnostic agent, ReAct agent

**Features:**
- Works with Anthropic, OpenAI, Amazon Bedrock, and custom endpoints
- Built-in ReAct pattern support
- Multi-agent orchestration
- Memory management
- Streaming responses

---

### Design & Frontend

#### figma
Figma API integration for design automation, component code generation, and design token extraction.

**Use when:**
- Working with Figma files
- Extracting design tokens
- Generating React components from designs
- Syncing design systems with code

**Triggers:** Figma API, design tokens, component generation

**Capabilities:**
- Extract colors, typography, and spacing
- Generate React components from Figma nodes
- Export CSS variables and Tailwind configs
- Access Design Tokens 2.0 (Variables API)
- Component code generation

---

#### analytics-metrics
Build data visualization and analytics dashboards with Recharts.

**Use when:**
- Creating charts and visualizations
- Building KPI displays
- Developing metrics dashboards
- Displaying data insights

**Triggers:** analytics, dashboard, charts, metrics, KPI, data visualization, Recharts

**Includes:**
- Line, Bar, and Pie charts
- KPI card components
- Dashboard layouts
- Number formatting utilities
- Responsive designs

---

### Development Tools

#### copilot-docs
Configure GitHub Copilot with custom instructions via `.github/copilot-instructions.md`.

**Use when:**
- Setting up repository-specific Copilot instructions
- Customizing Copilot behavior
- Creating AI guidance for your codebase

**Triggers:** Copilot instructions, copilot-instructions.md, GitHub Copilot config

**Best practices:**
- Define tech stack and architecture
- Specify code standards and conventions
- Include testing guidelines
- Add API patterns and error handling

---

#### github-trending
Fetch and display GitHub trending repositories and developers.

**Use when:**
- Building dashboards
- Discovering popular projects
- Tracking trending repos
- Creating discovery tools

**Triggers:** GitHub trending, popular repos, trending developers

**Methods:**
- Web scraping (recommended)
- GitHub Search API (alternative)
- Server-side implementation with caching
- React components included

**⚠️ Important:** GitHub does not provide an official trending API. This skill uses web scraping or Search API workarounds.

---

### AI & Image Generation

#### nano-banana-pro
Generate high-quality images using Google's Gemini 3 Pro Image API.

**Use when:**
- Creating professional visual content
- Generating images with text rendering
- Maintaining character consistency
- Building image generation features

**Triggers:** image generation, Gemini Pro, visual content, AI images

**Features:**
- Professional text rendering
- Character consistency (up to 5 subjects)
- Multiple aspect ratios (1:1, 3:2, 16:9, 9:16, 21:9)
- Resolution from 1K to 4K
- Google Search grounding
- Iterative editing support

---

## How to Use Skills

### With Claude Code

Skills in `.claude/skills/` are automatically available to Claude Code. Just reference the skill by name or use trigger keywords in your prompts.

```bash
# Example: Using the aws-agentcore skill
"Help me create a Bedrock agent with Lambda tool integration"
```

### Manual Activation

You can explicitly activate a skill by mentioning its name:

```bash
"Use the figma skill to extract design tokens from this file"
```

### File Structure

Each skill follows this structure:

```
.claude/skills/
├── skill-name/
│   └── SKILL.md          # Main skill file with YAML frontmatter
```

## Skill Format

Each `SKILL.md` file contains:

1. **YAML Frontmatter**: Name, description, and trigger keywords
2. **Documentation**: How to use the skill
3. **Code Examples**: Practical implementations
4. **Resources**: Links to official docs and references

Example:

```markdown
---
name: skill-name
description: Brief description of what the skill does
---

# Skill Name

Full documentation, examples, and usage patterns...
```

## Adding New Skills

To add a new skill:

1. Create a directory in `.claude/skills/`
2. Add a `SKILL.md` file with proper frontmatter
3. Include documentation and examples
4. Update this README

## Skills Source

These skills were imported from [hoodini/ai-agents-skills](https://github.com/hoodini/ai-agents-skills), a curated collection of specialized skills for AI coding agents.

## Resources

- **Original Skills Repository**: https://github.com/hoodini/ai-agents-skills
- **Anthropic Skills**: https://github.com/anthropics/skills
- **Skills Specification**: https://github.com/agentskills/agentskills

## License

Each skill retains its original license from the source repository.
