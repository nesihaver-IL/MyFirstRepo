---
name: figma
description: Figma API integration for design automation, component code generation, and design token extraction. Use when working with Figma files, extracting design tokens, generating React components from designs, or syncing design systems with code.
---

# Figma API Integration

Automate design workflows and generate code from Figma designs.

## Authentication

```typescript
const FIGMA_TOKEN = process.env.FIGMA_TOKEN;

const headers = {
  'X-Figma-Token': FIGMA_TOKEN,
};
```

## Get File Data

```typescript
async function getFigmaFile(fileKey: string) {
  const response = await fetch(
    `https://api.figma.com/v1/files/${fileKey}`,
    { headers }
  );
  return response.json();
}
```

## Extract File Key from URL

```typescript
// https://www.figma.com/file/ABC123/My-Design
function extractFileKey(url: string): string {
  const match = url.match(/file\/([a-zA-Z0-9]+)/);
  return match ? match[1] : '';
}
```

## Get Components

```typescript
async function getComponents(fileKey: string) {
  const response = await fetch(
    `https://api.figma.com/v1/files/${fileKey}/components`,
    { headers }
  );
  return response.json();
}
```

## Generate React Component

```typescript
interface FigmaNode {
  id: string;
  name: string;
  type: string;
  children?: FigmaNode[];
  fills?: any[];
  strokes?: any[];
  layoutMode?: 'HORIZONTAL' | 'VERTICAL';
  primaryAxisSizingMode?: string;
  counterAxisSizingMode?: string;
  paddingLeft?: number;
  paddingRight?: number;
  paddingTop?: number;
  paddingBottom?: number;
  itemSpacing?: number;
}

function nodeToReact(node: FigmaNode): string {
  const styles = extractStyles(node);
  const children = node.children?.map(nodeToReact).join('\n') || '';

  return `
<div style={{${styles}}}>
  ${children || node.name}
</div>
  `.trim();
}

function extractStyles(node: FigmaNode): string {
  const styles: string[] = [];

  // Layout
  if (node.layoutMode === 'HORIZONTAL') {
    styles.push('display: "flex"');
    styles.push('flexDirection: "row"');
  } else if (node.layoutMode === 'VERTICAL') {
    styles.push('display: "flex"');
    styles.push('flexDirection: "column"');
  }

  // Spacing
  if (node.itemSpacing) {
    styles.push(`gap: "${node.itemSpacing}px"`);
  }

  if (node.paddingLeft || node.paddingTop) {
    const padding = [
      node.paddingTop || 0,
      node.paddingRight || 0,
      node.paddingBottom || 0,
      node.paddingLeft || 0,
    ].join('px ');
    styles.push(`padding: "${padding}px"`);
  }

  // Colors
  if (node.fills?.[0]) {
    const fill = node.fills[0];
    if (fill.type === 'SOLID') {
      const { r, g, b, a = 1 } = fill.color;
      styles.push(`backgroundColor: "rgba(${r*255}, ${g*255}, ${b*255}, ${a})"`);
    }
  }

  return styles.join(', ');
}
```

## Extract Design Tokens

```typescript
async function extractColors(fileKey: string) {
  const file = await getFigmaFile(fileKey);
  const colors: Record<string, string> = {};

  function traverse(node: any) {
    if (node.fills) {
      node.fills.forEach((fill: any) => {
        if (fill.type === 'SOLID') {
          const { r, g, b, a = 1 } = fill.color;
          const hex = rgbToHex(r * 255, g * 255, b * 255);
          colors[node.name] = hex;
        }
      });
    }

    if (node.children) {
      node.children.forEach(traverse);
    }
  }

  traverse(file.document);
  return colors;
}

function rgbToHex(r: number, g: number, b: number): string {
  return '#' + [r, g, b]
    .map(x => Math.round(x).toString(16).padStart(2, '0'))
    .join('');
}
```

## Export as CSS Variables

```typescript
function colorsToCSSVariables(colors: Record<string, string>): string {
  return `:root {
${Object.entries(colors)
  .map(([name, value]) => `  --color-${name.toLowerCase().replace(/\s+/g, '-')}: ${value};`)
  .join('\n')}
}`;
}
```

## Export as Tailwind Config

```typescript
function colorsToTailwind(colors: Record<string, string>): string {
  const entries = Object.entries(colors)
    .map(([name, value]) => `        '${name}': '${value}',`)
    .join('\n');

  return `module.exports = {
  theme: {
    extend: {
      colors: {
${entries}
      },
    },
  },
};`;
}
```

## Get Design Tokens (Variables API)

```typescript
async function getVariables(fileKey: string) {
  const response = await fetch(
    `https://api.figma.com/v1/files/${fileKey}/variables/local`,
    { headers }
  );
  return response.json();
}
```

## Export Images

```typescript
async function exportImage(
  fileKey: string,
  nodeId: string,
  format: 'png' | 'jpg' | 'svg' = 'png',
  scale = 2
) {
  const response = await fetch(
    `https://api.figma.com/v1/images/${fileKey}?ids=${nodeId}&format=${format}&scale=${scale}`,
    { headers }
  );
  const data = await response.json();
  return data.images[nodeId]; // Returns image URL
}
```

## Complete Pipeline Example

```typescript
async function designToCode(figmaUrl: string) {
  const fileKey = extractFileKey(figmaUrl);

  // Get file data
  const file = await getFigmaFile(fileKey);

  // Extract tokens
  const colors = await extractColors(fileKey);

  // Generate CSS variables
  const cssVars = colorsToCSSVariables(colors);
  await fs.writeFile('tokens.css', cssVars);

  // Generate Tailwind config
  const tailwindConfig = colorsToTailwind(colors);
  await fs.writeFile('tailwind.config.js', tailwindConfig);

  // Get components
  const components = await getComponents(fileKey);

  // Generate React components
  for (const component of components.meta.components) {
    const reactCode = nodeToReact(component);
    await fs.writeFile(
      `components/${component.name}.tsx`,
      `export default function ${component.name}() {\n  return ${reactCode}\n}`
    );
  }

  console.log('Design-to-code complete!');
}
```

## Resources

- **Figma API Docs**: https://www.figma.com/developers/api
- **Plugin API**: https://www.figma.com/plugin-docs
- **Variables API**: https://www.figma.com/developers/api#variables
