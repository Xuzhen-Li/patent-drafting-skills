#!/usr/bin/env bash
# Install patent-drafting-skills into Cursor, Claude Code, or Codex skill folders.
# Idempotent. Default mode is a symlink. Respects $HOME (used by dry-run tests).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${ROOT}/skills"

usage() {
  cat <<'EOF'
Usage: install.sh --target cursor|claude|codex|all [--mode copy|link] [--dry-run] [-h]

Install every skills/<name> directory that contains a SKILL.md.

Targets (under $HOME):
  cursor   .cursor/skills
  claude   .claude/skills
  codex    .codex/skills
  all      all three

--mode link    symlink each skill directory (default)
--mode copy    copy skill files into the destination
--dry-run      print actions only; do not write
-h, --help     show this help

Link mode refuses to replace an existing real directory.
Copy mode replaces only that skill folder's contents (or a previous symlink).
A second run of the same command leaves a correct install unchanged.
EOF
}

TARGET=""
MODE="link"
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --target)
      if [[ $# -lt 2 ]]; then
        echo "install.sh: --target needs a value" >&2
        exit 1
      fi
      TARGET="$2"
      shift 2
      ;;
    --target=*)
      TARGET="${1#*=}"
      shift
      ;;
    --mode)
      if [[ $# -lt 2 ]]; then
        echo "install.sh: --mode needs a value" >&2
        exit 1
      fi
      MODE="$2"
      shift 2
      ;;
    --mode=*)
      MODE="${1#*=}"
      shift
      ;;
    *)
      echo "install.sh: unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "${TARGET}" ]]; then
  echo "install.sh: --target is required" >&2
  usage >&2
  exit 1
fi

case "${MODE}" in
  copy|link) ;;
  *)
    echo "install.sh: --mode must be copy or link" >&2
    exit 1
    ;;
esac

case "${TARGET}" in
  cursor|claude|codex|all) ;;
  *)
    echo "install.sh: --target must be cursor, claude, codex, or all" >&2
    exit 1
    ;;
esac

if [[ ! -d "${SKILLS_DIR}" ]]; then
  echo "install.sh: skills directory not found: ${SKILLS_DIR}" >&2
  exit 1
fi

skill_names=()
for dir in "${SKILLS_DIR}"/*; do
  [[ -d "${dir}" ]] || continue
  [[ -f "${dir}/SKILL.md" ]] || continue
  skill_names+=("$(basename "${dir}")")
done

if [[ ${#skill_names[@]} -eq 0 ]]; then
  echo "install.sh: no skills found in ${SKILLS_DIR}" >&2
  exit 1
fi

target_root() {
  case "$1" in
    cursor) printf '%s/.cursor/skills' "${HOME}" ;;
    claude) printf '%s/.claude/skills' "${HOME}" ;;
    codex) printf '%s/.codex/skills' "${HOME}" ;;
  esac
}

targets=()
if [[ "${TARGET}" == "all" ]]; then
  targets=(cursor claude codex)
else
  targets=("${TARGET}")
fi

log() {
  printf '%s\n' "$*"
}

install_one() {
  local name="$1"
  local src="$2"
  local dest_root="$3"
  local dest="${dest_root}/${name}"

  if [[ "${MODE}" == "link" ]]; then
    if [[ -L "${dest}" ]]; then
      local current
      current="$(readlink "${dest}")"
      if [[ "${current}" == "${src}" ]]; then
        log "unchanged  ${dest} -> ${src}"
        return
      fi
      if [[ "${DRY_RUN}" -eq 1 ]]; then
        log "ln -sfn ${src} ${dest}"
        return
      fi
      ln -sfn "${src}" "${dest}"
      log "relinked   ${dest} -> ${src}"
      return
    fi
    if [[ -e "${dest}" ]]; then
      echo "install.sh: ${dest} exists and is not a symlink; remove it or use --mode copy" >&2
      exit 1
    fi
    if [[ "${DRY_RUN}" -eq 1 ]]; then
      log "ln -sfn ${src} ${dest}"
      return
    fi
    ln -sfn "${src}" "${dest}"
    log "linked     ${dest} -> ${src}"
    return
  fi

  # copy: replace a previous symlink or the contents of a previous copy
  if [[ -L "${dest}" ]]; then
    if [[ "${DRY_RUN}" -eq 1 ]]; then
      log "rm ${dest}"
      log "mkdir -p ${dest}"
      log "cp -R ${src}/. ${dest}/"
      return
    fi
    rm "${dest}"
  elif [[ -e "${dest}" && ! -d "${dest}" ]]; then
    echo "install.sh: ${dest} exists and is not a directory" >&2
    exit 1
  fi

  if [[ "${DRY_RUN}" -eq 1 ]]; then
    log "mkdir -p ${dest}"
    log "cp -R ${src}/. ${dest}/"
    return
  fi

  mkdir -p "${dest}"
  local child
  for child in "${dest}"/* "${dest}"/.[!.]*; do
    if [[ -e "${child}" ]]; then
      rm -rf "${child}"
    fi
  done
  cp -R "${src}/." "${dest}/"
  log "copied     ${src} -> ${dest}"
}

log "patent-drafting-skills install"
log "  source:  ${SKILLS_DIR}"
log "  target:  ${TARGET}"
log "  mode:    ${MODE}"
log "  home:    ${HOME}"
if [[ "${DRY_RUN}" -eq 1 ]]; then
  log "  dry-run: yes"
fi

for t in "${targets[@]}"; do
  dest_root="$(target_root "${t}")"
  log ""
  log "[${t}] ${dest_root}"
  if [[ "${DRY_RUN}" -eq 1 ]]; then
    log "mkdir -p ${dest_root}"
  else
    mkdir -p "${dest_root}"
  fi
  for name in "${skill_names[@]}"; do
    install_one "${name}" "${SKILLS_DIR}/${name}" "${dest_root}"
  done
done

log ""
log "done (${#skill_names[@]} skills, ${#targets[@]} target(s))"
