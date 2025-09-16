# catalogo/migrations/0002_seed_initial_catalogo.py
from django.db import migrations
from django.core.management import call_command
from pathlib import Path

def load_fixtures(apps, schema_editor):
    app_dir = Path(__file__).resolve().parent.parent  # .../catalogo
    candidates = [
        # app_dir / "fixtures" / "initial_data.json",
        app_dir / "fixtures" / "paquetes_sample.json",
        # app_dir / "initial_data.json",
    ]
    for fixture in candidates:
        if fixture.exists():
            print(f"[seed] Cargando {fixture.name}")
            call_command("loaddata", str(fixture))
        else:
            print(f"[seed] No encontrado: {fixture}")

class Migration(migrations.Migration):
    dependencies = [
        ("catalogo", "0001_initial"),  # <-- AJUSTA si tu última es otra
    ]

    operations = [
        migrations.RunPython(load_fixtures, migrations.RunPython.noop),
    ]
