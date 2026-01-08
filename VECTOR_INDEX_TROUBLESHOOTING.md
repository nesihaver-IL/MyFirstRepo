# Vector Index Troubleshooting Guide for AWS Bedrock Agents

## Problem: Vector Index Failed After Adding Resources

When you attach files as resources to extend your agent's knowledge in AWS Bedrock (Foundry AI), the Vector Index creation can fail for several reasons.

---

## Common Root Causes

### 1. **Knowledge Base Sync Not Complete** (Most Common)
**What went wrong:**
- The Vector Index sync process takes 5-30 minutes
- If you tried to use the agent before sync completed, it will fail
- The sync status might show "Failed" or "Syncing" in the console

**How to fix:**
1. Navigate to **Bedrock Console → Knowledge Bases**
2. Select your knowledge base
3. Check the **Sync Status**
4. If status is "Failed" or "Syncing":
   - Click **"Sync"** button to restart the sync
   - Wait 5-30 minutes for completion
   - Monitor the sync progress

**Verification:**
```bash
# Check sync status via AWS CLI
aws bedrock-agent get-knowledge-base \
  --knowledge-base-id YOUR_KB_ID \
  --region us-east-1 \
  --query 'knowledgeBase.status'
```

---

### 2. **S3 Bucket Permissions Issue**
**What went wrong:**
- Bedrock service doesn't have permission to read your S3 bucket
- Bucket policy is missing or incorrect
- IAM role lacks S3 read permissions

**How to fix:**

**Step 1: Verify S3 bucket policy**
Add this policy to your S3 bucket:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowBedrockToReadBucket",
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock.amazonaws.com"
      },
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::YOUR-BUCKET-NAME/*",
        "arn:aws:s3:::YOUR-BUCKET-NAME"
      ],
      "Condition": {
        "StringEquals": {
          "aws:SourceAccount": "YOUR-ACCOUNT-ID"
        }
      }
    }
  ]
}
```

**Step 2: Update IAM Role**
Ensure your Bedrock Agent IAM role has this policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::YOUR-BUCKET-NAME/*",
        "arn:aws:s3:::YOUR-BUCKET-NAME"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v1"
    },
    {
      "Effect": "Allow",
      "Action": [
        "aoss:APIAccessAll"
      ],
      "Resource": "arn:aws:aoss:*:*:collection/*"
    }
  ]
}
```

---

### 3. **Invalid Document Format**
**What went wrong:**
- Uploaded files are in unsupported format
- Files are corrupted or empty
- Files contain only images (no extractable text)
- File size exceeds limits

**Supported formats:**
- ✅ PDF (.pdf)
- ✅ Plain Text (.txt)
- ✅ Markdown (.md)
- ✅ HTML (.html)
- ✅ Word Documents (.doc, .docx)
- ❌ Images alone (unless with OCR)
- ❌ Executables, binaries
- ❌ Files > 50MB

**How to fix:**
1. **Check file formats:**
   ```bash
   # List files in your S3 bucket
   aws s3 ls s3://YOUR-BUCKET-NAME/ --recursive
   ```

2. **Validate files:**
   - Open each file and ensure it contains readable text
   - Remove any corrupted files
   - Convert unsupported formats to PDF or TXT

3. **Re-upload clean files:**
   ```bash
   # Remove all files
   aws s3 rm s3://YOUR-BUCKET-NAME/ --recursive

   # Upload cleaned files
   aws s3 cp ./cleaned-documents/ s3://YOUR-BUCKET-NAME/ --recursive
   ```

4. **Trigger new sync:**
   - Go to Bedrock Console → Knowledge Bases
   - Click your knowledge base
   - Click **"Sync"**

---

### 4. **OpenSearch Serverless Configuration Issue**
**What went wrong:**
- Vector database (OpenSearch Serverless) wasn't properly created
- Network access policy is missing
- Data access policy is incorrect

**How to fix:**

**Step 1: Verify OpenSearch Serverless collection exists**
```bash
aws opensearchserverless list-collections --region us-east-1
```

**Step 2: Check data access policy**
Navigate to OpenSearch Serverless console and ensure your Bedrock IAM role has access:
```json
[
  {
    "Rules": [
      {
        "Resource": ["collection/YOUR-COLLECTION-NAME"],
        "Permission": [
          "aoss:CreateCollectionItems",
          "aoss:UpdateCollectionItems",
          "aoss:DescribeCollectionItems"
        ],
        "ResourceType": "collection"
      },
      {
        "Resource": ["index/YOUR-COLLECTION-NAME/*"],
        "Permission": [
          "aoss:CreateIndex",
          "aoss:UpdateIndex",
          "aoss:DescribeIndex",
          "aoss:ReadDocument",
          "aoss:WriteDocument"
        ],
        "ResourceType": "index"
      }
    ],
    "Principal": [
      "arn:aws:iam::YOUR-ACCOUNT-ID:role/BedrockAgentRole"
    ]
  }
]
```

**Step 3: Recreate knowledge base if needed**
If the OpenSearch collection is misconfigured, you may need to:
1. Delete the existing knowledge base
2. Create a new knowledge base
3. Let Bedrock create a new managed OpenSearch Serverless collection

---

### 5. **Chunking Strategy Issues**
**What went wrong:**
- Default chunking doesn't work well for your document types
- Documents are being split incorrectly
- Chunks are too small or too large

**How to fix:**

**Option 1: Use Custom Chunking**
1. Go to Bedrock Console → Knowledge Bases → Your KB
2. Click **Edit**
3. Scroll to **Chunking Strategy**
4. Select **Custom chunking**
5. Configure:
   - **Max tokens per chunk:** 300-500 (default: 300)
   - **Overlap percentage:** 20% (to maintain context)

**Option 2: Pre-process Documents**
For better results, prepare documents with:
- Clear section headers
- Logical paragraph breaks
- Remove excessive whitespace
- Add metadata tags if needed

**Test chunking:**
```python
# Python script to test chunk visibility
import boto3

client = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

response = client.retrieve(
    knowledgeBaseId='YOUR_KB_ID',
    retrievalQuery={
        'text': 'Test query about your documents'
    }
)

# Review what chunks are being retrieved
for result in response['retrievalResults']:
    print(f"Content: {result['content']['text']}")
    print(f"Score: {result['score']}")
    print("---")
```

---

### 6. **Embeddings Model Access Not Enabled**
**What went wrong:**
- Titan Embeddings model access not requested/approved
- Wrong embeddings model selected

**How to fix:**
1. Navigate to **Bedrock Console → Model Access**
2. Ensure these models are enabled:
   - ✅ **Amazon Titan Embeddings G1 - Text** (required for vector index)
   - ✅ **Anthropic Claude 3 Sonnet** (for agent)
3. If not enabled:
   - Click **"Modify model access"**
   - Check the required models
   - Click **"Save changes"**
   - Wait for approval (usually instant)

---

### 7. **Region Mismatch**
**What went wrong:**
- S3 bucket is in different region than Bedrock agent
- OpenSearch collection is in different region
- Cross-region access not configured

**How to fix:**
1. **Check all resources are in same region:**
   ```bash
   # Check agent region
   aws bedrock-agent list-agents --region us-east-1

   # Check S3 bucket region
   aws s3api get-bucket-location --bucket YOUR-BUCKET-NAME

   # Check OpenSearch collections
   aws opensearchserverless list-collections --region us-east-1
   ```

2. **If regions don't match:**
   - Create new S3 bucket in same region as agent
   - Copy documents to new bucket
   - Update knowledge base data source

---

## Step-by-Step Fix Procedure

### ✅ Complete Fix Workflow

**Step 1: Diagnose the Issue**
```bash
# Check knowledge base status
aws bedrock-agent get-knowledge-base \
  --knowledge-base-id YOUR_KB_ID \
  --region us-east-1

# Check for error messages in CloudWatch
aws logs tail /aws/bedrock/knowledgebases/YOUR_KB_ID --follow
```

**Step 2: Verify Permissions**
- [ ] S3 bucket policy allows Bedrock access
- [ ] IAM role has S3 read permissions
- [ ] IAM role has Bedrock InvokeModel permissions
- [ ] IAM role has OpenSearch Serverless access
- [ ] Titan Embeddings model is enabled

**Step 3: Verify Documents**
- [ ] All files are in supported formats
- [ ] Files contain extractable text
- [ ] Files are under size limits
- [ ] No corrupted files

**Step 4: Trigger Sync**
1. Bedrock Console → Knowledge Bases
2. Select your knowledge base
3. Click **"Sync"**
4. Wait 5-30 minutes
5. Monitor sync status

**Step 5: Test Knowledge Base**
1. Click **"Test"** in knowledge base console
2. Ask a question from your documents
3. Verify results are returned
4. Check relevance scores

**Step 6: Attach to Agent**
1. Navigate to your Bedrock Agent
2. Go to **"Knowledge bases"** section
3. Click **"Add knowledge base"**
4. Select your synced knowledge base
5. Add instructions:
   ```
   Use this knowledge base to answer questions about [your topic].
   Always cite sources when using knowledge base information.
   If the information isn't in the knowledge base, say so clearly.
   ```
6. Click **"Save"**
7. Click **"Prepare"** agent (top right)
8. Wait for agent to prepare (1-2 minutes)

**Step 7: Test End-to-End**
1. Click **"Test"** in agent console
2. Ask questions that require knowledge base
3. Verify agent retrieves correct information
4. Check trace details for knowledge base queries

---

## Prevention for Future Knowledge Base Creation

### Best Practices Checklist
- [ ] Create all resources in same AWS region
- [ ] Use Bedrock's managed OpenSearch Serverless (simplest)
- [ ] Enable required models before creating knowledge base
- [ ] Use clear document structure with headers
- [ ] Start with small document set (5-10 files) to test
- [ ] Test knowledge base independently before attaching to agent
- [ ] Use versioned S3 bucket
- [ ] Set up CloudWatch logging from the start
- [ ] Document your IAM policies

### Optimal Document Preparation
```bash
# Example: Organize documents before upload
mkdir -p kb-documents/{policies,procedures,faqs}

# Place documents in logical folders
cp policy*.pdf kb-documents/policies/
cp procedure*.pdf kb-documents/procedures/
cp faq*.txt kb-documents/faqs/

# Upload with structure
aws s3 sync ./kb-documents/ s3://YOUR-BUCKET-NAME/ \
  --metadata purpose=knowledge-base
```

---

## Quick Reference Commands

### Check Knowledge Base Status
```bash
aws bedrock-agent get-knowledge-base \
  --knowledge-base-id YOUR_KB_ID \
  --region us-east-1 \
  --query 'knowledgeBase.[status,storageConfiguration]'
```

### Force Knowledge Base Sync
```bash
aws bedrock-agent start-ingestion-job \
  --knowledge-base-id YOUR_KB_ID \
  --data-source-id YOUR_DATA_SOURCE_ID \
  --region us-east-1
```

### List Sync Jobs
```bash
aws bedrock-agent list-ingestion-jobs \
  --knowledge-base-id YOUR_KB_ID \
  --data-source-id YOUR_DATA_SOURCE_ID \
  --region us-east-1
```

### Test Knowledge Base Retrieval
```bash
aws bedrock-agent-runtime retrieve \
  --knowledge-base-id YOUR_KB_ID \
  --retrieval-query text="Your test question" \
  --region us-east-1
```

---

## When to Recreate Knowledge Base

Consider recreating if:
- ❌ Sync fails repeatedly (>3 times)
- ❌ OpenSearch collection is corrupted
- ❌ IAM permissions are too complex to untangle
- ❌ Wrong embedding model was used initially
- ❌ You need to change vector database type

**To recreate:**
1. Note all configuration details
2. Delete existing knowledge base (keeps S3 data)
3. Create new knowledge base with corrected settings
4. Let Bedrock create fresh OpenSearch collection
5. Sync will start automatically

---

## Need More Help?

### Debug with CloudWatch Logs
```bash
# View knowledge base sync logs
aws logs tail /aws/bedrock/knowledgebases/YOUR_KB_ID --follow

# View agent invocation logs
aws logs tail /aws/bedrock/agents/YOUR_AGENT_ID --follow

# Filter for errors
aws logs filter-log-events \
  --log-group-name /aws/bedrock/knowledgebases/YOUR_KB_ID \
  --filter-pattern "ERROR"
```

### Get Support
- **AWS Support Console:** Open a support case
- **AWS Forums:** [Bedrock Discussion Forum](https://repost.aws/tags/TAFtEW2PrZSK29pM-t38oGZg/amazon-bedrock)
- **Documentation:** [AWS Bedrock Knowledge Bases Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)

---

## Summary

**Most likely cause:** Knowledge Base sync not completed or S3 permissions issue

**Quickest fix:**
1. Check sync status in Bedrock Console
2. Verify S3 bucket permissions
3. Re-sync knowledge base
4. Wait 5-30 minutes
5. Test in knowledge base console before attaching to agent

**If that doesn't work:** Follow the complete fix workflow above, checking each component systematically.
