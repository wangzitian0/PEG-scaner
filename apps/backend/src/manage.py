#!/usr/bin/env python3
from __future__ import annotations

from flask.cli import FlaskGroup

from pegserver import create_app

cli = FlaskGroup(create_app=create_app)

if __name__ == '__main__':
    cli()
