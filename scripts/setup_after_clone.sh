#!/usr/bin/env bash
# Shell helper to setup the project after cloning (Linux / macOS / Git Bash)
# Usage: from repository root
#   bash scripts/setup_after_clone.sh --venv --install --migrate --loaddata

set -euo pipefail
CREATE_VENV=0
INSTALL_DEPS=0
RUN_MIGRATIONS=0
LOAD_DATA=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --venv) CREATE_VENV=1; shift ;;
    --install) INSTALL_DEPS=1; shift ;;
    --migrate) RUN_MIGRATIONS=1; shift ;;
    --loaddata) LOAD_DATA=1; shift ;;
    --yes) YES=1; shift ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

if [[ $CREATE_VENV -eq 1 ]]; then
  python -m venv .venv
fi

if [[ $INSTALL_DEPS -eq 1 ]]; then
  .venv/bin/pip install --upgrade pip
  .venv/bin/pip install -r requirements.txt
fi

if [[ $RUN_MIGRATIONS -eq 1 ]]; then
  .venv/bin/python manage.py migrate --noinput
fi

if [[ $LOAD_DATA -eq 1 ]]; then
  export PYTHONPATH='.'
  .venv/bin/python scripts/load_catalog_initial.py || true
  .venv/bin/python scripts/load_paquetes.py || true
  .venv/bin/python scripts/load_descuentos.py || true
  .venv/bin/python scripts/load_reservas.py || true
fi

echo "setup_after_clone.sh finished."
