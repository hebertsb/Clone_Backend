#!/usr/bin/env python
"""
Script para verificar el estado de las tablas en la base de datos de reservas.
"""
from django.db import connection
from typing import List, Tuple, Any

def execute_query(query: str) -> List[Tuple[Any, ...]]:
    """Ejecuta una consulta SQL y retorna los resultados de forma segura."""
    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()

def check_table_exists(table_name: str) -> bool:
    """Verifica si una tabla específica existe en la base de datos."""
    result = execute_query(
        "SELECT EXISTS (SELECT FROM information_schema.tables "
        "WHERE table_schema='public' AND table_name=%s)"
    )
    return result[0][0] if result else False

print("=== TABLAS DE HISTORIAL ===")
historial_tables = execute_query(
    "SELECT table_name FROM information_schema.tables "
    "WHERE table_schema='public' AND table_name LIKE '%historial%'"
)
if historial_tables:
    for table in historial_tables:
        print(f"  - {table[0]}")
else:
    print("  ❌ No hay tablas de historial")

print("\n=== TODAS LAS TABLAS DE RESERVAS ===")
reservas_tables = execute_query(
    "SELECT table_name FROM information_schema.tables "
    "WHERE table_schema='public' AND table_name LIKE '%reservas%'"
)
for table in reservas_tables:
    print(f"  - {table[0]}")

print("\n=== VERIFICANDO TABLA ESPECÍFICA ===")
existe = check_table_exists('reservas_historialreprogramacion')
print(f"reservas_historialreprogramacion existe: {existe}")

# Verificar el estado de las migraciones
print("\n=== ESTADO DE MIGRACIONES ===")
migraciones = execute_query(
    "SELECT name FROM django_migrations WHERE app='reservas' ORDER BY name"
)
for mig in migraciones:
    print(f"  ✅ {mig[0]}")