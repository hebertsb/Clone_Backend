# soporte/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import (
    SolicitudSoporte, 
    MensajeSoporte, 
    ConfiguracionSoporte,
    TipoSolicitud,
    EstadoSolicitud,
    PrioridadSolicitud
)
from reservas.models import Reserva


class UsuarioBasicoSerializer(serializers.ModelSerializer):
    """Serializer básico para mostrar información del usuario."""
    
    nombre_completo = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'nombre_completo', 'email']
        read_only_fields = ['id', 'username', 'email', 'nombre_completo']


class ReservaBasicaSerializer(serializers.ModelSerializer):
    """Serializer básico para mostrar información de la reserva."""
    
    fecha_formato = serializers.CharField(
        source='fecha_inicio.strftime', 
        read_only=True
    )
    
    class Meta:
        model = Reserva
        fields = [
            'id', 'fecha_inicio', 'fecha_formato', 'total', 'estado'
        ]
        read_only_fields = '__all__'


class MensajeSoporteSerializer(serializers.ModelSerializer):
    """Serializer para mensajes de soporte."""
    
    remitente = UsuarioBasicoSerializer(read_only=True)
    es_del_cliente = serializers.BooleanField(read_only=True)
    es_del_soporte = serializers.BooleanField(read_only=True)
    tiempo_desde_creacion = serializers.SerializerMethodField()
    
    class Meta:
        model = MensajeSoporte
        fields = [
            'id', 'mensaje', 'remitente', 'created_at', 'es_interno',
            'leido_por_cliente', 'leido_por_soporte', 
            'fecha_lectura_cliente', 'fecha_lectura_soporte',
            'archivo_adjunto', 'nombre_archivo_original',
            'es_del_cliente', 'es_del_soporte', 'tiempo_desde_creacion'
        ]
        read_only_fields = [
            'id', 'remitente', 'created_at', 'es_del_cliente', 'es_del_soporte',
            'fecha_lectura_cliente', 'fecha_lectura_soporte', 'tiempo_desde_creacion'
        ]
    
    def get_tiempo_desde_creacion(self, obj):
        """Calcula tiempo transcurrido desde la creación del mensaje."""
        if not obj.created_at:
            return None
        
        delta = timezone.now() - obj.created_at
        
        if delta.days > 0:
            return f"hace {delta.days} día{'s' if delta.days != 1 else ''}"
        elif delta.seconds >= 3600:
            horas = delta.seconds // 3600
            return f"hace {horas} hora{'s' if horas != 1 else ''}"
        elif delta.seconds >= 60:
            minutos = delta.seconds // 60
            return f"hace {minutos} minuto{'s' if minutos != 1 else ''}"
        else:
            return "hace unos segundos"
    
    def create(self, validated_data):
        """Crear mensaje asignando automáticamente el remitente."""
        validated_data['remitente'] = self.context['request'].user
        return super().create(validated_data)


class SolicitudSoporteListSerializer(serializers.ModelSerializer):
    """Serializer para listar solicitudes (vista resumida)."""
    
    cliente = UsuarioBasicoSerializer(read_only=True)
    agente_soporte = UsuarioBasicoSerializer(read_only=True)
    reserva = ReservaBasicaSerializer(read_only=True)
    
    tipo_solicitud_display = serializers.CharField(source='get_tipo_solicitud_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    
    tiempo_respuesta_sla = serializers.BooleanField(read_only=True)
    esta_vencido = serializers.BooleanField(read_only=True)
    tiempo_total_resolucion = serializers.FloatField(read_only=True)
    
    mensajes_no_leidos = serializers.SerializerMethodField()
    ultimo_mensaje = serializers.SerializerMethodField()
    
    class Meta:
        model = SolicitudSoporte
        fields = [
            'id', 'numero_ticket', 'cliente', 'agente_soporte', 'reserva',
            'tipo_solicitud', 'tipo_solicitud_display',
            'estado', 'estado_display',
            'prioridad', 'prioridad_display',
            'asunto', 'created_at', 'updated_at',
            'fecha_limite_respuesta', 'fecha_primera_respuesta', 
            'fecha_resolucion', 'fecha_cierre',
            'tiempo_respuesta_sla', 'esta_vencido', 'tiempo_total_resolucion',
            'mensajes_no_leidos', 'ultimo_mensaje', 'tags'
        ]
        read_only_fields = [
            'id', 'numero_ticket', 'created_at', 'updated_at',
            'fecha_limite_respuesta', 'fecha_primera_respuesta',
            'fecha_resolucion', 'fecha_cierre'
        ]
    
    def get_mensajes_no_leidos(self, obj):
        """Cuenta mensajes no leídos según el tipo de usuario."""
        request_user = self.context['request'].user
        
        if request_user == obj.cliente:
            # Cliente: contar mensajes del soporte no leídos
            return obj.mensajes.filter(
                leido_por_cliente=False,
                es_interno=False
            ).exclude(remitente=obj.cliente).count()
        else:
            # Soporte: contar mensajes del cliente no leídos
            return obj.mensajes.filter(
                leido_por_soporte=False,
                remitente=obj.cliente
            ).count()
    
    def get_ultimo_mensaje(self, obj):
        """Obtiene el último mensaje de la conversación."""
        ultimo = obj.mensajes.filter(es_interno=False).last()
        if ultimo:
            return {
                'mensaje': ultimo.mensaje[:100] + '...' if len(ultimo.mensaje) > 100 else ultimo.mensaje,
                'remitente': ultimo.remitente.get_full_name(),
                'fecha': ultimo.created_at,
                'es_del_cliente': ultimo.es_del_cliente
            }
        return None


class SolicitudSoporteDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para ver/editar una solicitud específica."""
    
    cliente = UsuarioBasicoSerializer(read_only=True)
    agente_soporte = UsuarioBasicoSerializer(read_only=True)
    reserva = ReservaBasicaSerializer(read_only=True)
    mensajes = MensajeSoporteSerializer(many=True, read_only=True)
    
    tipo_solicitud_display = serializers.CharField(source='get_tipo_solicitud_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    
    tiempo_respuesta_sla = serializers.BooleanField(read_only=True)
    esta_vencido = serializers.BooleanField(read_only=True)
    tiempo_total_resolucion = serializers.FloatField(read_only=True)
    
    estadisticas = serializers.SerializerMethodField()
    
    class Meta:
        model = SolicitudSoporte
        fields = [
            'id', 'numero_ticket', 'cliente', 'agente_soporte', 'reserva',
            'tipo_solicitud', 'tipo_solicitud_display',
            'estado', 'estado_display',
            'prioridad', 'prioridad_display',
            'asunto', 'descripcion', 'created_at', 'updated_at',
            'fecha_limite_respuesta', 'fecha_primera_respuesta', 
            'fecha_resolucion', 'fecha_cierre',
            'canal_origen', 'tags', 'satisfaccion_cliente', 'comentario_interno',
            'tiempo_respuesta_sla', 'esta_vencido', 'tiempo_total_resolucion',
            'mensajes', 'estadisticas'
        ]
        read_only_fields = [
            'id', 'numero_ticket', 'cliente', 'created_at', 'updated_at',
            'fecha_limite_respuesta', 'fecha_primera_respuesta',
            'fecha_resolucion', 'fecha_cierre'
        ]
    
    def get_estadisticas(self, obj):
        """Estadísticas de la solicitud."""
        total_mensajes = obj.mensajes.count()
        mensajes_cliente = obj.mensajes.filter(remitente=obj.cliente).count()
        mensajes_soporte = total_mensajes - mensajes_cliente
        
        return {
            'total_mensajes': total_mensajes,
            'mensajes_cliente': mensajes_cliente,
            'mensajes_soporte': mensajes_soporte,
            'tiempo_abierto_horas': obj.tiempo_total_resolucion or (
                (timezone.now() - obj.created_at).total_seconds() / 3600 
                if obj.created_at else 0
            ),
        }


class CrearSolicitudSoporteSerializer(serializers.ModelSerializer):
    """Serializer para crear una nueva solicitud de soporte."""
    
    reserva_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = SolicitudSoporte
        fields = [
            'tipo_solicitud', 'asunto', 'descripcion', 'prioridad', 
            'reserva_id', 'tags'
        ]
    
    def validate_reserva_id(self, value):
        """Validar que la reserva pertenezca al cliente."""
        if value:
            try:
                reserva = Reserva.objects.get(id=value)
                if reserva.usuario != self.context['request'].user:
                    raise serializers.ValidationError(
                        "No tiene permisos para referenciar esta reserva."
                    )
                return reserva
            except Reserva.DoesNotExist:
                raise serializers.ValidationError("La reserva especificada no existe.")
        return None
    
    def create(self, validated_data):
        """Crear solicitud asignando el cliente automáticamente."""
        reserva = validated_data.pop('reserva_id', None)
        validated_data['cliente'] = self.context['request'].user
        
        if reserva:
            validated_data['reserva'] = reserva
        
        return super().create(validated_data)


class GestionSolicitudSoporteSerializer(serializers.ModelSerializer):
    """Serializer para que soporte gestione solicitudes."""
    
    asignar_a_agente_id = serializers.IntegerField(required=False, write_only=True)
    
    class Meta:
        model = SolicitudSoporte
        fields = [
            'estado', 'prioridad', 'agente_soporte', 'asignar_a_agente_id',
            'tags', 'comentario_interno', 'satisfaccion_cliente'
        ]
    
    def validate_asignar_a_agente_id(self, value):
        """Validar que el agente existe y pertenece al grupo Soporte."""
        if value:
            try:
                from django.contrib.auth.models import Group
                agente = User.objects.get(id=value)
                
                if not agente.groups.filter(name='Soporte').exists():
                    raise serializers.ValidationError(
                        "El usuario especificado no pertenece al equipo de soporte."
                    )
                return agente
            except User.DoesNotExist:
                raise serializers.ValidationError("El agente especificado no existe.")
        return None
    
    def update(self, instance, validated_data):
        """Actualizar solicitud con lógica especial para asignación."""
        agente = validated_data.pop('asignar_a_agente_id', None)
        
        if agente:
            instance.asignar_agente(agente)
        
        return super().update(instance, validated_data)


class DashboardSoporteSerializer(serializers.Serializer):
    """Serializer para el dashboard del equipo de soporte."""
    
    solicitudes_pendientes = serializers.IntegerField()
    solicitudes_en_proceso = serializers.IntegerField()
    solicitudes_vencidas = serializers.IntegerField()
    solicitudes_resueltas_hoy = serializers.IntegerField()
    
    tiempo_promedio_respuesta = serializers.FloatField()
    tiempo_promedio_resolucion = serializers.FloatField()
    satisfaccion_promedio = serializers.FloatField()
    
    solicitudes_por_tipo = serializers.DictField()
    solicitudes_por_prioridad = serializers.DictField()
    carga_por_agente = serializers.ListField()
    
    tendencia_semanal = serializers.ListField()


class EstadisticasClienteSerializer(serializers.Serializer):
    """Serializer para estadísticas del cliente."""
    
    total_solicitudes = serializers.IntegerField()
    solicitudes_abiertas = serializers.IntegerField()
    solicitudes_resueltas = serializers.IntegerField()
    
    tiempo_promedio_resolucion = serializers.FloatField()
    satisfaccion_promedio = serializers.FloatField()
    
    ultima_actividad = serializers.DateTimeField()
    
    solicitudes_recientes = SolicitudSoporteListSerializer(many=True)


class ConfiguracionSoporteSerializer(serializers.ModelSerializer):
    """Serializer para configuración del sistema de soporte."""
    
    class Meta:
        model = ConfiguracionSoporte
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']