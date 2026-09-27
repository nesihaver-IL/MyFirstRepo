#!/usr/bin/env python3
"""
Disk Space Analyzer
Analyzes folder and file sizes and generates an interactive HTML treemap visualization.
"""

import os
import json
from pathlib import Path
from datetime import datetime


def get_size(path):
    """Calculate total size of a path (file or directory)."""
    total = 0
    try:
        if os.path.isfile(path):
            total = os.path.getsize(path)
        elif os.path.isdir(path):
            for entry in os.scandir(path):
                try:
                    if entry.is_file(follow_symlinks=False):
                        total += entry.stat(follow_symlinks=False).st_size
                    elif entry.is_dir(follow_symlinks=False):
                        total += get_size(entry.path)
                except (PermissionError, FileNotFoundError, OSError):
                    continue
    except (PermissionError, FileNotFoundError, OSError):
        pass
    return total


def format_size(size_bytes):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def analyze_directory(root_path, max_depth=5, min_size_mb=0.1):
    """
    Analyze directory structure and build data for visualization.

    Args:
        root_path: Root directory to analyze
        max_depth: Maximum depth to traverse
        min_size_mb: Minimum size in MB to include in visualization

    Returns:
        Dictionary with hierarchical structure and list of largest items
    """
    min_size_bytes = min_size_mb * 1024 * 1024

    def build_tree(path, depth=0, parent_name=""):
        """Recursively build tree structure."""
        if depth > max_depth:
            return None

        try:
            name = os.path.basename(path) or path
            size = get_size(path)

            if size < min_size_bytes and depth > 0:
                return None

            node = {
                'name': name,
                'path': path,
                'size': size,
                'size_formatted': format_size(size),
                'children': []
            }

            if os.path.isdir(path):
                try:
                    entries = []
                    for entry in os.scandir(path):
                        try:
                            entry_size = get_size(entry.path)
                            entries.append((entry.path, entry_size, entry.is_dir()))
                        except (PermissionError, FileNotFoundError, OSError):
                            continue

                    # Sort by size (largest first)
                    entries.sort(key=lambda x: x[1], reverse=True)

                    # Build children nodes
                    for entry_path, entry_size, is_dir in entries[:100]:  # Limit to top 100 items per folder
                        if entry_size >= min_size_bytes or depth == 0:
                            child = build_tree(entry_path, depth + 1, name)
                            if child:
                                node['children'].append(child)

                except (PermissionError, FileNotFoundError, OSError):
                    pass

            return node

        except (PermissionError, FileNotFoundError, OSError):
            return None

    print(f"Analyzing directory: {root_path}")
    print("This may take a few moments...")

    tree = build_tree(root_path)

    # Collect all items for "largest items" list
    all_items = []

    def collect_items(node):
        """Collect all items from tree."""
        if node:
            all_items.append({
                'path': node['path'],
                'size': node['size'],
                'size_formatted': node['size_formatted'],
                'is_dir': len(node.get('children', [])) > 0 or os.path.isdir(node['path'])
            })
            for child in node.get('children', []):
                collect_items(child)

    collect_items(tree)
    all_items.sort(key=lambda x: x['size'], reverse=True)

    return tree, all_items[:100]  # Return top 100 largest items


def generate_html_visualization(tree_data, largest_items, output_path, root_path):
    """Generate interactive HTML treemap visualization."""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_size = format_size(tree_data['size'])
    item_count = len(largest_items)

    tree_data_json = json.dumps(tree_data)
    largest_items_json = json.dumps(largest_items)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Disk Space Analyzer</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
        }}

        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}

        .header p {{
            font-size: 14px;
            opacity: 0.9;
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f9fafb;
            border-bottom: 1px solid #e5e7eb;
        }}

        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}

        .stat-card h3 {{
            font-size: 12px;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}

        .stat-card p {{
            font-size: 24px;
            font-weight: 600;
            color: #111827;
        }}

        .content {{
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 0;
        }}

        #treemap {{
            padding: 30px;
            min-height: 600px;
        }}

        .sidebar {{
            background: #f9fafb;
            border-left: 1px solid #e5e7eb;
            padding: 30px;
            overflow-y: auto;
            max-height: 800px;
        }}

        .sidebar h2 {{
            font-size: 18px;
            margin-bottom: 20px;
            color: #111827;
        }}

        .item-list {{
            list-style: none;
        }}

        .item-list li {{
            background: white;
            padding: 12px;
            margin-bottom: 8px;
            border-radius: 6px;
            border-left: 3px solid #667eea;
            font-size: 13px;
            transition: transform 0.2s;
        }}

        .item-list li:hover {{
            transform: translateX(4px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .item-size {{
            font-weight: 600;
            color: #667eea;
        }}

        .item-path {{
            color: #6b7280;
            font-size: 11px;
            margin-top: 4px;
            word-break: break-all;
        }}

        .item-type {{
            display: inline-block;
            padding: 2px 6px;
            background: #e5e7eb;
            border-radius: 3px;
            font-size: 10px;
            margin-left: 8px;
            color: #4b5563;
        }}

        .treemap-cell {{
            stroke: white;
            stroke-width: 2px;
            cursor: pointer;
            transition: opacity 0.2s;
        }}

        .treemap-cell:hover {{
            opacity: 0.8;
            stroke: #333;
            stroke-width: 3px;
        }}

        .treemap-text {{
            pointer-events: none;
            font-size: 11px;
            fill: white;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        }}

        .tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 12px;
            border-radius: 6px;
            font-size: 12px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            max-width: 300px;
            z-index: 1000;
        }}

        .breadcrumb {{
            padding: 15px 30px;
            background: #f9fafb;
            border-bottom: 1px solid #e5e7eb;
            font-size: 13px;
            color: #6b7280;
        }}

        .breadcrumb span {{
            cursor: pointer;
            color: #667eea;
        }}

        .breadcrumb span:hover {{
            text-decoration: underline;
        }}

        @media (max-width: 1024px) {{
            .content {{
                grid-template-columns: 1fr;
            }}

            .sidebar {{
                border-left: none;
                border-top: 1px solid #e5e7eb;
                max-height: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💾 Disk Space Analyzer</h1>
            <p>Interactive visualization of your disk usage • Generated on {timestamp}</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <h3>Root Path</h3>
                <p style="font-size: 14px; word-break: break-all;">{root_path}</p>
            </div>
            <div class="stat-card">
                <h3>Total Size</h3>
                <p>{total_size}</p>
            </div>
            <div class="stat-card">
                <h3>Items Analyzed</h3>
                <p>{item_count}</p>
            </div>
        </div>

        <div class="breadcrumb">
            <span id="breadcrumb">Click on any folder to zoom in</span>
        </div>

        <div class="content">
            <div id="treemap"></div>
            <div class="sidebar">
                <h2>📊 Largest Items</h2>
                <ul class="item-list" id="largest-items"></ul>
            </div>
        </div>
    </div>

    <div class="tooltip" id="tooltip"></div>

    <script>
        const data = {tree_data_json};
        const largestItems = {largest_items_json};

        // Populate largest items list
        const largestItemsList = document.getElementById('largest-items');
        largestItems.forEach(item => {{
            const li = document.createElement('li');
            li.innerHTML = `
                <div>
                    <span class="item-size">${{item.size_formatted}}</span>
                    <span class="item-type">${{item.is_dir ? 'Folder' : 'File'}}</span>
                </div>
                <div class="item-path">${{item.path}}</div>
            `;
            largestItemsList.appendChild(li);
        }});

        // Treemap visualization
        const width = document.getElementById('treemap').clientWidth - 60;
        const height = 600;

        const svg = d3.select('#treemap')
            .append('svg')
            .attr('width', width)
            .attr('height', height);

        const tooltip = d3.select('#tooltip');

        const color = d3.scaleOrdinal(d3.schemeTableau10);

        let currentNode = data;

        function render(node) {{
            const root = d3.hierarchy(node)
                .sum(d => d.children && d.children.length > 0 ? 0 : d.size)
                .sort((a, b) => b.value - a.value);

            const treemap = d3.treemap()
                .size([width, height])
                .padding(2)
                .round(true);

            treemap(root);

            svg.selectAll('*').remove();

            const cells = svg.selectAll('g')
                .data(root.leaves())
                .join('g')
                .attr('transform', d => `translate(${{d.x0}},${{d.y0}})`);

            cells.append('rect')
                .attr('class', 'treemap-cell')
                .attr('width', d => d.x1 - d.x0)
                .attr('height', d => d.y1 - d.y0)
                .attr('fill', d => color(d.depth))
                .on('click', (event, d) => {{
                    if (d.data.children && d.data.children.length > 0) {{
                        currentNode = d.data;
                        updateBreadcrumb();
                        render(currentNode);
                    }}
                }})
                .on('mouseover', (event, d) => {{
                    tooltip
                        .style('opacity', 1)
                        .html(`
                            <strong>${{d.data.name}}</strong><br>
                            Size: ${{d.data.size_formatted}}<br>
                            Path: ${{d.data.path}}
                        `)
                        .style('left', (event.pageX + 10) + 'px')
                        .style('top', (event.pageY + 10) + 'px');
                }})
                .on('mouseout', () => {{
                    tooltip.style('opacity', 0);
                }});

            cells.append('text')
                .attr('class', 'treemap-text')
                .selectAll('tspan')
                .data(d => {{
                    const width = d.x1 - d.x0;
                    const height = d.y1 - d.y0;
                    if (width > 60 && height > 30) {{
                        return [d.data.name, d.data.size_formatted];
                    }}
                    return [];
                }})
                .join('tspan')
                .attr('x', 4)
                .attr('y', (d, i) => 13 + i * 12)
                .text(d => d)
                .each(function(d) {{
                    const self = d3.select(this);
                    const textLength = self.node().getComputedTextLength();
                    const width = d3.select(this.parentNode).datum().x1 - d3.select(this.parentNode).datum().x0;
                    if (textLength > width - 8) {{
                        const text = d;
                        const avgCharWidth = textLength / text.length;
                        const maxChars = Math.floor((width - 8) / avgCharWidth) - 3;
                        if (maxChars > 0) {{
                            self.text(text.substring(0, maxChars) + '...');
                        }} else {{
                            self.text('');
                        }}
                    }}
                }});
        }}

        function updateBreadcrumb() {{
            document.getElementById('breadcrumb').innerHTML =
                `<span onclick="resetView()">Root</span> / ${{currentNode.name}}`;
        }}

        function resetView() {{
            currentNode = data;
            document.getElementById('breadcrumb').innerHTML = 'Click on any folder to zoom in';
            render(currentNode);
        }}

        render(currentNode);
    </script>
</body>
</html>
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\n✓ Visualization saved to: {output_path}")
    print(f"✓ Total size analyzed: {total_size}")
    print(f"✓ Number of items: {item_count}")


def main():
    import sys

    # Default to home directory or current directory
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        root_path = os.path.expanduser('~')

    if not os.path.exists(root_path):
        print(f"Error: Path '{root_path}' does not exist")
        sys.exit(1)

    output_path = os.path.join(os.path.expanduser('~'), 'disk_space_map.html')

    print("=" * 60)
    print("Disk Space Analyzer")
    print("=" * 60)
    print(f"Analyzing: {root_path}")
    print(f"Output: {output_path}")
    print("=" * 60)
    print()

    tree_data, largest_items = analyze_directory(root_path)
    generate_html_visualization(tree_data, largest_items, output_path, root_path)

    print(f"\nOpen the file in your browser to view the interactive map:")
    print(f"  file://{output_path}")
    print()


if __name__ == '__main__':
    main()
