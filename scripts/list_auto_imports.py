import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()
from django.apps import apps
import importlib

names = []
# List all model classes
for model in apps.get_models():
    names.append(f"{model._meta.app_label}.{model.__name__}")

# Common helpers that shell_plus often imports if available
extras = {}
try:
    extras['settings'] = importlib.import_module('django.conf').settings
except Exception:
    pass
try:
    extras['models'] = importlib.import_module('django.db').models
except Exception:
    pass
try:
    extras['apps'] = apps
except Exception:
    pass

print('Auto-import candidates count (models):', len(names))
for n in sorted(names):
    print('  ', n)

print('\nExtra objects available:')
for k in sorted(extras.keys()):
    print('  ', k)
