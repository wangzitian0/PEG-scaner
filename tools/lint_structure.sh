#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

allowed_dirs=(
  ".git"
  ".github"
  ".nx"
  ".pytest_cache"
  "apps"
  "docs"
  "libs"
  "node_modules"
  "nx"
  "tools"
  "x-data"
  "x-log"
)

allowed_files=(
  ".dockerignore"
  ".gitignore"
  ".prettierignore"
  ".prettierrc"
  "AGENTS.md"
  "PRD.md"
  "README.md"
  "docker-compose.yml"
  "nx"
  "nx.bat"
  "nx.json"
  "package-lock.json"
  "package.json"
  "tsconfig.base.json"
)

contains() {
  local needle=$1; shift
  for item in "$@"; do
    if [[ "$item" == "$needle" ]]; then
      return 0
    fi
  done
  return 1
}

violations=()
for entry in "$ROOT_DIR"/.* "$ROOT_DIR"/*; do
  name="$(basename "$entry")"
  [[ "$name" == "." || "$name" == ".." ]] && continue

  if [[ -d "$entry" ]]; then
    if ! contains "$name" "${allowed_dirs[@]}"; then
      violations+=("Unexpected directory at root: $name")
    fi
  else
    if ! contains "$name" "${allowed_files[@]}"; then
      violations+=("Unexpected file at root: $name")
    fi
  fi
done

required_readme_dirs=("apps" "docs" "libs" "tools")
optional_readme_dirs=("x-data" "x-log")  # Optional in CI (excluded from Docker)

for dir in "${required_readme_dirs[@]}"; do
  if [[ ! -f "$ROOT_DIR/$dir/README.md" ]]; then
    violations+=("Missing README.md in $dir/")
  fi
done

for dir in "${optional_readme_dirs[@]}"; do
  if [[ -d "$ROOT_DIR/$dir" && ! -f "$ROOT_DIR/$dir/README.md" ]]; then
    violations+=("Missing README.md in $dir/")
  fi
done

if ((${#violations[@]})); then
  printf 'Structure lint failed:\n'
  printf ' - %s\n' "${violations[@]}"
  exit 1
fi

echo "Structure lint passed."
