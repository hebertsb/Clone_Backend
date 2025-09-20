from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class NotificacionReprogramacion:
    """Maneja las notificaciones por email para reprogramaciones"""
    
    @staticmethod
    def notificar_cliente(reserva, fecha_anterior, motivo=None):
        """Envía notificación al cliente sobre la reprogramación"""
        try:
            usuario = reserva.usuario
            
            # Contexto para el template
            contexto = {
                'usuario': usuario,
                'reserva': reserva,
                'fecha_anterior': fecha_anterior,
                'fecha_nueva': reserva.fecha_inicio,
                'motivo': motivo,
                'servicios': reserva.detalles.all(),
            }
            
            # Crear el email
            asunto = f"Tu reserva #{reserva.pk} ha sido reprogramada"
            
            # Template en HTML (si existe)
            try:
                mensaje_html = render_to_string('emails/reprogramacion_cliente.html', contexto)
                mensaje_texto = strip_tags(mensaje_html)
            except:
                # Fallback a mensaje simple si no hay template
                mensaje_texto = f"""
Hola {usuario.nombres} {usuario.apellidos},

Tu reserva #{reserva.pk} ha sido reprogramada exitosamente.

Detalles de la reprogramación:
- Fecha anterior: {fecha_anterior.strftime('%d/%m/%Y %H:%M')}
- Nueva fecha: {reserva.fecha_inicio.strftime('%d/%m/%Y %H:%M')}
- Estado: {reserva.estado}
- Total: {reserva.total} {reserva.moneda}

{f'Motivo: {motivo}' if motivo else ''}

Si tienes alguna pregunta, no dudes en contactarnos.

Saludos,
Equipo de Turismo
                """
                mensaje_html = None
            
            # Enviar email
            if mensaje_html:
                email = EmailMultiAlternatives(
                    subject=asunto,
                    body=mensaje_texto,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[usuario.email]
                )
                email.attach_alternative(mensaje_html, "text/html")
                email.send()
            else:
                send_mail(
                    subject=asunto,
                    message=mensaje_texto,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[usuario.email],
                    fail_silently=False
                )
            
            logger.info(f"Notificación de reprogramación enviada al cliente {usuario.email} para reserva {reserva.pk}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando notificación al cliente para reserva {reserva.pk}: {str(e)}")
            return False
    
    @staticmethod
    def notificar_administrador(reserva, fecha_anterior, reprogramado_por, motivo=None):
        """Crea notificación en el panel de soporte para el equipo (NO envía email)
        
        Este método ha sido actualizado para NO enviar emails a administradores.
        En su lugar, crea una SolicitudSoporte que aparecerá en el panel de soporte
        para que el equipo pueda revisar y gestionar la reprogramación.
        """
        try:
            # Importar aquí para evitar circular imports
            from soporte.models import SolicitudSoporte, TipoSolicitud, PrioridadSolicitud
            
            # Crear solicitud de soporte en lugar de enviar email
            asunto = f"Reprogramación de reserva #{reserva.pk}"
            
            descripcion = f"""Nueva reprogramación registrada:

Reserva ID: #{reserva.pk}
Cliente: {reserva.usuario.nombres} {reserva.usuario.apellidos}
Email: {reserva.usuario.email}
Teléfono: {reserva.usuario.telefono or 'No proporcionado'}

Detalles de la reprogramación:
- Fecha anterior: {fecha_anterior.strftime('%d/%m/%Y %H:%M')}
- Nueva fecha: {reserva.fecha_inicio.strftime('%d/%m/%Y %H:%M')}
- Reprogramado por: {reprogramado_por.nombres} {reprogramado_por.apellidos}
- Número de reprogramaciones: {reserva.numero_reprogramaciones}
- Total: {reserva.total} {reserva.moneda}

{f'Motivo: {motivo}' if motivo else 'Sin motivo especificado'}

Servicios incluidos:
{chr(10).join([f"- {detalle.servicio.titulo} (x{detalle.cantidad})" for detalle in reserva.detalles.all()])}

Por favor, revisa y confirma la disponibilidad de recursos para la nueva fecha.
            """
            
            # Determinar prioridad según número de reprogramaciones
            if reserva.numero_reprogramaciones >= 3:
                prioridad = PrioridadSolicitud.ALTA
            elif reserva.numero_reprogramaciones >= 2:
                prioridad = PrioridadSolicitud.MEDIA
            else:
                prioridad = PrioridadSolicitud.BAJA
            
            # Crear notificación en el panel de soporte
            solicitud = SolicitudSoporte.objects.create(
                cliente=reserva.usuario,
                tipo_solicitud=TipoSolicitud.REPROGRAMACION,
                prioridad=prioridad,
                asunto=asunto,
                descripcion=descripcion,
                reserva=reserva,
                canal_origen='SISTEMA_AUTOMATICO',
                tags='reprogramacion,automatica'
            )
            
            logger.info(f"Notificación de reprogramación creada en panel soporte #{solicitud.numero_ticket} para reserva {reserva.pk}")
            return True
            
        except Exception as e:
            logger.error(f"Error creando notificación de soporte para reserva {reserva.pk}: {str(e)}")
            return False
    
    @staticmethod
    def enviar_recordatorio_reprogramacion(reserva, dias_antes=1):
        """Envía recordatorio de la nueva fecha programada"""
        try:
            fecha_recordatorio = reserva.fecha_inicio - timezone.timedelta(days=dias_antes)
            
            if timezone.now().date() == fecha_recordatorio.date():
                usuario = reserva.usuario
                
                asunto = f"Recordatorio: Tu reserva #{reserva.pk} es mañana"
                mensaje = f"""
Hola {usuario.nombres},

Te recordamos que tu reserva reprogramada #{reserva.pk} es mañana:

Fecha: {reserva.fecha_inicio.strftime('%d/%m/%Y a las %H:%M')}
Total: {reserva.total} {reserva.moneda}

¡Esperamos verte!

Saludos,
Equipo de Turismo
                """
                
                send_mail(
                    subject=asunto,
                    message=mensaje,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[usuario.email],
                    fail_silently=True
                )
                
                logger.info(f"Recordatorio enviado para reserva reprogramada {reserva.pk}")
                return True
                
        except Exception as e:
            logger.error(f"Error enviando recordatorio para reserva {reserva.pk}: {str(e)}")
            return False