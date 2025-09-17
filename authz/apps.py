from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.contrib.auth.hashers import make_password, identify_hasher
from django.conf import settings
from django.db import connection
import re


class AuthzConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authz'

    def ready(self):
        from .models import Usuario
        def hash_plain_passwords(sender, **kwargs):
            for usuario in Usuario.objects.all():
                pwd = usuario.password
                # Si la contraseña parece estar en texto plano (no tiene formato hash)
                try:
                    identify_hasher(pwd)
                except Exception:
                    # Si no es hash, la hasheamos
                    usuario.password = make_password(pwd)
                    usuario.save()
        post_migrate.connect(hash_plain_passwords, sender=self)
