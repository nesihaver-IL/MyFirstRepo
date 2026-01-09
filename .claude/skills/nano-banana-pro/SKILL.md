---
name: nano-banana-pro
description: Generate images using Google Gemini 3 Pro Image API. Use when creating high-quality images with text rendering, character consistency, or professional visual content. Triggers on image generation, Gemini Pro, visual content, AI images.
---

# Nano Banana Pro (Gemini 3 Pro Image)

Generate high-quality images using Google's Gemini 3 Pro Image API.

## Features

- Professional text rendering
- Character consistency (up to 5 subjects)
- Multiple aspect ratios (1:1, 3:2, 16:9, 9:16, 21:9)
- Resolution from 1K to 4K
- Google Search grounding for current information
- Iterative editing through multi-turn conversations

## Installation

```bash
pip install google-generativeai
```

## Quick Start (Python)

```python
import google.generativeai as genai

# Configure API
genai.configure(api_key="YOUR_API_KEY")

# Initialize model
model = genai.GenerativeModel('gemini-3-pro-image')

# Generate image
response = model.generate_content(
    "A serene mountain landscape at sunset with vibrant colors",
    generation_config={
        'response_modalities': ['TEXT', 'IMAGE'],
        'aspect_ratio': '16:9',
        'resolution': '2K'
    }
)

# Access generated image
image = response.parts[0].inline_data
with open('output.jpg', 'wb') as f:
    f.write(image.data)
```

## Configuration Options

```python
generation_config = {
    'response_modalities': ['TEXT', 'IMAGE'],
    'aspect_ratio': '16:9',  # Options: 1:1, 3:2, 16:9, 9:16, 21:9
    'resolution': '2K',      # Options: 1K, 2K, 4K
    'enable_search': True,   # Enable Google Search grounding
}
```

## REST API

```bash
curl https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image:generateContent \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: YOUR_API_KEY" \
  -d '{
    "contents": [{
      "parts": [{
        "text": "A modern tech startup office with glass walls"
      }]
    }],
    "generationConfig": {
      "responseModalities": ["TEXT", "IMAGE"],
      "aspectRatio": "16:9",
      "resolution": "2K"
    }
  }'
```

## TypeScript/JavaScript

```typescript
import { GoogleGenerativeAI } from '@google/generative-ai';

const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);

async function generateImage(prompt: string) {
  const model = genAI.getGenerativeModel({ model: 'gemini-3-pro-image' });

  const result = await model.generateContent({
    contents: [{ role: 'user', parts: [{ text: prompt }] }],
    generationConfig: {
      responseModalities: ['TEXT', 'IMAGE'],
      aspectRatio: '16:9',
      resolution: '2K',
    },
  });

  const response = result.response;
  const image = response.parts[0].inlineData;

  return image;
}
```

## Next.js API Route

```typescript
// app/api/generate-image/route.ts
import { GoogleGenerativeAI } from '@google/generative-ai';
import { NextResponse } from 'next/server';

const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY!);

export async function POST(request: Request) {
  try {
    const { prompt, aspectRatio = '16:9', resolution = '2K' } = await request.json();

    const model = genAI.getGenerativeModel({ model: 'gemini-3-pro-image' });

    const result = await model.generateContent({
      contents: [{ role: 'user', parts: [{ text: prompt }] }],
      generationConfig: {
        responseModalities: ['TEXT', 'IMAGE'],
        aspectRatio,
        resolution,
      },
    });

    const image = result.response.parts[0].inlineData;

    return NextResponse.json({
      success: true,
      image: {
        data: Buffer.from(image.data).toString('base64'),
        mimeType: image.mimeType,
      }
    });
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Failed to generate image' },
      { status: 500 }
    );
  }
}
```

## Character Consistency

```python
# First image with character
response1 = model.generate_content(
    "A friendly robot character with blue metallic body"
)

# Maintain character in new scene
response2 = model.generate_content([
    response1.parts[0],  # Reference previous image
    "The same robot character now in a futuristic city"
])
```

## With Google Search Grounding

```python
response = model.generate_content(
    "Latest iPhone model with accurate details",
    generation_config={
        'response_modalities': ['TEXT', 'IMAGE'],
        'enable_search': True,  # Uses Google Search for accuracy
        'resolution': '2K'
    }
)
```

## Iterative Editing

```python
# Initial generation
chat = model.start_chat()

response1 = chat.send_message(
    "A modern kitchen with marble countertops",
    generation_config={'response_modalities': ['TEXT', 'IMAGE']}
)

# Refine the image
response2 = chat.send_message(
    "Add more natural lighting and plants"
)

# Further refinement
response3 = chat.send_message(
    "Change countertops to dark wood"
)
```

## Performance vs Quality

- **Gemini 3 Pro Image**: Higher quality, slower (production use)
- **Gemini 2.5 Flash**: Faster processing, lower quality (prototyping)

```python
# For production
model = genai.GenerativeModel('gemini-3-pro-image')

# For rapid iteration
model = genai.GenerativeModel('gemini-2.5-flash')
```

## Resources

- **API Docs**: https://ai.google.dev/docs/gemini-api
- **Pricing**: https://ai.google.dev/pricing
