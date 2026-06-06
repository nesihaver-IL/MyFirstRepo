# Image Processing Setup Guide

## Overview

Your AI agent now supports **automatic image description and retrieval** from PowerPoint presentations and image files using GPT-4o Vision. Images are automatically described and indexed as searchable text.

## What Changed

### Before
- ❌ PPT and PNG files were uploaded as binary files
- ❌ Images were replaced with "[Image]" placeholders
- ❌ Only text content was searchable

### After
- ✅ PPT files: Text extracted + images described
- ✅ PNG/JPG files: AI-generated descriptions
- ✅ All content searchable via text queries
- ✅ Agent can retrieve information about images

## How It Works

```
1. You upload a PPT or PNG file
   ↓
2. System extracts text from slides (PPT only)
   ↓
3. GPT-4o Vision describes each image
   ↓
4. Combined content saved as searchable text
   ↓
5. Agent can now retrieve image information
```

### Example

**Input PPT Slide:**
- Title: "Q4 Sales Performance"
- Chart image: Bar chart showing revenue growth
- Bullet points: "Revenue up 25%", "New markets expanding"

**What Gets Indexed:**
```
--- Slide 1 ---
Q4 Sales Performance
Revenue up 25%
New markets expanding

[Image Description: A bar chart displaying quarterly sales performance
with vertical bars showing progressive revenue growth across Q1-Q4.
Q4 shows the highest bar at approximately 25% increase. The chart uses
blue bars with gridlines and axis labels for revenue in millions.]
```

**User Query:** "Show me the sales chart from Q4"

**Agent Response:** "The Q4 presentation includes a bar chart showing
quarterly sales performance with revenue growth across Q1-Q4, with Q4
showing the highest performance at approximately 25% increase..."

## Setup Instructions

### 1. Install Required Dependencies

```bash
cd /home/user/MyFirstRepo/02-work/ai-foundry-agent
pip install -r requirements.txt
```

New dependencies added:
- `python-pptx==0.6.23` - PowerPoint file processing
- `Pillow==10.4.0` - Image handling
- `PyPDF2==3.0.1` - PDF processing (future use)

### 2. Configure Azure OpenAI

Add these variables to your `.env` file:

```bash
# Required for image processing
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com
AZURE_OPENAI_API_KEY=your-api-key-here
```

**Where to find these:**

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Azure OpenAI resource
3. Click "Keys and Endpoint" in the left menu
4. Copy:
   - **Endpoint** → `AZURE_OPENAI_ENDPOINT`
   - **Key 1** or **Key 2** → `AZURE_OPENAI_API_KEY`

### 3. Verify GPT-4o Model Deployment

Your Azure OpenAI resource must have **gpt-4o** deployed:

1. In Azure Portal, go to your OpenAI resource
2. Click "Model deployments" → "Manage Deployments"
3. Verify `gpt-4o` is listed with status "Succeeded"
4. If not deployed:
   - Click "Create new deployment"
   - Select `gpt-4o` model
   - Set deployment name to `gpt-4o`
   - Deploy

### 4. Restart Your Application

```bash
# Stop the current application (Ctrl+C)

# Restart with new configuration
python -m src.api.main
# or
uvicorn src.api.main:app --reload
```

### 5. Verify Setup

Check the logs on startup:

```
✅ SUCCESS:
INFO - Initialized image processing components
INFO - Application started successfully

❌ FAILURE (image processing disabled):
WARNING - Azure OpenAI credentials not provided. Image processing disabled.
```

## Usage

### Upload Files via API

```bash
# Upload a PowerPoint presentation
curl -X POST "http://localhost:8000/upload-files" \
  -H "Content-Type: application/json" \
  -d '{
    "file_paths": ["/path/to/presentation.pptx"]
  }'

# Upload image files
curl -X POST "http://localhost:8000/upload-files" \
  -H "Content-Type: application/json" \
  -d '{
    "file_paths": [
      "/path/to/chart.png",
      "/path/to/diagram.jpg"
    ]
  }'
```

### Upload Files via Python

```python
from src.agent import KnowledgeHubAgent, AgentConfig

# Initialize agent
config = AgentConfig(
    subscription_id="your-sub-id",
    resource_group="your-rg",
    project_name="your-project",
    azure_openai_endpoint="https://your-openai.openai.azure.com",
    azure_openai_api_key="your-key",
)

agent = KnowledgeHubAgent(config=config)
agent.create_vector_store()
agent.create_agent()

# Upload files with automatic preprocessing
file_ids = agent.upload_files([
    "data/quarterly_report.pptx",
    "images/sales_chart.png",
])

print(f"Uploaded {len(file_ids)} files")
```

### Query the Agent

```python
# Query about images
response = agent.query("What does the sales chart show?")
print(response)

# Query about presentation content
response = agent.query("Summarize the Q4 performance slides")
print(response)
```

## Supported File Types

| File Type | Extension | Processing |
|-----------|-----------|------------|
| PowerPoint | `.ppt`, `.pptx` | Text extraction + image description |
| Images | `.png`, `.jpg`, `.jpeg` | AI-generated description |
| Images | `.gif`, `.bmp`, `.webp` | AI-generated description |
| Text | `.txt`, `.md` | Direct indexing (no preprocessing) |

## How Image Descriptions Work

### Description Quality

GPT-4o Vision generates comprehensive descriptions including:

- **Main subject:** What the image shows
- **Visual elements:** Charts, diagrams, text, objects
- **Data/information:** Key metrics, trends, values
- **Context:** Slide title and surrounding text (for PPT)
- **Purpose:** Intended message or insight

### Description Example

**Image Input:** Sales performance bar chart

**Generated Description:**
> "A bar chart displaying quarterly sales performance with vertical bars
> showing progressive revenue growth across Q1 through Q4. Each bar is
> colored in blue with the height representing revenue in millions. Q4
> shows the highest bar at approximately 25% increase compared to Q1.
> The chart includes gridlines, axis labels, and a title 'Sales Performance'.
> The trend indicates consistent growth throughout the year."

### Customization

To adjust description detail level, edit `src/vector-store/image_describer.py`:

```python
# Line 50: Change detail_level parameter
response = self.openai_client.chat.completions.create(
    model=self.model,
    messages=[...],
    max_tokens=500,  # Increase for longer descriptions
)
```

Available detail levels:
- `"low"` - Basic overview (faster, cheaper)
- `"high"` - Detailed analysis (default)
- `"auto"` - Automatic based on image complexity

## Logs and Monitoring

### What to Look For

**Successful preprocessing:**
```
INFO - Processing PowerPoint: quarterly_report.pptx (15 slides)
INFO - Described image on slide 3 of quarterly_report.pptx
INFO - Described image on slide 7 of quarterly_report.pptx
INFO - Generated description for sales_chart.png
INFO - Uploaded preprocessed quarterly_report.pptx: file-abc123
INFO - Added 1 files to vector store
```

**Preprocessing disabled (missing credentials):**
```
WARNING - Azure OpenAI credentials not provided. Image processing disabled.
WARNING - Image processing not available for chart.png. Uploading as binary (text extraction may be limited).
```

**Errors:**
```
ERROR - Error describing image sales_chart.png: [error details]
ERROR - Error uploading file presentation.pptx: [error details]
```

## Cost Considerations

### GPT-4o Vision API Costs

Each image processed incurs:
- **Base cost:** ~$0.0025 per image (varies by region)
- **Detail level:** "high" costs more than "low"
- **Token usage:** ~150-500 tokens per description

**Example:**
- 50-slide PowerPoint with 25 images
- Cost: ~$0.06 per presentation
- Processing time: ~30 seconds

### Optimization Tips

1. **Reduce detail for simple images:**
   ```python
   # In image_describer.py, line 35
   detail_level: str = "low"  # Change from "high"
   ```

2. **Process only unique images:**
   - Avoid duplicate images across presentations
   - Consider deduplication logic for large batches

3. **Use caching:**
   - System automatically creates temp files during processing
   - No duplicate processing for same file uploads

## Troubleshooting

### Issue: "Image processing disabled" warning

**Cause:** Azure OpenAI credentials not configured

**Solution:**
1. Verify `.env` file has correct values:
   ```bash
   cat .env | grep OPENAI
   ```
2. Check endpoint URL format (must include `https://`)
3. Verify API key is valid (try in Azure Portal)
4. Restart application

### Issue: "Error describing image" errors

**Cause:** GPT-4o model not deployed or quota exceeded

**Solution:**
1. Verify model deployment:
   ```bash
   # Check Azure Portal → OpenAI → Model deployments
   ```
2. Check quota limits in Azure Portal
3. Verify image file is not corrupted:
   ```python
   from PIL import Image
   Image.open("problem_image.png").verify()
   ```

### Issue: Agent doesn't retrieve image content

**Cause:** Files uploaded before feature was enabled

**Solution:**
1. Delete old vector store
2. Re-upload files with new preprocessing enabled
3. Query again

### Issue: "No content extracted" from PPT

**Cause:** PowerPoint file uses unsupported format or is corrupted

**Solution:**
1. Open PPT in Microsoft PowerPoint
2. Save as newer `.pptx` format
3. Try uploading again

## Testing

### Quick Test

1. Create a test image:
   ```bash
   # Use any PNG/JPG image, or create one:
   python -c "from PIL import Image; Image.new('RGB', (400,300), 'blue').save('test.png')"
   ```

2. Upload and query:
   ```python
   agent.upload_files(["test.png"])
   response = agent.query("What does the test image show?")
   print(response)
   ```

### Test with PowerPoint

1. Create test presentation with:
   - Text slides
   - Slides with images/charts

2. Upload:
   ```python
   agent.upload_files(["test_presentation.pptx"])
   ```

3. Check logs for:
   ```
   INFO - Processing PowerPoint: test_presentation.pptx (X slides)
   INFO - Described image on slide Y
   ```

4. Query:
   ```python
   response = agent.query("What charts are in the presentation?")
   ```

## Next Steps

### Recommended Enhancements

1. **Add PDF Support:**
   - Extract images from PDFs
   - Already have PyPDF2 dependency

2. **Implement Image Caching:**
   - Cache descriptions for duplicate images
   - Reduce API costs

3. **Add OCR for Text in Images:**
   - Use Azure Computer Vision OCR
   - Extract text from infographics

4. **Multimodal Vector Search:**
   - Use CLIP embeddings for visual similarity
   - Enable "find similar images" queries

## Support

### Documentation
- Azure AI Foundry: https://learn.microsoft.com/azure/ai-studio/
- GPT-4o Vision: https://learn.microsoft.com/azure/ai-services/openai/how-to/gpt-with-vision

### Need Help?
- Check logs in application output
- Review error messages in Azure Portal
- Verify all environment variables are set correctly

---

**Status:** ✅ Implementation complete and ready to use

**Last updated:** 2026-01-21
