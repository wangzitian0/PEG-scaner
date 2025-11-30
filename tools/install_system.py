#!/usr/bin/env python3
"""
System dependency installer/checker.

Detects required binaries (node, npm, python3, docker) and prints install commands.
Use --apply to execute the suggested package-manager commands automatically (when supported).
"""

import argparse
import os
import platform
import shutil
import subprocess
from pathlib import Path

REQUIRED = ['node', 'npm', 'python3', 'docker']

RECIPES = {
    'macos': {
        'manager': 'brew',
        'commands': {
            'node': ['brew', 'install', 'node@20'],
            'npm': ['brew', 'install', 'node@20'],
            'python3': ['brew', 'install', 'python@3.12'],
            'docker': ['brew', 'install', '--cask', 'docker'],
        },
        'notes': 'Install Homebrew from https://brew.sh if missing. Docker Desktop (brew install --cask docker) or Podman (brew install podman) both work; launch Docker Desktop once after install or alias podman to docker.',
    },
    'ubuntu': {
        'manager': 'apt',
        'commands': {
            'node': ['sudo', 'apt-get', 'install', '-y', 'nodejs', 'npm'],
            'npm': ['sudo', 'apt-get', 'install', '-y', 'nodejs', 'npm'],
            'python3': ['sudo', 'apt-get', 'install', '-y', 'python3', 'python3-pip'],
            'docker': ['sudo', 'apt-get', 'install', '-y', 'docker.io'],
        },
        'notes': 'Consider using NodeSource (https://github.com/nodesource/distributions) for the latest Node.js 20.x on Ubuntu/Debian.',
    },
    'debian': 'ubuntu',
    'pop': 'ubuntu',
    'linuxmint': 'ubuntu',
    'fedora': {
        'manager': 'dnf',
        'commands': {
            'node': ['sudo', 'dnf', 'install', '-y', 'nodejs', 'npm'],
            'npm': ['sudo', 'dnf', 'install', '-y', 'nodejs', 'npm'],
            'python3': ['sudo', 'dnf', 'install', '-y', 'python3', 'python3-pip'],
            'docker': ['sudo', 'dnf', 'install', '-y', 'docker'],
        },
        'notes': 'After installing docker, run `sudo systemctl enable --now docker`.',
    },
    'centos': {
        'manager': 'yum',
        'commands': {
            'node': ['sudo', 'yum', 'install', '-y', 'nodejs', 'npm'],
            'npm': ['sudo', 'yum', 'install', '-y', 'nodejs', 'npm'],
            'python3': ['sudo', 'yum', 'install', '-y', 'python3', 'python3-pip'],
            'docker': ['sudo', 'yum', 'install', '-y', 'docker'],
        },
        'notes': 'Start docker with `sudo systemctl enable --now docker`.',
    },
    'rhel': 'centos',
    'amazon': 'centos',
    'windows': {
        'manager': 'choco',
        'commands': {
            'node': ['choco', 'install', 'nodejs-lts', '-y'],
            'npm': ['choco', 'install', 'nodejs-lts', '-y'],
            'python3': ['choco', 'install', 'python', '-y'],
            'docker': ['choco', 'install', 'docker-desktop', '-y'],
        },
        'notes': 'Install Chocolatey from https://chocolatey.org/install if missing. After docker-desktop install, restart the machine.',
    },
}


def detect_linux_id():
    os_release = Path('/etc/os-release')
    if not os_release.exists():
        return None
    data = {}
    for line in os_release.read_text().splitlines():
        if '=' in line:
            key, value = line.split('=', 1)
            data[key.strip()] = value.strip().strip('"')
    return data.get('ID') or data.get('ID_LIKE')


def detect_os():
    system = platform.system().lower()
    if system == 'darwin':
        return 'macos'
    if system == 'windows':
        return 'windows'
    if system == 'linux':
        return detect_linux_id() or 'linux'
    return system


def resolve_recipe(os_name):
    recipe = RECIPES.get(os_name)
    if isinstance(recipe, str):
        return RECIPES.get(recipe)
    return recipe


def missing_binaries():
    return [binary for binary in REQUIRED if shutil.which(binary) is None]


def run_commands(cmds):
    for cmd in cmds:
        print(f"[system-install] running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(description='Check/install system-wide dependencies (node/npm/python/docker).')
    parser.add_argument('--apply', action='store_true', help='Execute the recommended install commands (when supported). Requires appropriate privileges.')
    args = parser.parse_args()

    os_name = detect_os()
    recipe = resolve_recipe(os_name)

    missing = missing_binaries()
    if not missing:
        print('[system-install] All required binaries are already available.')
        return

    print(f'[system-install] Missing: {", ".join(missing)}')
    if not recipe:
        print('[system-install] No automated recipe for this OS. Please install the missing tools manually.')
        return

    print(f"[system-install] Detected OS: {os_name}. Package manager hint: {recipe.get('manager')}")
    if recipe.get('notes'):
        print(f"[system-install] Notes: {recipe['notes']}")

    commands = []
    for binary in missing:
        cmd = recipe['commands'].get(binary)
        if cmd:
            commands.append(cmd)
        else:
            print(f"[system-install] No command defined for {binary}; install manually.")

    if not commands:
        return

    if args.apply:
        run_commands(commands)
    else:
        print('[system-install] Suggested commands (run manually or re-run with --apply):')
        for cmd in commands:
            print('  ' + ' '.join(cmd))


if __name__ == '__main__':
    main()
