#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_DIR="$ROOT_DIR/x-log"
mkdir -p "$PID_DIR"

ENV_FILE="${ENV:-}"
if [[ -n "${ENV_FILE}" && -f "${ENV_FILE}" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
  set +a
fi

BACKEND_CMD=${BACKEND_CMD:-"npx nx run backend:start"}
MOBILE_CMD=${MOBILE_CMD:-"cd apps/mobile && npx react-native start --port ${MOBILE_DEV_PORT:-8081}"}
SESSION_FILE="$PID_DIR/.dev_session"

resolve_session_tag() {
  local mode="$1"
  local previous=""
  if [[ -f "$SESSION_FILE" ]]; then
    previous="$(cat "$SESSION_FILE")"
  fi

  if [[ "$mode" == "start" ]]; then
    local tag="${DEV_SESSION_NAME:-pegscanner_dev_$(date +%s)}"
    echo "$tag" >"$SESSION_FILE"
    echo "$tag"
  else
    if [[ -n "${DEV_SESSION_NAME:-}" ]]; then
      echo "$DEV_SESSION_NAME"
    elif [[ -n "$previous" ]]; then
      echo "$previous"
    else
      echo "pegscanner_dev"
    fi
  fi
}

start_service() {
  local name="$1"
  local cmd="$2"
  local session="$3"
  local backend_host="${BACKEND_HOST:-127.0.0.1}"
  local backend_port="${BACKEND_PORT:-8000}"
  local mobile_port="${MOBILE_DEV_PORT:-8081}"

  local pid_file="$PID_DIR/${session}_${name}.pid"
  local log_file="$PID_DIR/${session}_${name}.log"

  if [[ -f "$pid_file" ]] && kill -0 "$(cat "$pid_file")" >/dev/null 2>&1; then
    echo "Service [$session:$name] already running (pid $(cat "$pid_file")), skipping"
    return
  fi

  nohup bash -c "cd \"$ROOT_DIR\" && eval \"$cmd\"" >"$log_file" 2>&1 &
  echo $! >"$pid_file"
  if [[ "$name" == "backend" ]]; then
    echo "Started [$session:$name] pid $(cat "$pid_file") → http://${backend_host}:${backend_port}/ (logs: $log_file)"
  elif [[ "$name" == "mobile" ]]; then
    echo "Started [$session:$name] pid $(cat "$pid_file") → Metro dev server on port ${mobile_port} (logs: $log_file)"
  else
    echo "Started [$session:$name] pid $(cat "$pid_file"). Logs: $log_file"
  fi
}

stop_service() {
  local name="$1"
  local session="$2"
  local pid_file="$PID_DIR/${session}_${name}.pid"
  if [[ -f "$pid_file" ]]; then
    local pid
    pid=$(cat "$pid_file")
    if kill -0 "$pid" >/dev/null 2>&1; then
      kill "$pid" >/dev/null 2>&1 || true
      echo "Stopped [$session:$name] pid $pid"
    fi
    rm -f "$pid_file"
  fi
}

case "${1:-}" in
  start)
    SESSION_TAG="$(resolve_session_tag start)"
    shift
    SERVICES=("$@")
    if [[ ${#SERVICES[@]} -eq 0 ]]; then
      SERVICES=("backend" "mobile")
    fi
    for svc in "${SERVICES[@]}"; do
      case "$svc" in
        backend) start_service "backend" "$BACKEND_CMD" "$SESSION_TAG" ;;
        mobile) start_service "mobile" "$MOBILE_CMD" "$SESSION_TAG" ;;
        *) echo "Unknown service '$svc'"; exit 1 ;;
      esac
    done
    ;;
  stop)
    SESSION_TAG="$(resolve_session_tag stop)"
    shift
    SERVICES=("$@")
    if [[ ${#SERVICES[@]} -eq 0 ]]; then
      SERVICES=("backend" "mobile")
    fi
    for svc in "${SERVICES[@]}"; do
      case "$svc" in
        backend) stop_service "backend" "$SESSION_TAG" ;;
        mobile) stop_service "mobile" "$SESSION_TAG" ;;
        *) echo "Unknown service '$svc'"; exit 1 ;;
      esac
    done
    ;;
  *)
    echo "Usage: tools/dev.sh [start|stop] [backend|mobile ...]"
    exit 1
    ;;
esac
