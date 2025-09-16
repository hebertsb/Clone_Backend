from django.db import migrations
from django.core.management import call_command
from pathlib import Path

def load_seed_data(apps, schema_editor):
    base_dir = Path(__file__).resolve().parent.parent  # va a /authz
    fixtures = [
        base_dir / "fixtures" / "datos_cupones.json",
        # base_dir / "fixtures" / "datos_usuarios.json",
    ]

    for fixture in fixtures:
        if fixture.exists():
            print(f"✔️ Cargando fixture: {fixture.name}")
            call_command("loaddata", str(fixture))
        else:
            print(f"⚠️ Fixture no encontrado: {fixture}")

class Migration(migrations.Migration):

    dependencies = [
        ("cupones", "0001_initial"),  # asegúrate de que esta sea la anterior correcta
    ]

    operations = [
        migrations.RunPython(load_seed_data),
    ]
