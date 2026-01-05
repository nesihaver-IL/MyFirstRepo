#!/bin/bash

# AWS Cost Investigation Script
# This script helps you quickly identify what's consuming your AWS budget

set -e

REGION="${AWS_REGION:-us-east-1}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "unknown")

echo "=================================================="
echo "AWS Cost Investigation Report"
echo "=================================================="
echo "Account: $ACCOUNT_ID"
echo "Region: $REGION"
echo "Date: $(date)"
echo "=================================================="
echo ""

# Function to check if AWS CLI is configured
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        echo "❌ AWS CLI not found. Please install it first."
        exit 1
    fi

    if ! aws sts get-caller-identity &> /dev/null; then
        echo "❌ AWS CLI not configured. Run 'aws configure' first."
        exit 1
    fi
    echo "✅ AWS CLI configured"
}

# Function to get today's costs
get_daily_costs() {
    echo ""
    echo "📊 COST SUMMARY (Last 7 Days)"
    echo "=================================================="

    START_DATE=$(date -d '7 days ago' +%Y-%m-%d 2>/dev/null || date -v-7d +%Y-%m-%d)
    END_DATE=$(date +%Y-%m-%d)

    aws ce get-cost-and-usage \
        --time-period Start=$START_DATE,End=$END_DATE \
        --granularity DAILY \
        --metrics "UnblendedCost" \
        --region us-east-1 \
        --query 'ResultsByTime[*].[TimePeriod.Start,Total.UnblendedCost.Amount]' \
        --output text | while read date cost; do
            printf "%s: \$%.2f\n" "$date" "$cost"
        done
}

# Function to get costs by service
get_service_costs() {
    echo ""
    echo "💰 COSTS BY SERVICE (Last 7 Days)"
    echo "=================================================="

    START_DATE=$(date -d '7 days ago' +%Y-%m-%d 2>/dev/null || date -v-7d +%Y-%m-%d)
    END_DATE=$(date +%Y-%m-%d)

    aws ce get-cost-and-usage \
        --time-period Start=$START_DATE,End=$END_DATE \
        --granularity DAILY \
        --metrics "UnblendedCost" \
        --group-by Type=DIMENSION,Key=SERVICE \
        --region us-east-1 \
        --query 'ResultsByTime[0].Groups[?Metrics.UnblendedCost.Amount > `0.01`].[Keys[0],Metrics.UnblendedCost.Amount]' \
        --output text | sort -k2 -rn | while read service cost; do
            printf "%-40s \$%.2f\n" "$service" "$cost"
        done
}

# Function to check OpenSearch Serverless (BIGGEST COST DRIVER)
check_opensearch() {
    echo ""
    echo "⚠️  OPENSEARCH SERVERLESS COLLECTIONS (EXPENSIVE!)"
    echo "=================================================="

    collections=$(aws opensearchserverless list-collections --region $REGION --query 'collectionSummaries[*].[name,id,status]' --output text 2>/dev/null)

    if [ -z "$collections" ]; then
        echo "✅ No OpenSearch collections found (Good!)"
    else
        echo "❌ WARNING: OpenSearch collections found!"
        echo "Each collection costs ~\$350/month minimum!"
        echo ""
        echo "$collections" | while read name id status; do
            echo "Collection: $name"
            echo "  ID: $id"
            echo "  Status: $status"
            echo "  Estimated cost: ~\$350/month (4 OCUs)"
            echo ""
        done
        echo "🔥 DELETE THESE IMMEDIATELY if not needed:"
        echo "$collections" | while read name id status; do
            echo "  aws opensearchserverless delete-collection --id $id --region $REGION"
        done
    fi
}

# Function to check Bedrock agents
check_bedrock_agents() {
    echo ""
    echo "🤖 BEDROCK AGENTS"
    echo "=================================================="

    agents=$(aws bedrock-agent list-agents --region $REGION --query 'agentSummaries[*].[agentName,agentId,agentStatus]' --output text 2>/dev/null)

    if [ -z "$agents" ]; then
        echo "No Bedrock agents found"
    else
        echo "Found agents:"
        echo "$agents" | while read name id status; do
            echo "  - $name (ID: $id, Status: $status)"
        done

        echo ""
        echo "To delete an agent:"
        echo "$agents" | while read name id status; do
            echo "  aws bedrock-agent delete-agent --agent-id $id --region $REGION"
        done
    fi
}

# Function to check Knowledge Bases
check_knowledge_bases() {
    echo ""
    echo "📚 BEDROCK KNOWLEDGE BASES"
    echo "=================================================="

    kbs=$(aws bedrock-agent list-knowledge-bases --region $REGION --query 'knowledgeBaseSummaries[*].[name,knowledgeBaseId,status]' --output text 2>/dev/null)

    if [ -z "$kbs" ]; then
        echo "No knowledge bases found"
    else
        echo "Found knowledge bases:"
        echo "$kbs" | while read name id status; do
            echo "  - $name (ID: $id, Status: $status)"
        done

        echo ""
        echo "To delete a knowledge base:"
        echo "$kbs" | while read name id status; do
            echo "  aws bedrock-agent delete-knowledge-base --knowledge-base-id $id --region $REGION"
        done
    fi
}

# Function to check Lambda functions
check_lambda_functions() {
    echo ""
    echo "λ LAMBDA FUNCTIONS"
    echo "=================================================="

    functions=$(aws lambda list-functions --region $REGION --query 'Functions[*].[FunctionName,Runtime,LastModified]' --output text 2>/dev/null)

    if [ -z "$functions" ]; then
        echo "No Lambda functions found"
    else
        count=$(echo "$functions" | wc -l)
        echo "Found $count Lambda function(s)"
        echo ""
        echo "$functions" | head -10 | while read name runtime modified; do
            echo "  - $name (Runtime: $runtime)"
        done

        if [ "$count" -gt 10 ]; then
            echo "  ... and $((count - 10)) more"
        fi
    fi
}

# Function to check S3 buckets
check_s3_buckets() {
    echo ""
    echo "🪣 S3 BUCKETS"
    echo "=================================================="

    buckets=$(aws s3 ls 2>/dev/null | awk '{print $3}')

    if [ -z "$buckets" ]; then
        echo "No S3 buckets found"
    else
        count=$(echo "$buckets" | wc -l)
        echo "Found $count bucket(s)"
        echo ""

        for bucket in $buckets; do
            size=$(aws s3 ls s3://$bucket --recursive --summarize 2>/dev/null | grep "Total Size" | awk '{print $3}')
            if [ -n "$size" ]; then
                size_mb=$(echo "scale=2; $size / 1024 / 1024" | bc)
                echo "  - $bucket: ${size_mb} MB"
            else
                echo "  - $bucket: 0 MB (empty)"
            fi
        done
    fi
}

# Function to check CloudWatch log groups
check_cloudwatch_logs() {
    echo ""
    echo "📝 CLOUDWATCH LOG GROUPS"
    echo "=================================================="

    logs=$(aws logs describe-log-groups --region $REGION --query 'logGroups[*].[logGroupName,storedBytes]' --output text 2>/dev/null)

    if [ -z "$logs" ]; then
        echo "No log groups found"
    else
        total_bytes=0
        echo "$logs" | while read name bytes; do
            total_bytes=$((total_bytes + bytes))
            mb=$(echo "scale=2; $bytes / 1024 / 1024" | bc)
            if (( $(echo "$mb > 1" | bc -l) )); then
                echo "  - $name: ${mb} MB"
            fi
        done

        total_mb=$(echo "scale=2; $total_bytes / 1024 / 1024" | bc)
        echo ""
        echo "Total log storage: ${total_mb} MB"
        echo "Free tier limit: 5 GB (5120 MB)"
    fi
}

# Function to provide recommendations
provide_recommendations() {
    echo ""
    echo "💡 COST REDUCTION RECOMMENDATIONS"
    echo "=================================================="
    echo ""
    echo "1. ⚠️  DELETE OpenSearch Serverless collections immediately"
    echo "   These cost ~\$350/month each, even if unused!"
    echo ""
    echo "2. 🎯 Use Claude 3 Haiku instead of Sonnet/Opus for testing"
    echo "   Haiku is 10x cheaper: \$0.25 vs \$3 per 1M input tokens"
    echo ""
    echo "3. 🚫 Avoid Knowledge Bases for learning/testing"
    echo "   Use direct context in prompts instead"
    echo ""
    echo "4. 🔄 Delete resources immediately after testing"
    echo "   Don't leave agents/functions running when not in use"
    echo ""
    echo "5. ⏱️  Set CloudWatch log retention to 1 day for test environments"
    echo "   Reduces storage costs significantly"
    echo ""
    echo "6. 💰 Create budget alerts at \$5/day to catch issues early"
    echo "   AWS Budgets → Create budget → Daily limit \$5"
    echo ""
    echo "For detailed guidance, see: AWS_COST_MANAGEMENT_GUIDE.md"
    echo ""
}

# Main execution
main() {
    check_aws_cli
    get_daily_costs
    get_service_costs
    check_opensearch
    check_bedrock_agents
    check_knowledge_bases
    check_lambda_functions
    check_s3_buckets
    check_cloudwatch_logs
    provide_recommendations

    echo ""
    echo "=================================================="
    echo "Investigation complete!"
    echo "=================================================="
}

# Run main function
main
