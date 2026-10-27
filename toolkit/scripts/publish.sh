#!/usr/bin/env bash
# publish.sh — publish one lesson folder to the GitHub Pages lessons repo.
#
# Usage: bash publish.sh <lesson_dir> [repo_name]
#   <lesson_dir> must contain index.html and meta.json. Its folder name is the slug.
#   repo_name defaults to ste-learn. The repo is created (public) on first use.
#
# Prints the live page URL. Requires an authenticated `gh` CLI.
set -euo pipefail

LESSON_DIR="$(cd "$1" && pwd)"
REPO="${2:-ste-learn}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SLUG="$(basename "$LESSON_DIR")"

[[ -f "$LESSON_DIR/index.html" && -f "$LESSON_DIR/meta.json" ]] || { echo "ERROR: $LESSON_DIR needs index.html and meta.json" >&2; exit 2; }

# GitHub owner of the lessons repo (override with STE_OWNER).
OWNER="${STE_OWNER:-shrivardhan232006}"
WORK="${STE_WORKDIR:-$HOME/.ste-learn-repo}"

REMOTE="https://github.com/$OWNER/$REPO.git"
if [[ -d "$WORK/.git" ]]; then
  cd "$WORK"
  git fetch -q origin 2>/dev/null && git rev-parse -q --verify origin/main >/dev/null && git reset -q --hard origin/main || true
elif git ls-remote "$REMOTE" >/dev/null 2>&1; then
  git clone -q --depth 1 "$REMOTE" "$WORK"; cd "$WORK"
else
  echo "Repo $OWNER/$REPO not reachable. Trying to create it …"
  if ! gh repo create "$OWNER/$REPO" --public \
      --description "Study manuals in ASD-STE100 Simplified Technical English" >/dev/null 2>&1; then
    echo "ERROR: cannot see or create $OWNER/$REPO from this session." >&2
    echo "  If it exists: attach it to the session with push access (add_repo), then run again." >&2
    echo "  If not: create it at https://github.com/new?name=$REPO&visibility=public, then attach it." >&2
    exit 3
  fi
  mkdir -p "$WORK"; cd "$WORK"; git init -q -b main; git remote add origin "$REMOTE"
fi
git rev-parse -q --verify HEAD >/dev/null || git checkout -q -B main

git config user.name "$OWNER"
git config user.email "$OWNER@users.noreply.github.com"

mkdir -p assets "lessons/$SLUG"
cp "$SKILL_DIR/assets/manual.css" "$SKILL_DIR/assets/manual.js" assets/
cp -R "$LESSON_DIR/." "lessons/$SLUG/"
touch .nojekyll
python3 "$SKILL_DIR/scripts/build_index.py" "$WORK" "$OWNER" "$REPO"

git add -A
if git diff --cached --quiet; then
  echo "No changes to publish."
else
  git commit -q -m "Publish lesson: $SLUG" -m "${STE_COMMIT_TRAILER:-}"
  git push -q -u origin main
fi

# Turn on GitHub Pages (main branch, root) if it is not on yet. Already on for ste-learn.
if ! gh api "repos/$OWNER/$REPO/pages" >/dev/null 2>&1; then
  gh api -X POST "repos/$OWNER/$REPO/pages" -f "source[branch]=main" -f "source[path]=/" >/dev/null 2>&1 \
    && echo "GitHub Pages turned on." \
    || echo "NOTE: could not check Pages via API. If the site 404s, turn it on at https://github.com/$OWNER/$REPO/settings/pages (Deploy from a branch → main → /root)."
fi

LOWER_OWNER="$(echo "$OWNER" | tr '[:upper:]' '[:lower:]')"
echo "HOME_URL=https://$LOWER_OWNER.github.io/$REPO/"
echo "LESSON_URL=https://$LOWER_OWNER.github.io/$REPO/lessons/$SLUG/"
echo "REPO_URL=https://github.com/$OWNER/$REPO"
