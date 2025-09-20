# soporte/signals.py

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import SolicitudSoporte, MensajeSoporte, EstadoSolicitud, TipoSolicitud
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=SolicitudSoporte)
def procesar_nueva_solicitud(sender, instance, created, **kwargs):
    """
    Procesa una nueva solicitud de soporte:
    1. Asigna automáticamente un agente si está configurado
    2. Envía notificación al cliente
    3. Determina prioridad automática para reprogramaciones
    """
    
    if created:
        # Auto-asignar agente si está configurado
        from .models import ConfiguracionSoporte
        config = ConfiguracionSoporte.obtener_configuracion()
        
        if config.asignacion_automatica:
            agente_disponible = obtener_agente_disponible()
            if agente_disponible:
                instance.asignar_agente(agente_disponible)
                logger.info(f"Solicitud {instance.numero_ticket} auto-asignada a {agente_disponible.get_full_name()}")  # type: ignore
        
        # Prioridad automática para reprogramaciones urgentes
        if instance.tipo_solicitud == TipoSolicitud.REPROGRAMACION and instance.reserva:
            from datetime import timedelta
            from django.utils import timezone
            
            # Si la reserva es en menos de 24 horas, prioridad alta
            if instance.reserva.fecha_inicio <= timezone.now() + timedelta(hours=24):
                instance.prioridad = 'ALTA'
                instance.save(update_fields=['prioridad'])
        
        # Enviar notificación al cliente
        enviar_notificacion_nueva_solicitud(instance)
        
        logger.info(f"Nueva solicitud creada: {instance.numero_ticket} - Tipo: {instance.tipo_solicitud}")


@receiver(post_save, sender=MensajeSoporte)
def procesar_nuevo_mensaje(sender, instance, created, **kwargs):
    """
    Procesa un nuevo mensaje:
    1. Actualiza estado de la solicitud si es necesario
    2. Marca mensajes como leídos automáticamente según el remitente
    """
    
    if created:
        # Si el mensaje es del cliente y la solicitud estaba esperando respuesta, cambiar estado
        if (instance.es_del_cliente and 
            instance.solicitud.estado == EstadoSolicitud.ESPERANDO_CLIENTE):
            instance.solicitud.estado = EstadoSolicitud.EN_PROCESO
            instance.solicitud.save(update_fields=['estado'])
        
        # Marcar como leído por el remitente automáticamente
        if instance.es_del_cliente:
            instance.leido_por_cliente = True
            instance.fecha_lectura_cliente = instance.created_at
        else:
            instance.leido_por_soporte = True
            instance.fecha_lectura_soporte = instance.created_at
        
        instance.save(update_fields=[
            'leido_por_cliente', 'leido_por_soporte',
            'fecha_lectura_cliente', 'fecha_lectura_soporte'
        ])
        
        logger.info(f"Nuevo mensaje en {instance.solicitud.numero_ticket} de {instance.remitente.get_full_name()}")


def obtener_agente_disponible():
    """
    Busca un agente de soporte disponible con menos carga de trabajo.
    """
    try:
        # Buscar usuarios en el grupo 'Soporte'
        grupo_soporte = Group.objects.get(name='Soporte')
        agentes = grupo_soporte.user_set.filter(is_active=True)
        
        if not agentes.exists():
            logger.warning("No hay agentes de soporte disponibles")
            return None
        
        from .models import ConfiguracionSoporte
        config = ConfiguracionSoporte.obtener_configuracion()
        
        # Encontrar agente con menos solicitudes activas
        agente_menos_cargado = None
        min_solicitudes = float('inf')
        
        for agente in agentes:
            solicitudes_activas = agente.solicitudes_asignadas.filter(  # type: ignore
                estado__in=[EstadoSolicitud.PENDIENTE, EstadoSolicitud.EN_PROCESO, EstadoSolicitud.ESPERANDO_CLIENTE]
            ).count()
            
            if solicitudes_activas < min_solicitudes and solicitudes_activas < config.max_solicitudes_por_agente:
                min_solicitudes = solicitudes_activas
                agente_menos_cargado = agente
        
        return agente_menos_cargado
        
    except Group.DoesNotExist:
        logger.error("Grupo 'Soporte' no existe. Crear grupo en Django Admin.")
        return None
    except Exception as e:
        logger.error(f"Error obteniendo agente disponible: {e}")
        return None


def enviar_notificacion_nueva_solicitud(solicitud):
    """
    Envía notificación por email al cliente sobre la nueva solicitud.
    """
    from .models import ConfiguracionSoporte
    
    config = ConfiguracionSoporte.obtener_configuracion()
    
    if not config.enviar_emails_cliente:
        return
    
    try:
        # Contexto para el template
        context = {
            'solicitud': solicitud,
            'cliente': solicitud.cliente,
            'numero_ticket': solicitud.numero_ticket,
            'fecha_limite': solicitud.fecha_limite_respuesta,
        }
        
        # Generar contenido del email
        asunto = f"Solicitud de Soporte Creada - Ticket #{solicitud.numero_ticket}"
        
        # Email en texto plano
        mensaje_texto = f"""
Estimado/a {solicitud.cliente.get_full_name()},

Hemos recibido su solicitud de soporte exitosamente.

Detalles de la solicitud:
• Ticket: #{solicitud.numero_ticket}
• Tipo: {solicitud.get_tipo_solicitud_display()}
• Asunto: {solicitud.asunto}
• Estado: {solicitud.get_estado_display()}
• Prioridad: {solicitud.get_prioridad_display()}

{f"• Reserva relacionada: {solicitud.reserva}" if solicitud.reserva else ""}

Nuestro equipo revisará su solicitud y le responderemos lo antes posible.
Tiempo estimado de primera respuesta: {solicitud.fecha_limite_respuesta.strftime('%d/%m/%Y a las %H:%M') if solicitud.fecha_limite_respuesta else 'No especificado'}

Puede hacer seguimiento de su solicitud ingresando a su panel de cliente en nuestro sistema.

Saludos cordiales,
Equipo de Soporte - Sistema UAGRM
"""
        
        # Enviar email
        send_mail(
            subject=asunto,
            message=mensaje_texto,
            from_email=f"Soporte UAGRM <{settings.DEFAULT_FROM_EMAIL}>",
            recipient_list=[solicitud.cliente.email],
            fail_silently=False,
        )
        
        logger.info(f"Notificación enviada a {solicitud.cliente.email} para ticket {solicitud.numero_ticket}")
        
    except Exception as e:
        logger.error(f"Error enviando notificación de nueva solicitud: {e}")


def enviar_notificacion_mensaje_cliente(mensaje):
    """
    Envía notificación al cliente cuando soporte responde.
    """
    if mensaje.es_del_soporte and not mensaje.es_interno:
        try:
            asunto = f"Nueva respuesta en su solicitud #{mensaje.solicitud.numero_ticket}"
            
            mensaje_texto = f"""
Estimado/a {mensaje.solicitud.cliente.get_full_name()},

Hemos respondido a su solicitud de soporte.

Ticket: #{mensaje.solicitud.numero_ticket}
Asunto: {mensaje.solicitud.asunto}

Para ver la respuesta completa y continuar la conversación, ingrese a su panel de cliente.

Saludos cordiales,
Equipo de Soporte - Sistema UAGRM
"""
            
            send_mail(
                subject=asunto,
                message=mensaje_texto,
                from_email=f"Soporte UAGRM <{settings.DEFAULT_FROM_EMAIL}>",
                recipient_list=[mensaje.solicitud.cliente.email],
                fail_silently=False,
            )
            
            logger.info(f"Notificación de respuesta enviada a {mensaje.solicitud.cliente.email}")
            
        except Exception as e:
            logger.error(f"Error enviando notificación de mensaje: {e}")