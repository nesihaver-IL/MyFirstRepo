#!/usr/bin/env python3
"""
Convert PPTX to self-contained HTML with embedded images.
Extracts all slides, text, and images from the PPTX file.
"""

import base64
import io
import os
from pathlib import Path
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

def get_image_base64(image_stream):
    """Convert image stream to base64 data URI."""
    image_bytes = image_stream.read()
    image_stream.seek(0)
    b64 = base64.b64encode(image_bytes).decode('utf-8')
    return b64

def extract_text_from_shape(shape):
    """Extract text from a shape if it has a text frame."""
    if hasattr(shape, 'text_frame'):
        text_lines = []
        for paragraph in shape.text_frame.paragraphs:
            if paragraph.text.strip():
                text_lines.append(paragraph.text.strip())
        return text_lines
    return []

def process_slide(slide, slide_num):
    """Extract all content from a slide."""
    slide_data = {
        'number': slide_num,
        'title': '',
        'text_blocks': [],
        'images': []
    }

    # Extract text and images from all shapes
    for shape_idx, shape in enumerate(slide.shapes):
        # Extract text
        text_lines = extract_text_from_shape(shape)
        if text_lines:
            if not slide_data['title'] and shape_idx < 3:
                slide_data['title'] = text_lines[0]
            else:
                slide_data['text_blocks'].extend(text_lines)

        # Extract images
        if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
            try:
                image = shape.image
                image_bytes = image.blob
                mime_type = image.content_type
                b64 = base64.b64encode(image_bytes).decode('utf-8')
                slide_data['images'].append({
                    'data': f'data:{mime_type};base64,{b64}',
                    'width': shape.width,
                    'height': shape.height
                })
            except Exception as e:
                print(f"Warning: Could not extract image from slide {slide_num}: {e}")

    return slide_data

def generate_html(slides_data, output_path):
    """Generate HTML file from extracted slide data."""

    html_parts = [
        '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Microsoft 365 Copilot - Practical Examples and How-tos</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #F8F7F3 0%, #F3F0E8 100%);
            color: #2C3E50;
            line-height: 1.6;
        }

        header {
            background: linear-gradient(90deg, #6B9BD1 0%, #7BA886 100%);
            color: white;
            padding: 3rem 2rem;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }

        header p {
            font-size: 1.1rem;
            opacity: 0.95;
        }

        .search-bar {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 1.5rem;
        }

        .search-bar input {
            width: 100%;
            padding: 0.75rem 1rem;
            font-size: 1rem;
            border: 2px solid #C19A6B;
            border-radius: 8px;
            background: white;
            color: #2C3E50;
        }

        .search-bar input:focus {
            outline: none;
            border-color: #6B9BD1;
            box-shadow: 0 0 8px rgba(107, 155, 209, 0.3);
        }

        nav {
            position: sticky;
            top: 1rem;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 1.5rem;
            z-index: 100;
        }

        .nav-container {
            background: white;
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            max-height: 60vh;
            overflow-y: auto;
        }

        nav a {
            display: block;
            padding: 0.75rem 1rem;
            margin: 0.25rem 0;
            color: #2C3E50;
            text-decoration: none;
            border-left: 4px solid #C19A6B;
            border-radius: 4px;
            transition: all 0.3s ease;
            font-size: 0.95rem;
        }

        nav a:hover {
            background: #F8F7F3;
            border-left-color: #7BA886;
            transform: translateX(4px);
            color: #7BA886;
        }

        nav a.active {
            background: #F0F4F8;
            border-left-color: #6B9BD1;
            color: #6B9BD1;
            font-weight: 600;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 1.5rem 2rem;
        }

        section {
            background: white;
            border-radius: 10px;
            padding: 2.5rem;
            margin: 2rem 0;
            border-top: 4px solid #C19A6B;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            scroll-margin-top: 100px;
        }

        h2 {
            color: #6B9BD1;
            font-size: 2rem;
            margin-bottom: 1.5rem;
            border-bottom: 3px solid #7BA886;
            padding-bottom: 0.75rem;
            position: relative;
            padding-left: 1rem;
        }

        h2::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 4px;
            background: #C19A6B;
            border-radius: 2px;
        }

        h3 {
            color: #7BA886;
            font-size: 1.3rem;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
            position: relative;
            padding-left: 1.5rem;
        }

        h3::before {
            content: '▸';
            position: absolute;
            left: 0;
            color: #C19A6B;
            font-size: 1.5rem;
        }

        p {
            margin-bottom: 1rem;
            line-height: 1.8;
        }

        ul, ol {
            margin: 1rem 0 1rem 2rem;
        }

        li {
            margin-bottom: 0.5rem;
        }

        .slide-images {
            margin: 2rem 0;
            text-align: center;
        }

        .slide-images img {
            max-width: 100%;
            height: auto;
            margin: 1rem 0;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .slide-number {
            display: inline-block;
            background: #C19A6B;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
            margin-bottom: 1rem;
            font-weight: 600;
        }

        footer {
            background: #2C3E50;
            color: white;
            text-align: center;
            padding: 2rem;
            margin-top: 3rem;
            font-size: 0.9rem;
        }

        .hidden {
            display: none !important;
        }

        @media (max-width: 768px) {
            header h1 {
                font-size: 1.8rem;
            }

            section {
                padding: 1.5rem;
            }

            h2 {
                font-size: 1.5rem;
            }

            nav {
                position: relative;
                margin: 2rem auto;
            }

            .nav-container {
                max-height: none;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>Microsoft 365 Copilot</h1>
        <p>Practical Examples and How-tos</p>
    </header>

    <div class="search-bar">
        <input type="text" id="searchInput" placeholder="Search slides...">
    </div>

    <nav>
        <div class="nav-container">
            <strong style="display: block; padding: 0.5rem 0; color: #6B9BD1;">Navigate Slides</strong>
'''
    ]

    # Add navigation links
    for slide in slides_data:
        title = slide['title'] if slide['title'] else f"Slide {slide['number']}"
        html_parts.append(f'            <a href="#slide-{slide["number"]}">{title}</a>\n')

    html_parts.append('''        </div>
    </nav>

    <div class="container">
''')

    # Add slide content
    for slide in slides_data:
        title = slide['title'] if slide['title'] else f"Slide {slide['number']}"
        html_parts.append(f'''        <section id="slide-{slide["number"]}">
            <span class="slide-number">Slide {slide["number"]}</span>
            <h2>{title}</h2>
''')

        if slide['text_blocks']:
            for text in slide['text_blocks']:
                if text.strip():
                    html_parts.append(f'            <p>{text}</p>\n')

        if slide['images']:
            html_parts.append('            <div class="slide-images">\n')
            for img in slide['images']:
                html_parts.append(f'                <img src="{img["data"]}" alt="Slide {slide["number"]} image">\n')
            html_parts.append('            </div>\n')

        html_parts.append('        </section>\n')

    html_parts.append('''    </div>

    <footer>
        <p>Generated from: Microsoft 365 Copilot - Practical Examples and How-tos</p>
        <p>Self-contained HTML with embedded images — ready to share</p>
    </footer>

    <script>
        const searchInput = document.getElementById('searchInput');
        const sections = document.querySelectorAll('section');
        const navLinks = document.querySelectorAll('nav a');

        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            sections.forEach(section => {
                const text = section.textContent.toLowerCase();
                section.classList.toggle('hidden', !text.includes(query));
            });
        });

        window.addEventListener('scroll', () => {
            let current = '';
            sections.forEach(section => {
                const sectionTop = section.offsetTop;
                if (scrollY >= sectionTop - 150) {
                    current = section.getAttribute('id');
                }
            });

            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${current}`) {
                    link.classList.add('active');
                }
            });
        });

        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                target.scrollIntoView({ behavior: 'smooth' });
            });
        });
    </script>
</body>
</html>
''')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(html_parts))

    print(f"✓ HTML file created: {output_path}")
    return output_path

def main():
    script_dir = Path(__file__).parent
    pptx_path = script_dir / "Microsoft 365 Copilot - Practical examples and how-tos.pptx"
    output_path = script_dir / "Microsoft 365 Copilot - Practical examples and how-tos.html"

    if not pptx_path.exists():
        print(f"Error: PPTX file not found at {pptx_path}")
        return

    print(f"Loading PPTX: {pptx_path}")
    prs = Presentation(str(pptx_path))

    print(f"Processing {len(prs.slides)} slides...")
    slides_data = []

    for slide_num, slide in enumerate(prs.slides, 1):
        if slide_num % 10 == 0:
            print(f"  → Processed slide {slide_num}...")
        slide_data = process_slide(slide, slide_num)
        slides_data.append(slide_data)

    print(f"Generating HTML with {len(slides_data)} slides...")
    generate_html(slides_data, str(output_path))

    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"✓ Done! File size: {file_size_mb:.1f} MB")

if __name__ == '__main__':
    main()
