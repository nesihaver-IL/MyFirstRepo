#!/bin/bash
# habits-dashboard: deterministic fact-gathering
#
# Emits one JSON object on stdout with everything a script can answer
# reliably: git state, filesystem sizes, skill/agent inventory, per-project
# stats, and a set of hygiene checks. Claude turns this into the dashboard's
# prose and structure — this script's only job is to make sure the facts
# underneath that prose are always regenerated fresh, never hand-copied
# forward from a previous run.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$REPO_ROOT"

esc() { python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$1"; }

# ---------- repo / branch state ----------
BRANCH=$(git branch --show-current)
HEAD_SHA=$(git rev-parse --short HEAD)
HEAD_DATE=$(git log -1 --format=%cI)
COMMIT_COUNT=$(git rev-list --count HEAD)
CLEAN=$( [ -z "$(git status --porcelain)" ] && echo true || echo false )
LAST_SUBJ=$(git log -1 --format=%s)

git fetch origin main --quiet 2>/dev/null || true
AHEAD=0; BEHIND=0
if git rev-parse --verify origin/main >/dev/null 2>&1; then
  read -r BEHIND AHEAD <<< "$(git rev-list --left-right --count origin/main...HEAD)"
fi

# ---------- top-level sizes ----------
SIZES_JSON="{"
first=true
for d in 01-personal 02-work 03-plans 04-reference .claude .config .cursor; do
  [ -d "$d" ] || continue
  sz=$(du -sh "$d" 2>/dev/null | cut -f1)
  $first || SIZES_JSON+=","
  SIZES_JSON+="$(esc "$d"):$(esc "$sz")"
  first=false
done
SIZES_JSON+="}"

# ---------- skills / agents inventory ----------
skills_active=$(ls .claude/skills 2>/dev/null | grep -v '^README' || true)
skills_archived=$(ls .claude/skills-archive 2>/dev/null || true)
agents=$(ls .claude/agents 2>/dev/null || true)

jarr() { python3 -c 'import json,sys; print(json.dumps([l for l in sys.stdin.read().splitlines() if l]))'; }
SKILLS_ACTIVE_JSON=$(echo "$skills_active" | jarr)
SKILLS_ARCHIVED_JSON=$(echo "$skills_archived" | jarr)
AGENTS_JSON=$(echo "$agents" | jarr)
SKILL_COUNT=$(echo "$skills_active" | grep -c . || true)

# ---------- per-project stats (auto-discovered, not hardcoded) ----------
PROJECTS_JSON="["
first=true
for group_dir in 01-personal 02-work; do
  [ -d "$group_dir" ] || continue
  for p in "$group_dir"/*/; do
    [ -d "$p" ] || continue
    p="${p%/}"
    name=$(basename "$p")
    last=$(git log -1 --format=%cs -- "$p" 2>/dev/null || echo "")
    files=$(find "$p" -type f 2>/dev/null | wc -l | tr -d ' ')
    size=$(du -sh "$p" 2>/dev/null | cut -f1)
    documented=false
    if grep -qi "$name" CLAUDE.md 2>/dev/null; then documented=true; fi
    $first || PROJECTS_JSON+=","
    PROJECTS_JSON+="{\"path\":$(esc "$p"),\"name\":$(esc "$name"),\"group\":$(esc "$group_dir"),\"lastCommit\":$(esc "$last"),\"files\":$files,\"size\":$(esc "$size"),\"documented\":$documented}"
    first=false
  done
done
PROJECTS_JSON+="]"

# ---------- hygiene checks (generic, not tied to any specific past incident) ----------
tracked_venvs=$(git ls-files | grep -E '(^|/)\.venv[^/]*/(bin|lib|pyvenv.cfg)' | sed -E 's#(/[^/]+){1,2}$##' | sort -u || true)
tracked_worktrees=$(git ls-files -- '.claude/worktrees/*' | sed -E 's#(/.claude/worktrees/[^/]+)/.*#\1#' | sort -u || true)
backslash_paths=$(git ls-files | grep '\\\\' || true)

stale_docs="["
first=true
for f in TODO.md DECISIONS.md CLAUDE-STATUS.md CLAUDE.md .claude/COMMAND_REGISTRY.md; do
  [ -f "$f" ] || continue
  d=$(git log -1 --format=%cs -- "$f" 2>/dev/null || echo "")
  [ -n "$d" ] || continue
  days=$(( ( $(date -u +%s) - $(date -u -d "$d" +%s) ) / 86400 ))
  $first || stale_docs+=","
  stale_docs+="{\"file\":$(esc "$f"),\"lastTouched\":$(esc "$d"),\"daysStale\":$days}"
  first=false
done
stale_docs+="]"

# any archived skill name still referenced in COMMAND_REGISTRY.md
registry_drift="[]"
if [ -f .claude/COMMAND_REGISTRY.md ] && [ -n "$skills_archived" ]; then
  hits=$(echo "$skills_archived" | while read -r s; do [ -n "$s" ] && grep -ql -- "$s" .claude/COMMAND_REGISTRY.md 2>/dev/null && echo "$s"; done || true)
  registry_drift=$(echo "$hits" | jarr)
fi

# claimed skill count in CLAUDE.md vs actual
claimed=$(grep -oE '[0-9]+ (active )?(registered )?skills' CLAUDE.md 2>/dev/null | head -1 | grep -oE '^[0-9]+' || echo "")
claimed_json="null"; [ -n "$claimed" ] && claimed_json="$claimed"

echo "{"
echo "  \"generatedAt\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
echo "  \"repo\": {"
echo "    \"branch\": $(esc "$BRANCH"),"
echo "    \"headSha\": $(esc "$HEAD_SHA"),"
echo "    \"headDate\": $(esc "$HEAD_DATE"),"
echo "    \"commitCount\": $COMMIT_COUNT,"
echo "    \"clean\": $CLEAN,"
echo "    \"lastCommitSubject\": $(esc "$LAST_SUBJ"),"
echo "    \"aheadOfMain\": $AHEAD,"
echo "    \"behindMain\": $BEHIND"
echo "  },"
echo "  \"sizes\": $SIZES_JSON,"
echo "  \"skillsActive\": $SKILLS_ACTIVE_JSON,"
echo "  \"skillsArchived\": $SKILLS_ARCHIVED_JSON,"
echo "  \"agents\": $AGENTS_JSON,"
echo "  \"skillCount\": $SKILL_COUNT,"
echo "  \"projects\": $PROJECTS_JSON,"
echo "  \"hygiene\": {"
echo "    \"trackedVenvs\": $(echo "$tracked_venvs" | jarr),"
echo "    \"trackedWorktreeDirs\": $(echo "$tracked_worktrees" | jarr),"
echo "    \"backslashPaths\": $(echo "$backslash_paths" | jarr),"
echo "    \"staleDocs\": $stale_docs,"
echo "    \"registryListsArchived\": $registry_drift,"
echo "    \"claimedSkillCountInClaudeMd\": $claimed_json"
echo "  }"
echo "}"
