import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','backend.settings')
import django
django.setup()
from django.apps import apps
names=[f'{m._meta.app_label}.{m.__name__}' for m in apps.get_models()]
open('scripts/auto_imports.txt','w',encoding='utf-8').write('\n'.join(names))
print('Wrote scripts/auto_imports.txt')
