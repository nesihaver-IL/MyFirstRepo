# AWS Bedrock Agent Development

This repository contains comprehensive guides and tools for building AWS Bedrock Agents, with a strong focus on cost management and Free Tier optimization.

## 📚 Documentation

### [AWS_BEDROCK_AGENT_PLAN.md](./AWS_BEDROCK_AGENT_PLAN.md)
Complete step-by-step guide for building your first AWS Bedrock Agent, covering:
- AWS account setup and IAM configuration
- Model access and selection
- Agent design and implementation
- Knowledge bases and action groups
- Testing, deployment, and monitoring

### [AWS_COST_MANAGEMENT_GUIDE.md](./AWS_COST_MANAGEMENT_GUIDE.md) ⚡ **START HERE if you have budget concerns!**
Comprehensive guide for managing AWS costs when building Bedrock Agents:
- How to investigate what consumed your budget
- Identifying expensive resources (OpenSearch Serverless costs ~$350/month!)
- Step-by-step resource cleanup instructions
- Free Tier optimization strategies
- Cost-effective testing practices
- Emergency cost control procedures

## 🚀 Quick Start: Investigate Your AWS Costs

If your AWS Free Tier credits are gone and you want to know why:

### 1. Run the Cost Investigation Script

```bash
# Make sure you have AWS CLI configured
aws configure

# Run the investigation script
./check_aws_costs.sh
```

This script will automatically check:
- Your daily costs for the last 7 days
- Costs broken down by AWS service
- OpenSearch Serverless collections (⚠️ **biggest cost driver!**)
- Bedrock agents and knowledge bases
- Lambda functions
- S3 buckets and storage
- CloudWatch logs

### 2. Take Immediate Action

Based on the script output, the most common cost culprits are:

**🔴 CRITICAL - Delete OpenSearch Serverless Collections**
```bash
# These cost ~$350/month EACH, even if unused!
aws opensearchserverless list-collections --region us-east-1
aws opensearchserverless delete-collection --id COLLECTION_ID --region us-east-1
```

**🟡 Delete Unused Bedrock Agents**
```bash
aws bedrock-agent list-agents --region us-east-1
aws bedrock-agent delete-agent --agent-id AGENT_ID --region us-east-1
```

**🟡 Delete Knowledge Bases**
```bash
aws bedrock-agent list-knowledge-bases --region us-east-1
aws bedrock-agent delete-knowledge-base --knowledge-base-id KB_ID --region us-east-1
```

### 3. Set Up Cost Alerts

Prevent this from happening again:

```bash
# Create a $5 daily budget alert via AWS Console:
# 1. Go to AWS Billing Dashboard → Budgets
# 2. Create budget → Cost budget
# 3. Set amount: $5/day
# 4. Alert threshold: 80% ($4)
# 5. Add your email
```

## 💡 Key Insights for Free Tier Users

### ❌ What to AVOID
1. **OpenSearch Serverless (Knowledge Bases backend)** - Costs ~$350/month minimum
2. **Claude 3 Sonnet/Opus for testing** - 10-40x more expensive than Haiku
3. **Leaving resources running when not testing** - Continuous charges
4. **Large document sets in Knowledge Bases** - Embedding costs add up

### ✅ What to DO Instead
1. **Use Claude 3 Haiku** - Only $0.25 per 1M input tokens (vs $3 for Sonnet)
2. **Avoid Knowledge Bases during learning** - Use direct context in prompts
3. **Test locally first** - Validate Lambda functions before deploying
4. **Delete resources same day** - Don't leave things running overnight
5. **Batch your tests** - Plan test cases in advance, run efficiently
6. **Set 1-day log retention** - Reduce CloudWatch storage costs

## 📊 Expected Costs

### Simple Agent Testing (No Knowledge Base)
```
- 1 Agent with Claude 3 Haiku
- 2 Lambda functions
- 50 test queries
- Total cost: ~$0.02
```

### Agent with Knowledge Base (24 hours)
```
- 1 Agent with Claude 3 Haiku
- 1 Knowledge Base (OpenSearch Serverless)
- 50 test queries
- Total cost: ~$23.30 (OpenSearch is $23!)
```

**Key insight:** Knowledge Bases cost 1000x more than simple agents!

## 🛠️ Tools in This Repository

### `check_aws_costs.sh`
Automated script to investigate your AWS spending and identify expensive resources.

**Usage:**
```bash
./check_aws_costs.sh
```

**Output:**
- Daily cost summary
- Costs by AWS service
- List of all Bedrock resources
- Recommendations for cost reduction

## 📖 Learning Path

### Week 1: Learn Theory (Cost: $0)
- Read AWS Bedrock documentation
- Study the implementation plan
- Design your agent on paper
- Write and test Lambda functions locally

### Week 2: Minimal Testing (Cost: $0.50 - $2)
- Create ONE simple agent (no Knowledge Base)
- Use Claude 3 Haiku
- Run 10-20 focused tests
- Delete agent immediately after

### Week 3: Advanced Features (Optional, Cost: $5-10)
- Create Knowledge Base ONLY if needed
- Test for 1-2 hours MAXIMUM
- DELETE OpenSearch collection same day
- Document your learnings

### Week 4: Production Planning (Cost: $0)
- Design production architecture
- Calculate monthly costs
- Plan your budget ($50-100/month)
- Implement monitoring and alerts

## 🆘 Emergency Cost Control

If costs are running away RIGHT NOW:

```bash
# 1. Delete ALL OpenSearch collections (HIGHEST PRIORITY)
aws opensearchserverless list-collections --region us-east-1 --query 'collectionSummaries[*].id' --output text | \
  xargs -I {} aws opensearchserverless delete-collection --id {} --region us-east-1

# 2. Delete all Bedrock agents
aws bedrock-agent list-agents --region us-east-1 --query 'agentSummaries[*].agentId' --output text | \
  xargs -I {} aws bedrock-agent delete-agent --agent-id {} --region us-east-1

# 3. Delete all Knowledge Bases
aws bedrock-agent list-knowledge-bases --region us-east-1 --query 'knowledgeBaseSummaries[*].knowledgeBaseId' --output text | \
  xargs -I {} aws bedrock-agent delete-knowledge-base --knowledge-base-id {} --region us-east-1

# 4. Verify everything is deleted
./check_aws_costs.sh
```

## 📝 Additional Resources

### AWS Documentation
- [Amazon Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)
- [OpenSearch Serverless Pricing](https://aws.amazon.com/opensearch-service/pricing/)
- [AWS Free Tier Details](https://aws.amazon.com/free/)
- [AWS Cost Management](https://aws.amazon.com/aws-cost-management/)

### Free Alternatives for Learning
- [Ollama - Run LLMs locally](https://ollama.ai/)
- [LM Studio - Local model testing](https://lmstudio.ai/)
- [OpenAI Playground - $5 free credits](https://platform.openai.com/playground)

## 🎯 Next Steps

1. **Investigate costs** → Run `./check_aws_costs.sh`
2. **Delete expensive resources** → Follow script recommendations
3. **Read cost guide** → See [AWS_COST_MANAGEMENT_GUIDE.md](./AWS_COST_MANAGEMENT_GUIDE.md)
4. **Set up alerts** → Create budget in AWS Console
5. **Plan wisely** → Use optimization strategies from the guide
6. **Test smartly** → Use Haiku model, avoid Knowledge Bases

## 📧 Questions?

For AWS Bedrock questions:
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS Support Forums](https://repost.aws/)

For cost management questions:
- Review the [AWS_COST_MANAGEMENT_GUIDE.md](./AWS_COST_MANAGEMENT_GUIDE.md)
- Use [AWS Pricing Calculator](https://calculator.aws/)

---

**Remember:** When learning AWS Bedrock on Free Tier, avoid Knowledge Bases and always use Claude 3 Haiku for testing! 🚀
