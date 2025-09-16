import time
import sys

start = time.perf_counter()
print('Start')

t0 = time.perf_counter()
import os
print('import os:', time.perf_counter()-t0)

# time importing django
t1 = time.perf_counter()
try:
    import django
    print('import django:', time.perf_counter()-t1)
except Exception as e:
    print('import django failed:', e)
    sys.exit(1)

# set settings and setup
t2 = time.perf_counter()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
print('set DJANGO_SETTINGS_MODULE:', time.perf_counter()-t2)

t3 = time.perf_counter()
django.setup()
print('django.setup():', time.perf_counter()-t3)

# apps registry
t4 = time.perf_counter()
from django.apps import apps
print('import apps:', time.perf_counter()-t4)

# get_models
t5 = time.perf_counter()
models = list(apps.get_models())
print('apps.get_models():', time.perf_counter()-t5)
print('models count:', len(models))

# optional DB introspection
try:
    t6 = time.perf_counter()
    from django.db import connection
    tables = connection.introspection.table_names()
    print('DB introspection:', time.perf_counter()-t6, 'tables:', len(tables))
except Exception as e:
    print('DB introspection failed:', e)

print('Total elapsed:', time.perf_counter()-start)
