from reservas.models import Reserva
from reservas.serializers import ReservaConHistorialSerializer
from typing import Any, Dict

print('=== PROBANDO SERIALIZER DIRECTAMENTE ===')
try:
    reserva = Reserva.objects.get(id=1005)
    # Acceso seguro a atributos del modelo
    reserva_id = getattr(reserva, 'id', 'N/A')
    reserva_estado = getattr(reserva, 'estado', 'N/A')
    print(f'Reserva encontrada: {reserva_id} - {reserva_estado}')
    
    # Verificar que los campos existen
    print(f'numero_reprogramaciones: {getattr(reserva, "numero_reprogramaciones", "N/A")}')
    print(f'fecha_original: {getattr(reserva, "fecha_original", "N/A")}')
    print(f'fecha_reprogramacion: {getattr(reserva, "fecha_reprogramacion", "N/A")}')
    
    # Probar el serializer
    print('\nProbando serialization...')
    serializer = ReservaConHistorialSerializer(reserva)
    data = serializer.data
    print('✅ Serialización exitosa')
    
    # Acceso seguro a los datos serializados
    if isinstance(data, dict):
        puede_reprogramar = data.get("puede_reprogramar", "N/A")
    else:
        # Si data es una lista u otro tipo, manejarlo apropiadamente
        puede_reprogramar = "N/A (tipo de datos inesperado)"
    
    print(f'puede_reprogramar: {puede_reprogramar}')
    
except Exception as e:
    print(f'❌ ERROR: {e}')
    import traceback
    traceback.print_exc()