#!/usr/bin/env bash
set -euo pipefail

# Full two-way sync helper
# - Fetches origin
# - Merges origin/<branch> into local <branch>, preferring local on conflicts
# - Pushes local branch to origin
# Usage: scripts/full-sync.sh [branch]

cd "$(git rev-parse --show-toplevel)"

branch="${1:-$(git rev-parse --abbrev-ref HEAD)}"
echo "Full-sync starting for branch: $branch"

git remote get-url origin >/dev/null 2>&1 || { echo "Remote 'origin' not found" >&2; exit 1; }

# Stash uncommitted changes if present
STASHED=0
if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
  echo "Working tree has uncommitted changes — stashing..."
  git stash push -u -m "full-sync auto-stash $(date --iso-8601=seconds)" >/dev/null
  STASHED=1
fi

echo "Fetching origin..."
git fetch origin --prune

# Ensure branch exists locally and check it out
if ! git show-ref --verify --quiet "refs/heads/$branch"; then
  echo "Local branch '$branch' not found; creating from origin/$branch if available..."
  if git ls-remote --exit-code --heads origin "$branch" >/dev/null 2>&1; then
    git checkout -B "$branch" "origin/$branch"
  else
    git checkout -B "$branch"
  fi
else
  git checkout "$branch"
fi

echo "Merging origin/$branch into local $branch (local wins on conflicts)..."
# Use recursive strategy option 'ours' so local side wins during conflicts
if ! git merge --no-edit -X ours "origin/$branch"; then
  echo "Merge failed — aborting merge and restoring stash if any" >&2
  git merge --abort || true
  if [ "$STASHED" -eq 1 ]; then
    git stash pop || true
  fi
  exit 2
fi

echo "Pushing local $branch to origin..."
git push origin "$branch"

if [ "$STASHED" -eq 1 ]; then
  echo "Restoring stashed changes..."
  if ! git stash pop; then
    echo "Warning: 'git stash pop' failed. Stash entry kept — resolve manually." >&2
  fi
fi

echo "Full sync complete for branch: $branch"
