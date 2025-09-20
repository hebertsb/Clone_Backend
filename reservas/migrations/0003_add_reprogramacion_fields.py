# Generated manually to fix missing reprogramacion fields
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0002_configuracionglobalreprogramacion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reserva',
            name='fecha_original',
            field=models.DateTimeField(blank=True, null=True, help_text="Fecha original antes de la reprogramación"),
        ),
        migrations.AddField(
            model_name='reserva',
            name='fecha_reprogramacion',
            field=models.DateTimeField(blank=True, null=True, help_text="Fecha cuando se hizo la reprogramación"),
        ),
        migrations.AddField(
            model_name='reserva',
            name='motivo_reprogramacion',
            field=models.TextField(blank=True, null=True, help_text="Motivo de la reprogramación"),
        ),
        migrations.AddField(
            model_name='reserva',
            name='numero_reprogramaciones',
            field=models.PositiveSmallIntegerField(default=0, help_text="Número de veces que se ha reprogramado"),
        ),
        migrations.AddField(
            model_name='reserva',
            name='reprogramado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, 
                                  related_name="reservas_reprogramadas", to=settings.AUTH_USER_MODEL,
                                  help_text="Usuario que hizo la reprogramación"),
        ),
        # Agregar los índices que faltan
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS reservas_reserva_usuario_idx ON reservas_reserva(usuario_id);",
            reverse_sql="DROP INDEX IF EXISTS reservas_reserva_usuario_idx;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS reservas_reserva_estado_idx ON reservas_reserva(estado);",
            reverse_sql="DROP INDEX IF EXISTS reservas_reserva_estado_idx;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS reservas_reserva_fecha_inicio_idx ON reservas_reserva(fecha_inicio);",
            reverse_sql="DROP INDEX IF EXISTS reservas_reserva_fecha_inicio_idx;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS reservas_reserva_fecha_reprogramacion_idx ON reservas_reserva(fecha_reprogramacion);",
            reverse_sql="DROP INDEX IF EXISTS reservas_reserva_fecha_reprogramacion_idx;"
        ),
    ]