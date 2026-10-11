#!/usr/bin/env python3
"""Build the static data file behind the Claude Code 360° page.

Runs inside the Pages deploy workflow on a full-history checkout, so every
value comes from local git and the working tree — no GitHub API calls, which
keeps the page clear of the 60-requests-per-hour anonymous limit.

Usage: build-claude-code-360-snapshot.py <output.json>
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

GROUPS = {"01-personal": "Personal", "02-work": "Work"}
TOP_LEVEL = ["01-personal", "02-work", "03-plans", "04-reference", ".claude", ".config", ".cursor"]


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def first_line(markdown):
    for line in markdown.splitlines():
        stripped = line.strip().lstrip("#").strip()
        if stripped:
            return stripped
    return None


def frontmatter_description(markdown):
    block = re.match(r"^---\n(.*?)\n---", markdown, re.S)
    if not block:
        return None
    lines = block.group(1).splitlines()
    for i, line in enumerate(lines):
        if not line.startswith("description:"):
            continue
        value = line[len("description:"):].strip()
        if value in (">", "|", ">-", "|-", ""):
            continuation = []
            for follow in lines[i + 1:]:
                if follow[:1] in (" ", "\t"):
                    continuation.append(follow.strip())
                else:
                    break
            return " ".join(continuation) or None
        return value.strip('"').strip("'")
    return None


def agent_description(markdown):
    body = re.sub(r"^#.+\n+", "", markdown, count=1)
    return body.split("\n\n")[0].strip() or None


def load_tree():
    tree = []
    for line in git("ls-tree", "-r", "-l", "HEAD").splitlines():
        meta, path = line.split("\t", 1)
        mode, kind, _sha, size = meta.split()
        if kind != "blob":
            continue
        tree.append({"path": path, "type": "blob", "size": int(size)})
    return tree


def load_branches():
    branches = []
    refs = git("for-each-ref", "--format=%(refname)", "refs/remotes/origin").split()
    for ref in refs:
        name = ref[len("refs/remotes/origin/"):]
        if name == "HEAD":
            continue
        last = git("log", "-1", "--format=%cI", ref).strip()
        ahead = int(git("rev-list", "--count", f"refs/remotes/origin/main..{ref}"))
        behind = int(git("rev-list", "--count", f"{ref}..refs/remotes/origin/main"))
        branches.append({"name": name, "lastCommit": last, "aheadBy": ahead, "behindBy": behind})
    return sorted(branches, key=lambda b: (b["name"] != "main", b["name"]))


def load_project_meta(tree):
    projects = {}
    for group in GROUPS:
        names = {t["path"].split("/")[1] for t in tree if t["path"].startswith(group + "/")
                 and t["path"].count("/") >= 2}
        for name in names:
            path = f"{group}/{name}"
            last = git("log", "-1", "--format=%aI", "HEAD", "--", path).strip() or None
            note = first_line(read_text(os.path.join(path, "CLAUDE.md"))) \
                or first_line(read_text(os.path.join(path, "README.md")))
            projects[path] = {"lastCommit": last, "note": note}
    return projects


def load_skill_descriptions():
    skills, archived, agents = {}, [], {}
    skills_dir = ".claude/skills"
    if os.path.isdir(skills_dir):
        for name in sorted(d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))):
            md = read_text(os.path.join(skills_dir, name, "SKILL.md"))
            if md:
                skills[name] = frontmatter_description(md) or "No description frontmatter — see the file directly."
    archive_dir = ".claude/skills-archive"
    if os.path.isdir(archive_dir):
        archived = sorted(d for d in os.listdir(archive_dir) if os.path.isdir(os.path.join(archive_dir, d)))
    agents_dir = ".claude/agents"
    if os.path.isdir(agents_dir):
        for name in sorted(d for d in os.listdir(agents_dir) if os.path.isdir(os.path.join(agents_dir, d))):
            md = read_text(os.path.join(agents_dir, name, "AGENT.md"))
            if md:
                agents[name] = agent_description(md) or "No description in this agent's file."
    return skills, archived, agents


def main(out_path):
    tree = load_tree()
    skills, archived, agents = load_skill_descriptions()
    head = git("log", "-1", "--format=%h %s", "HEAD").strip()
    latest_sha, latest_subject, latest_date = git("log", "-1", "--format=%H%x1f%s%x1f%aI", "HEAD").strip().split("\x1f")
    snapshot = {
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generatedFrom": head,
        "latestCommit": {"sha": latest_sha, "commit": {"message": latest_subject, "author": {"date": latest_date}}},
        "tree": tree,
        "branches": load_branches(),
        "projectMeta": load_project_meta(tree),
        "skillDescriptions": skills,
        "archivedSkills": archived,
        "agentDescriptions": agents,
        "claudeMd": read_text("CLAUDE.md"),
        "claudeStatus": read_text("CLAUDE-STATUS.md"),
        "registry": read_text(".claude/COMMAND_REGISTRY.md"),
    }
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False)
    print(f"wrote {out_path}: {len(tree)} files, {len(snapshot['branches'])} branches, "
          f"{len(snapshot['projectMeta'])} projects, {len(skills)} skills, {len(agents)} agents")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: build-claude-code-360-snapshot.py <output.json>")
    main(sys.argv[1])
