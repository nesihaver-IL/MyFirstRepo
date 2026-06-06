---
name: github-trending
description: Fetch and display GitHub trending repositories and developers. Use when building dashboards, discovering popular projects, or tracking trending repos. Triggers on GitHub trending, popular repos, trending developers.
---

# GitHub Trending Data

Fetch trending repositories and developers from GitHub.

## Important Note

**GitHub does NOT provide an official trending API.** This skill uses web scraping or GitHub Search API as alternatives.

## Method 1: Web Scraping (Recommended)

```typescript
import * as cheerio from 'cheerio';

interface TrendingRepo {
  owner: string;
  name: string;
  url: string;
  description: string;
  language: string;
  stars: number;
  forks: number;
  todayStars: number;
}

async function getTrendingRepos(
  language = '',
  since = 'daily' // 'daily', 'weekly', 'monthly'
): Promise<TrendingRepo[]> {
  const url = language
    ? `https://github.com/trending/${language}?since=${since}`
    : `https://github.com/trending?since=${since}`;

  const response = await fetch(url, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (compatible; TrendingBot/1.0)'
    }
  });

  const html = await response.text();
  const $ = cheerio.load(html);
  const repos: TrendingRepo[] = [];

  $('article.Box-row').each((_, element) => {
    const $el = $(element);
    const $title = $el.find('h2 a');
    const fullName = $title.attr('href')?.slice(1) || '';
    const [owner, name] = fullName.split('/');

    const description = $el.find('p').text().trim();
    const language = $el.find('[itemprop="programmingLanguage"]').text().trim();

    const starsText = $el.find('a[href*="stargazers"]').text().trim();
    const stars = parseNumber(starsText);

    const forksText = $el.find('a[href*="forks"]').text().trim();
    const forks = parseNumber(forksText);

    const todayStarsText = $el.find('span.float-sm-right').text().trim();
    const todayStars = parseNumber(todayStarsText);

    repos.push({
      owner,
      name,
      url: `https://github.com${$title.attr('href')}`,
      description,
      language,
      stars,
      forks,
      todayStars,
    });
  });

  return repos;
}

function parseNumber(text: string): number {
  const cleaned = text.replace(/,/g, '');
  const match = cleaned.match(/[\d.]+/);
  if (!match) return 0;

  const num = parseFloat(match[0]);
  if (text.includes('k')) return Math.round(num * 1000);
  if (text.includes('m')) return Math.round(num * 1000000);
  return Math.round(num);
}
```

## Method 2: GitHub Search API

```typescript
interface GitHubRepo {
  name: string;
  owner: { login: string };
  html_url: string;
  description: string;
  language: string;
  stargazers_count: number;
  forks_count: number;
  created_at: string;
}

async function getTrendingViaSearch(
  language = '',
  token?: string
): Promise<GitHubRepo[]> {
  const date = new Date();
  date.setDate(date.getDate() - 7); // Last week
  const since = date.toISOString().split('T')[0];

  const query = [
    `created:>${since}`,
    'stars:>100',
    language ? `language:${language}` : '',
  ].filter(Boolean).join(' ');

  const headers: HeadersInit = {
    'Accept': 'application/vnd.github.v3+json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(
    `https://api.github.com/search/repositories?q=${encodeURIComponent(query)}&sort=stars&order=desc`,
    { headers }
  );

  const data = await response.json();
  return data.items;
}
```

## Next.js API Route

```typescript
// app/api/trending/route.ts
import { NextResponse } from 'next/server';
import * as cheerio from 'cheerio';

export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const language = searchParams.get('language') || '';
  const since = searchParams.get('since') || 'daily';

  try {
    const repos = await getTrendingRepos(language, since);

    return NextResponse.json(
      { success: true, data: repos },
      {
        headers: {
          'Cache-Control': 'public, s-maxage=3600, stale-while-revalidate=1800',
        },
      }
    );
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Failed to fetch trending repos' },
      { status: 500 }
    );
  }
}
```

## React Component

```tsx
'use client';

import { useState, useEffect } from 'react';

interface Repo {
  owner: string;
  name: string;
  url: string;
  description: string;
  language: string;
  stars: number;
  todayStars: number;
}

export function TrendingRepos() {
  const [repos, setRepos] = useState<Repo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/trending')
      .then(res => res.json())
      .then(data => {
        setRepos(data.data);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="space-y-4">
      {repos.map(repo => (
        <div key={repo.url} className="border rounded-lg p-4">
          <a
            href={repo.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline font-semibold"
          >
            {repo.owner}/{repo.name}
          </a>

          <p className="text-gray-600 mt-2">{repo.description}</p>

          <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
            {repo.language && (
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 rounded-full bg-blue-500" />
                {repo.language}
              </span>
            )}

            <span>⭐ {repo.stars.toLocaleString()}</span>

            <span className="text-green-600">
              +{repo.todayStars.toLocaleString()} today
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
```

## Caching Strategy

```typescript
// Cache for 1 hour
const CACHE_TTL = 3600000; // 1 hour in ms
const cache = new Map<string, { data: any; timestamp: number }>();

async function getCachedTrending(language: string, since: string) {
  const key = `${language}-${since}`;
  const cached = cache.get(key);

  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }

  const data = await getTrendingRepos(language, since);
  cache.set(key, { data, timestamp: Date.now() });

  return data;
}
```

## Important Warnings

1. **GitHub may change their HTML** - Monitor for breakages
2. **Rate limiting** - Use aggressive caching (1 hour minimum)
3. **User-Agent required** - Always include User-Agent header
4. **CORS** - Implement server-side to avoid CORS issues

## Rate Limits

**Scraping**: No official limits, but be respectful
**GitHub API**:
- Unauthenticated: 10 requests/minute
- Authenticated: 30 requests/minute

## Resources

- **GitHub Search API**: https://docs.github.com/en/rest/search
- **Alternative Service**: https://github-trending-api.now.sh
