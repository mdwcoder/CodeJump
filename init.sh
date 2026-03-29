#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_DIR="$PROJECT_ROOT/.venv"
REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"
COMMAND_NAME="filejump"
MARKER_BEGIN="# >>> filejump path >>>"
MARKER_END="# <<< filejump path <<<"

detect_python() {
  if command -v python3 >/dev/null 2>&1; then
    echo "python3"
    return
  fi
  if command -v python >/dev/null 2>&1; then
    echo "python"
    return
  fi
  echo "Python 3.11+ is required but was not found." >&2
  exit 1
}

validate_python() {
  local python_cmd="$1"
  "$python_cmd" - <<'PY'
import sys
if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11+ is required.")
PY
}

ensure_venv() {
  local python_cmd="$1"
  if [[ ! -x "$VENV_DIR/bin/python" ]]; then
    echo "Creating local virtual environment in $VENV_DIR"
    "$python_cmd" -m venv "$VENV_DIR"
  fi
}

install_dependencies() {
  local python_bin="$1"
  echo "Installing dependencies into $VENV_DIR"
  "$python_bin" -m pip install --disable-pip-version-check -r "$REQUIREMENTS_FILE"
}

pick_install_dir() {
  if [[ -d "/usr/local/bin" && -w "/usr/local/bin" ]]; then
    echo "/usr/local/bin"
    return
  fi
  mkdir -p "$HOME/.local/bin" 2>/dev/null || true
  if [[ -d "$HOME/.local/bin" && -w "$HOME/.local/bin" ]]; then
    echo "$HOME/.local/bin"
    return
  fi
  mkdir -p "$PROJECT_ROOT/.local/bin"
  echo "$PROJECT_ROOT/.local/bin"
}

append_path_to_shell_rc() {
  local install_dir="$1"
  case ":$PATH:" in
    *":$install_dir:"*) return ;;
  esac

  local rc_file
  case "$(basename "${SHELL:-}")" in
    zsh) rc_file="$HOME/.zshrc" ;;
    bash) rc_file="$HOME/.bashrc" ;;
    *) rc_file="$HOME/.profile" ;;
  esac

  touch "$rc_file"
  if grep -Fq "$MARKER_BEGIN" "$rc_file"; then
    return
  fi

  {
    echo
    echo "$MARKER_BEGIN"
    echo "export PATH=\"$install_dir:\$PATH\""
    echo "$MARKER_END"
  } >>"$rc_file"

  echo "Added $install_dir to PATH in $rc_file"
}

install_launcher() {
  local install_dir="$1"
  local launcher_path="$install_dir/$COMMAND_NAME"

  cat >"$launcher_path" <<EOF
#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$PROJECT_ROOT"
VENV_DIR="\$PROJECT_ROOT/.venv"

if [[ ! -x "\$VENV_DIR/bin/python" ]]; then
  exec "\$PROJECT_ROOT/init.sh" "\$@"
fi

exec "\$VENV_DIR/bin/python" -m codejump.main "\$@"
EOF

  chmod +x "$launcher_path"
  echo "Installed launcher: $launcher_path"
}

launch_app() {
  local launcher_path="$1"
  shift
  echo "Launching CodeJump"
  exec "$launcher_path" "$@"
}

main() {
  local python_cmd
  python_cmd="$(detect_python)"
  validate_python "$python_cmd"
  ensure_venv "$python_cmd"

  local venv_python="$VENV_DIR/bin/python"
  install_dependencies "$venv_python"

  local install_dir
  install_dir="$(pick_install_dir)"
  install_launcher "$install_dir"
  append_path_to_shell_rc "$install_dir"

  launch_app "$install_dir/$COMMAND_NAME" "$@"
}

main "$@"
