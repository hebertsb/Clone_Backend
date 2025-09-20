"""
Comando para probar la configuración de emails del sistema.
"""

from django.core.management.base import BaseCommand
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
import sys


class Command(BaseCommand):
    help = 'Prueba la configuración de emails del sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email de destino para la prueba (por defecto usa EMAIL_HOST_USER)',
        )
        parser.add_argument(
            '--tipo',
            choices=['simple', 'html', 'completo'],
            default='simple',
            help='Tipo de prueba de email a realizar',
        )
        parser.add_argument(
            '--admin',
            action='store_true',
            help='Enviar también a emails de administradores',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.HTTP_INFO('🧪 Iniciando prueba de configuración de emails...\n')
        )

        # Verificar configuración básica
        if not self._verificar_configuracion():
            return

        # Determinar email de destino
        email_destino = options['email'] or settings.EMAIL_HOST_USER
        if not email_destino:
            self.stdout.write(
                self.style.ERROR('❌ No se pudo determinar email de destino. '
                               'Especifica --email o configura EMAIL_HOST_USER.')
            )
            return

        # Realizar prueba según tipo
        tipo_prueba = options['tipo']
        incluir_admin = options['admin']

        if tipo_prueba == 'simple':
            self._prueba_simple(email_destino, incluir_admin)
        elif tipo_prueba == 'html':
            self._prueba_html(email_destino, incluir_admin)
        elif tipo_prueba == 'completo':
            self._prueba_completa(email_destino, incluir_admin)

    def _verificar_configuracion(self):
        """Verifica que la configuración de email esté completa."""
        
        self.stdout.write('📋 Verificando configuración...')
        
        config_items = [
            ('EMAIL_BACKEND', getattr(settings, 'EMAIL_BACKEND', None)),
            ('EMAIL_HOST', getattr(settings, 'EMAIL_HOST', None)),
            ('EMAIL_PORT', getattr(settings, 'EMAIL_PORT', None)),
            ('EMAIL_HOST_USER', getattr(settings, 'EMAIL_HOST_USER', None)),
            ('EMAIL_HOST_PASSWORD', '***' if getattr(settings, 'EMAIL_HOST_PASSWORD', None) else None),
            ('DEFAULT_FROM_EMAIL', getattr(settings, 'DEFAULT_FROM_EMAIL', None)),
        ]
        
        problemas = []
        
        for nombre, valor in config_items:
            if valor:
                self.stdout.write(f'  ✅ {nombre}: {valor}')
            else:
                self.stdout.write(f'  ❌ {nombre}: No configurado')
                problemas.append(nombre)
        
        if hasattr(settings, 'ADMIN_EMAILS'):
            self.stdout.write(f'  ✅ ADMIN_EMAILS: {len(settings.ADMIN_EMAILS)} emails configurados')
        else:
            self.stdout.write('  ⚠️ ADMIN_EMAILS: No configurado')
        
        if problemas:
            self.stdout.write(
                self.style.ERROR(f'\n❌ Faltan configuraciones: {", ".join(problemas)}')
            )
            self.stdout.write(
                self.style.WARNING('💡 Revisa el archivo .env y la documentación de configuración.')
            )
            return False
        
        self.stdout.write(self.style.SUCCESS('✅ Configuración básica completa\n'))
        return True

    def _prueba_simple(self, email_destino, incluir_admin):
        """Realiza una prueba simple de envío de email."""
        
        self.stdout.write('📧 Enviando email de prueba simple...')
        
        destinatarios = [email_destino]
        if incluir_admin and hasattr(settings, 'ADMIN_EMAILS'):
            destinatarios.extend(settings.ADMIN_EMAILS)
        
        try:
            send_mail(
                subject='Prueba de Email - Sistema de Reservas',
                message='''
Hola!

Este es un email de prueba del sistema de reservas.

Si recibes este mensaje, significa que la configuracion de email esta funcionando correctamente.

Configuracion utilizada:
- Host: {}
- Puerto: {}
- Usuario: {}

Felicidades!

Saludos,
Sistema de Reservas
'''.format(
                    getattr(settings, 'EMAIL_HOST', 'No configurado'),
                    getattr(settings, 'EMAIL_PORT', 'No configurado'),
                    getattr(settings, 'EMAIL_HOST_USER', 'No configurado'),
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=destinatarios,
                fail_silently=False,
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Email enviado exitosamente a: {", ".join(destinatarios)}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error enviando email: {e}')
            )
            self._mostrar_troubleshooting(e)

    def _prueba_html(self, email_destino, incluir_admin):
        """Realiza una prueba de email con formato HTML."""
        
        self.stdout.write('📧 Enviando email de prueba con formato HTML...')
        
        destinatarios = [email_destino]
        if incluir_admin and hasattr(settings, 'ADMIN_EMAILS'):
            destinatarios.extend(settings.ADMIN_EMAILS)
        
        html_content = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Prueba de Email HTML</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #e8f5e8; padding: 20px; border-radius: 8px; border: 2px solid #28a745;">
        <h2 style="color: #155724; text-align: center;">✅ Prueba de Email HTML Exitosa</h2>
        
        <p>¡Felicidades! Si estás viendo este email con formato, significa que:</p>
        
        <ul style="background-color: white; padding: 15px; border-radius: 5px;">
            <li>✅ La configuración SMTP está funcionando</li>
            <li>✅ Los emails HTML se renderizan correctamente</li>
            <li>✅ El sistema está listo para enviar notificaciones</li>
        </ul>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h4>📊 Información de la Configuración:</h4>
            <p><strong>Host:</strong> {}</p>
            <p><strong>Puerto:</strong> {}</p>
            <p><strong>Usuario:</strong> {}</p>
            <p><strong>Fecha de prueba:</strong> {}</p>
        </div>
        
        <p style="text-align: center; margin-top: 30px;">
            <strong>🎉 ¡Sistema de Emails Configurado Correctamente! 🎉</strong>
        </p>
    </div>
</body>
</html>
'''.format(
            getattr(settings, 'EMAIL_HOST', 'No configurado'),
            getattr(settings, 'EMAIL_PORT', 'No configurado'),
            getattr(settings, 'EMAIL_HOST_USER', 'No configurado'),
            '19 de septiembre de 2025'
        )
        
        text_content = '''
✅ Prueba de Email HTML Exitosa

¡Felicidades! La configuración de email está funcionando correctamente.

Información de configuración:
- Host: {}
- Puerto: {}
- Usuario: {}

🎉 ¡Sistema de Emails Configurado Correctamente! 🎉
'''.format(
            getattr(settings, 'EMAIL_HOST', 'No configurado'),
            getattr(settings, 'EMAIL_PORT', 'No configurado'),
            getattr(settings, 'EMAIL_HOST_USER', 'No configurado'),
        )
        
        try:
            msg = EmailMultiAlternatives(
                subject='✅ Prueba HTML - Sistema de Reservas',
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=destinatarios,
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Email HTML enviado exitosamente a: {", ".join(destinatarios)}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error enviando email HTML: {e}')
            )
            self._mostrar_troubleshooting(e)

    def _prueba_completa(self, email_destino, incluir_admin):
        """Realiza una batería completa de pruebas."""
        
        self.stdout.write('🧪 Iniciando prueba completa...\n')
        
        # Prueba 1: Email simple
        self.stdout.write('1️⃣ Prueba de email simple:')
        self._prueba_simple(email_destino, False)
        
        self.stdout.write('\n' + '='*50 + '\n')
        
        # Prueba 2: Email HTML
        self.stdout.write('2️⃣ Prueba de email HTML:')
        self._prueba_html(email_destino, False)
        
        self.stdout.write('\n' + '='*50 + '\n')
        
        # Prueba 3: Email a administradores
        if incluir_admin and hasattr(settings, 'ADMIN_EMAILS'):
            self.stdout.write('3️⃣ Prueba de email a administradores:')
            try:
                send_mail(
                    subject='🔔 Prueba Admin - Sistema de Reservas',
                    message='Prueba de notificación para administradores.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=settings.ADMIN_EMAILS,
                    fail_silently=False,
                )
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Email a admins enviado: {", ".join(settings.ADMIN_EMAILS)}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error enviando a admins: {e}')
                )
        
        self.stdout.write('\n' + '='*50 + '\n')
        self.stdout.write(
            self.style.SUCCESS('🎉 Prueba completa finalizada!')
        )

    def _mostrar_troubleshooting(self, error):
        """Muestra consejos de troubleshooting según el error."""
        
        error_str = str(error).lower()
        
        self.stdout.write('\n💡 Consejos de troubleshooting:')
        
        if 'authentication' in error_str:
            self.stdout.write('''
🔐 Error de autenticación:
  • Para Gmail: Usa contraseña de aplicación, no tu contraseña normal
  • Ve a: https://myaccount.google.com/security
  • Crea una contraseña de aplicación específica para esta app
  • Asegúrate de que 2FA esté habilitado en Gmail
''')
        
        elif 'connection' in error_str or 'connect' in error_str:
            self.stdout.write('''
🌐 Error de conexión:
  • Verifica tu conexión a internet
  • Para Gmail: smtp.gmail.com puerto 587
  • Para Outlook: smtp-mail.outlook.com puerto 587
  • Verifica que EMAIL_HOST y EMAIL_PORT sean correctos
''')
        
        elif 'recipient' in error_str:
            self.stdout.write('''
📧 Error de destinatario:
  • Verifica que el email destinatario sea válido
  • Revisa la carpeta de spam del destinatario
  • Puede que el proveedor de email tenga límites de envío
''')
        
        else:
            self.stdout.write('''
🔍 Error general:
  • Revisa los logs detallados
  • Verifica todas las variables de entorno en .env
  • Prueba primero con EMAIL_BACKEND=console para debug
  • Contacta al soporte técnico si persiste el problema
''')
        
        self.stdout.write('\n📖 Para más información, revisa: GUIA_CONFIGURACION_EMAILS.md')