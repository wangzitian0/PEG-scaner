#!/usr/bin/env python3
import argparse
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = ROOT / 'tools'
TOOLS_BIN = TOOLS_DIR / 'bin'
PID_DIR = ROOT / 'x-log'

NEO4J_CONTAINER = os.getenv('NEO4J_CONTAINER', 'pegscanner_neo4j_dev')
NEO4J_HTTP_PORT = os.getenv('NEO4J_HTTP_PORT', '7474')
NEO4J_BOLT_PORT = os.getenv('NEO4J_BOLT_PORT', '7687')
NEO4J_AUTH = os.getenv('NEO4J_AUTH', 'neo4j/neo4j')
NEO4J_IMAGE = os.getenv('NEO4J_DOCKER_IMAGE', 'neo4j:5')
SKIP_NEO4J_CONTAINER = os.getenv('SKIP_NEO4J_CONTAINER', '0') == '1'

BACKEND_PID = PID_DIR / 'env_backend.pid'
FRONTEND_PID = PID_DIR / 'env_frontend.pid'

WATCHED_PROCS = []
SHUTTING_DOWN = False
NEO4J_STARTED = False


def run(cmd, **kwargs):
    kwargs.setdefault('check', True)
    kwargs.setdefault('cwd', ROOT)
    print(f"[env] running: {' '.join(cmd)}")
    return subprocess.run(cmd, **kwargs)


def spawn(label, cmd, pid_file=None):
    print(f"[env] starting {label}: {' '.join(cmd)}")
    proc = subprocess.Popen(cmd, cwd=ROOT)
    WATCHED_PROCS.append((label, proc, pid_file))
    if pid_file:
        PID_DIR.mkdir(parents=True, exist_ok=True)
        pid_file.write_text(str(proc.pid))


def ensure_docker():
    try:
        subprocess.run(['docker', '--version'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RuntimeError('Docker CLI not available; required for Neo4j container')


def start_neo4j():
    global NEO4J_STARTED
    if SKIP_NEO4J_CONTAINER or NEO4J_STARTED:
        return
    ensure_docker()
    subprocess.run(['docker', 'rm', '-f', NEO4J_CONTAINER], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    run([
        'docker', 'run', '-d',
        '--name', NEO4J_CONTAINER,
        '-p', f'{NEO4J_HTTP_PORT}:7474',
        '-p', f'{NEO4J_BOLT_PORT}:7687',
        '-e', f'NEO4J_AUTH={NEO4J_AUTH}',
        '-e', 'NEO4J_PLUGINS=[]',
        NEO4J_IMAGE,
    ])
    NEO4J_STARTED = True
    print(f'[env] Neo4j running (http:{NEO4J_HTTP_PORT} bolt:{NEO4J_BOLT_PORT})')


def stop_neo4j():
    global NEO4J_STARTED
    if SKIP_NEO4J_CONTAINER or not NEO4J_STARTED:
        return
    try:
        subprocess.run(['docker', 'rm', '-f', NEO4J_CONTAINER], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f'[env] Neo4j container {NEO4J_CONTAINER} stopped')
    except FileNotFoundError:
        pass
    NEO4J_STARTED = False


def lint_structure():
    run(['bash', str(TOOLS_DIR / 'lint_structure.sh')])


def clear_vite_cache():
    run(['node', str(TOOLS_DIR / 'clear_vite_cache.js')])


def prepare_dev_machine():
    print('[env] preparing development machine (tooling + dependencies)...')
    for binary, hint in [('node', 'install Node.js 20+'),
                         ('npm', 'install Node.js 20+'),
                         ('python3', 'install Python 3.10+')]:
        if not shutil.which(binary):
            raise RuntimeError(f"Required binary '{binary}' not found ({hint})")
    global SKIP_NEO4J_CONTAINER
    TOOLS_BIN.mkdir(parents=True, exist_ok=True)
    os.environ['PATH'] = f"{TOOLS_BIN}:{os.environ.get('PATH','')}"
    if not SKIP_NEO4J_CONTAINER and not shutil.which('docker'):
        podman_path = shutil.which('podman')
        if podman_path:
            wrapper = TOOLS_BIN / 'docker'
            wrapper.write_text("#!/usr/bin/env bash\nexec podman \"$@\"\n")
            wrapper.chmod(0o755)
            print("[env] docker missing, using podman wrapper at tools/bin/docker")
        else:
            raise RuntimeError("Docker CLI is required for the built-in Neo4j container. "
                               "Install Docker Desktop or Podman (alias to 'docker'), "
                               "or set SKIP_NEO4J_CONTAINER=1 and point to an external Neo4j.")
    bootstrap_dev()


def bootstrap_dev():
    print('[env] bootstrapping development environment...')
    run(['npm', 'install'])
    run(['python3', '-m', 'venv', 'apps/backend/.venv'])
    run(['./apps/backend/.venv/bin/python3', '-m', 'pip', 'install', '-r', 'apps/backend/requirements.txt'])
    run(['npx', 'nx', 'run', 'backend:generate-proto'])
    print('[env] dev bootstrap complete.')


def bootstrap_prod():
    print('[env] bootstrapping production environment...')
    run(['npm', 'ci'])
    run(['python3', '-m', 'venv', 'apps/backend/.venv'])
    run(['./apps/backend/.venv/bin/python3', '-m', 'pip', 'install', '-r', 'apps/backend/requirements.txt'])
    run(['npx', 'nx', 'run', 'backend:generate-proto'])
    print('[env] prod bootstrap complete.')


def stop_current_processes():
    global SHUTTING_DOWN
    if SHUTTING_DOWN:
        return
    SHUTTING_DOWN = True
    for label, proc, pid_file in WATCHED_PROCS:
        if proc.poll() is None:
            print(f'[env] stopping {label} (pid {proc.pid})')
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
        if pid_file and pid_file.exists():
            pid_file.unlink(missing_ok=True)
    stop_neo4j()


def handle_signal(signum, frame):
    print(f'[env] received signal {signum}, shutting down...')
    stop_current_processes()
    sys.exit(0)


def stop_pidfile_processes(graceful_delay=5):
    for label, pid_file in (('backend', BACKEND_PID), ('frontend', FRONTEND_PID)):
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text().strip())
            except ValueError:
                pid = None
            if pid:
                print(f'[env] stopping existing {label} process {pid}')
                try:
                    os.kill(pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            time.sleep(graceful_delay)
            pid_file.unlink(missing_ok=True)
    stop_neo4j()


def start_dev():
    prepare_dev_machine()
    lint_structure()
    clear_vite_cache()
    start_neo4j()
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    spawn('backend', ['npx', 'nx', 'run', 'backend:start'])
    time.sleep(2)
    spawn('metro', ['npx', 'nx', 'run', 'mobile:start'])
    time.sleep(2)
    spawn('vite', ['npx', 'nx', 'run', 'mobile:serve'])

    print('[env] dev environment running. Press Ctrl+C to stop.')
    _monitor_processes()


def start_prod():
    lint_structure()
    start_neo4j()
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    backend_cmd = [
        'bash', '-lc',
        'PYTHONPATH=apps/backend/src:apps/backend/proto/generated:. ./apps/backend/.venv/bin/python3 apps/backend/src/manage.py run --host 0.0.0.0 --port 8000'
    ]
    frontend_cmd = ['npx', 'nx', 'run', 'mobile:serve', '--', '--mode', 'production', '--host', '0.0.0.0']

    spawn('backend', backend_cmd, BACKEND_PID)
    time.sleep(2)
    spawn('frontend', frontend_cmd, FRONTEND_PID)

    print('[env] production services running. Press Ctrl+C to stop.')
    _monitor_processes()


def restart_prod():
    print('[env] restarting production stack...')
    stop_pidfile_processes(graceful_delay=5)
    WATCHED_PROCS.clear()
    global SHUTTING_DOWN
    SHUTTING_DOWN = False
    start_prod()


def _monitor_processes():
    while True:
        alive = [proc.poll() for _, proc, _ in WATCHED_PROCS]
        if any(code is not None for code in alive):
            print('[env] one of the processes exited; shutting down.')
            stop_current_processes()
            break
        time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description='Env management tools')
    sub = parser.add_subparsers(dest='command')
    sub.add_parser('dev', help='Start dev stack (Neo4j + backend + Metro + Vite)')
    sub.add_parser('start', help='Start production stack (Neo4j + backend + production web)')
    sub.add_parser('restart', help='Gracefully restart production stack')
    sub.add_parser('bootstrap-dev', help='Install dependencies for development')
    sub.add_parser('bootstrap-prod', help='Install dependencies for production')
    args = parser.parse_args()

    if args.command == 'dev':
        start_dev()
    elif args.command == 'start':
        start_prod()
    elif args.command == 'restart':
        restart_prod()
    elif args.command == 'bootstrap-dev':
        bootstrap_dev()
    elif args.command == 'bootstrap-prod':
        bootstrap_prod()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
