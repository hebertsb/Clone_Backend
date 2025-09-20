# Generated manually to fix missing HistorialReprogramacion table

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0003_add_reprogramacion_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistorialReprogramacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('fecha_anterior', models.DateTimeField(help_text='Fecha anterior de la reserva')),
                ('fecha_nueva', models.DateTimeField(help_text='Nueva fecha de la reserva')),
                ('motivo', models.TextField(blank=True, help_text='Motivo de la reprogramación', null=True)),
                ('notificacion_enviada', models.BooleanField(default=False, help_text='Si se envió notificación por email')),
                ('reprogramado_por', models.ForeignKey(blank=True, help_text='Usuario que realizó la reprogramación', null=True, on_delete=django.db.models.deletion.SET_NULL, to='authz.usuario')),
                ('reserva', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historial_reprogramaciones', to='reservas.reserva')),
            ],
            options={
                'verbose_name': 'Historial de Reprogramación',
                'verbose_name_plural': 'Historiales de Reprogramación',
                'ordering': ['-created_at'],
            },
        ),
    ]