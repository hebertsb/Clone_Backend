#!/usr/bin/env bash
# Simple script to run only Django migrations (no venv creation)
# Usage from repo root:
#   bash scripts/migrate_all.sh

if [ -x ".venv/bin/python" ]; then
  PY=.venv/bin/python
else
  PY=python
fi

$PY manage.py migrate --noinput

echo "migrate_all.sh finished."
