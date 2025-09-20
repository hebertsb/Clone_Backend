
from rest_framework import serializers
from .models import Reserva, ReservaServicio, Acompanante, ReservaAcompanante, HistorialReprogramacion, ReglasReprogramacion, ConfiguracionGlobalReprogramacion
from authz.models import Usuario
from catalogo.models import Servicio
from decimal import Decimal
from rest_framework.exceptions import ValidationError
from rest_framework.fields import Field
from typing import cast
from django.utils import timezone
from datetime import timedelta

class ReservaServicioSerializer(serializers.ModelSerializer):
    tipo = serializers.CharField(source="servicio.tipo", read_only=True)
    titulo = serializers.CharField(source="servicio.titulo", read_only=True)
    precio_unitario = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    class Meta:
        model = ReservaServicio
        fields = ["servicio", "tipo", "titulo", "cantidad", "precio_unitario", "fecha_servicio"]

class UsuarioReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["id", "nombres", "apellidos", "email", "telefono"]

class AcompananteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acompanante
        fields = ["id", "nombre", "apellido", "documento", "fecha_nacimiento", "nacionalidad", "email", "telefono"]

class ReservaAcompananteSerializer(serializers.ModelSerializer):
    acompanante = AcompananteSerializer(read_only=True)
    acompanante_id = serializers.PrimaryKeyRelatedField(write_only=True, source='acompanante', queryset=Acompanante.objects.all(), required=False)
    reserva = serializers.PrimaryKeyRelatedField(queryset=Reserva.objects.all(), required=False)

    class Meta:
        model = ReservaAcompanante
        fields = ["reserva", "acompanante", "acompanante_id", "estado", "es_titular"]
        read_only_fields = ["acompanante"]
        validators = []

    def validate(self, attrs):
        es_titular = attrs.get('es_titular', False)
        reserva = attrs.get('reserva')
        acompanante = attrs.get('acompanante')

        # Evitar duplicados (misma reserva + mismo acompañante)
        if reserva and isinstance(acompanante, Acompanante) and ReservaAcompanante.objects.filter(reserva=reserva, acompanante=acompanante).exists():
            raise serializers.ValidationError({"acompanante": "Este acompañante ya está asociado a la reserva."})

        # Un solo titular por reserva
        if es_titular and reserva and ReservaAcompanante.objects.filter(reserva=reserva, es_titular=True).exists():
            raise serializers.ValidationError({"es_titular": "Ya existe un titular para esta reserva."})

        # Permisos: si el usuario es CLIENTE solo puede agregar a sus propias reservas
        request = self.context.get('request')
        if request is not None:
            user = request.user
            roles = []
            if hasattr(user, 'roles'):
                roles = list(user.roles.values_list('nombre', flat=True))
            if 'CLIENTE' in roles and reserva and reserva.usuario != user:
                raise serializers.ValidationError({"detail": "No puedes agregar acompañantes a una reserva que no es tuya."})

        return attrs

class ReservaSerializer(serializers.ModelSerializer):
    usuario = UsuarioReservaSerializer(read_only=True)
    detalles = ReservaServicioSerializer(many=True)
    acompanantes = ReservaAcompananteSerializer(many=True, required=False)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    class Meta:
        model = Reserva
        fields = [
            "id", "usuario", "fecha_inicio", "estado", "cupon", "total", "moneda", "detalles", "acompanantes", "created_at", "updated_at"
        ]
    read_only_fields = ["usuario"]

    def create(self, validated_data):
        from .models import ReservaServicio, ReservaAcompanante, Acompanante as AcompananteModel

        import sys
        print('DEBUG validated_data:', validated_data, file=sys.stderr)
        request = self.context.get('request')
        if request is not None:
            print('DEBUG request.data:', request.data, file=sys.stderr)

        detalles = validated_data.pop('detalles', [])
        # Prefer validated nested data; when nested serializer is read-only for 'acompanante'
        # the client's nested object may not appear in validated_data. Fall back to raw
        # request data to accept companion objects sent by the frontend.
        # SIEMPRE tomar los acompañantes desde request.data para asegurar que llegan completos
        acompanantes = []
        if request is not None:
            acompanantes = request.data.get('acompanantes', [])

        # Calcular precio real desde catalogo y total
        suma = Decimal('0')
        detalles_para_crear = []
        validated_data.pop('acompanantes', None)
        acompanantes = request.data.get('acompanantes', []) if request is not None else []  # Tomar acompañantes desde request.data
        for d in detalles:
            servicio_val = d.get('servicio')
            cantidad = int(d.get('cantidad', 1))
            fecha_servicio = d.get('fecha_servicio')

            # El campo nested puede venir ya convertido a instancia Servicio
            if isinstance(servicio_val, Servicio):
                servicio_obj = servicio_val
            else:
                try:
                    servicio_obj = Servicio.objects.get(pk=servicio_val)
                except Servicio.DoesNotExist:
                    raise ValidationError({"detalles": f"Servicio con id {servicio_val} no encontrado."})

            # VALIDACIÓN DE CUPO USANDO max_personas DEL PAQUETE
            paquete = getattr(servicio_obj, 'paquete', None)
            if paquete is not None:
                max_personas = getattr(paquete, 'max_personas', None)
                if max_personas is not None:
                    # Contar personas ya reservadas para ese paquete
                    from reservas.models import ReservaServicio
                    reservas_servicio = ReservaServicio.objects.filter(servicio=servicio_obj)
                    total_personas_reservadas = sum([rs.cantidad for rs in reservas_servicio])
                    personas_nueva_reserva = cantidad
                    if total_personas_reservadas + personas_nueva_reserva > max_personas:
                        raise ValidationError({
                            'detalles': f"No hay cupo suficiente en el paquete '{paquete.nombre}'. Cupo máximo: {max_personas}, reservados: {total_personas_reservadas}"
                        })

            precio_real = servicio_obj.costo
            subtotal = Decimal(str(precio_real)) * cantidad
            suma += subtotal
            detalles_para_crear.append({
                'servicio': servicio_obj,
                'cantidad': cantidad,
                'precio_unitario': precio_real,
                'fecha_servicio': fecha_servicio,
            })

        # Sobrescribir total con la suma calculada
        validated_data['total'] = suma

        # Crear la reserva
        reserva = Reserva.objects.create(**validated_data)

        # Crear detalles con precio real
        for detalle in detalles_para_crear:
            ReservaServicio.objects.create(reserva=reserva, **detalle)

        # Procesar acompañantes si vienen en el payload
        # El formato aceptado por acompanantes será una lista de objetos con la forma:
        # { "acompanante": {..datos..} | <id>, "estado": "CONFIRMADO", "es_titular": true }
        titular_count = 0

        for rv in acompanantes:
            # rv puede ser un dict que contenga 'acompanante' o directamente los campos del acompanante
            v = rv.get('acompanante') if isinstance(rv, dict) and 'acompanante' in rv else rv
            estado = rv.get('estado') if isinstance(rv, dict) else None
            es_titular = rv.get('es_titular', False) if isinstance(rv, dict) else False

            acompanante_obj = None
            # v puede ser instancia de Acompanante, un pk (int) o dict con datos
            if isinstance(v, AcompananteModel):
                acompanante_obj = v
            elif isinstance(v, int):
                acompanante_obj = AcompananteModel.objects.get(pk=v)
            elif isinstance(v, dict):
                # Validar campos requeridos antes de crear
                documento = v.get('documento')
                nombre = v.get('nombre')
                apellido = v.get('apellido')
                fecha_nacimiento = v.get('fecha_nacimiento')
                # Normalizar fecha_nacimiento si viene como string
                if isinstance(fecha_nacimiento, str):
                    try:
                         fecha_nacimiento = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
                    except ValueError:
                        raise ValidationError({
                            "acompanantes": f"Formato de fecha inválido para '{fecha_nacimiento}'. Usa YYYY-MM-DD."
                    })
                # Si nos dan documento, intentar obtener; si no existe y faltan campos requeridos, lanzar error
                if documento:
                    acompanante_obj = AcompananteModel.objects.filter(documento=documento).first()
                    if not acompanante_obj:
                        # Para crear nuevo acompañante se requieren nombre, apellido y fecha_nacimiento
                        missing = []
                        if not nombre:
                            missing.append('nombre')
                        if not apellido:
                            missing.append('apellido')
                        if not fecha_nacimiento:
                            missing.append('fecha_nacimiento')
                        if missing:
                            raise ValidationError({
                                'acompanantes': f"Faltan campos para crear acompañante con documento '{documento}': {', '.join(missing)}"
                            })
                        acompanante_obj = AcompananteModel.objects.create(
                            documento=documento,
                            nombre=nombre,
                            apellido=apellido,
                            fecha_nacimiento=fecha_nacimiento,
                            nacionalidad=v.get('nacionalidad'),
                            email=v.get('email'),
                            telefono=v.get('telefono'),
                        )

        if acompanantes:
            for rv in acompanantes:
                # Permitir ambos formatos: plano y anidado
                datos = None
                estado = None
                es_titular = False
                if isinstance(rv, dict):
                    if 'acompanante' in rv and isinstance(rv['acompanante'], dict):
                        datos = rv['acompanante']
                        estado = rv.get('estado')
                        es_titular = rv.get('es_titular', False)
                    else:
                        datos = rv
                        estado = rv.get('estado')
                        es_titular = rv.get('es_titular', False)

                else:
                    datos = rv

                acompanante_obj = None
                # datos puede ser instancia de Acompanante, un pk (int) o dict con datos
                if isinstance(datos, AcompananteModel):
                    acompanante_obj = datos
                elif isinstance(datos, int):
                    acompanante_obj = AcompananteModel.objects.get(pk=datos)
                elif isinstance(datos, dict):
                    # Si el dict tiene los campos de persona, usarlos siempre
                    documento = datos.get('documento', '')
                    nombre = datos.get('nombre', '')
                    apellido = datos.get('apellido', '')
                    fecha_nacimiento = datos.get('fecha_nacimiento', None)
                    nacionalidad = datos.get('nacionalidad')
                    email = datos.get('email')
                    telefono = datos.get('telefono')

                    # Validar todos los campos obligatorios antes de crear
                    missing = []
                    if not documento:
                        missing.append('documento')
                    if not nombre:
                        missing.append('nombre')
                    if not apellido:
                        missing.append('apellido')
                    if not fecha_nacimiento:
                        missing.append('fecha_nacimiento')
                    if missing:
                        raise ValidationError({
                            'acompanantes': f"Faltan campos obligatorios para crear acompañante: {', '.join(missing)}"
                        })

                    # Si nos dan documento, intentar obtener; si no existe, crear
                    acompanante_obj = AcompananteModel.objects.filter(documento=documento).first()
                    if not acompanante_obj:
                        acompanante_obj = AcompananteModel.objects.create(
                            documento=documento,
                            nombre=nombre,
                            apellido=apellido,
                            fecha_nacimiento=fecha_nacimiento,
                            nacionalidad=nacionalidad,
                            email=email,
                            telefono=telefono,
                        )

                if es_titular:
                    titular_count += 1

                ReservaAcompanante.objects.create(reserva=reserva, acompanante=acompanante_obj, estado=estado or 'CONFIRMADO', es_titular=es_titular)

            if titular_count > 1:
                raise ValidationError({"acompanantes": "Solo puede haber un titular por reserva."})

        return reserva

    def update(self, instance, validated_data):
        from .models import ReservaServicio, ReservaAcompanante, Acompanante as AcompananteModel

        detalles = validated_data.pop('detalles', None)
        # Prefer validated nested data; if missing, use raw request payload (allows nested acompanante dicts)
        if 'acompanantes' in validated_data:
            acompanantes = validated_data.pop('acompanantes', None)
        else:
            request = self.context.get('request')
            acompanantes = None
            if request is not None:
                acompanantes = request.data.get('acompanantes', None)

        # Actualizar campos simples
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Si vienen detalles, sincronizarlos: crear/actualizar/eliminar
        if detalles is not None:
            # Mapear servicios existentes por id
            existentes = {rs.servicio_id: rs for rs in instance.detalles.all()}
            nuevos_servicios = set()
            suma = Decimal('0')
            for d in detalles:
                servicio_val = d.get('servicio')
                cantidad = int(d.get('cantidad', 1))
                fecha_servicio = d.get('fecha_servicio')

                if isinstance(servicio_val, Servicio):
                    servicio_obj = servicio_val
                else:
                    servicio_obj = Servicio.objects.get(pk=servicio_val)
                # Ayuda a los analizadores estáticos
                servicio_obj = cast(Servicio, servicio_obj)

                precio_real = servicio_obj.costo
                subtotal = Decimal(str(precio_real)) * cantidad
                suma += subtotal

                servicio_id = getattr(servicio_obj, 'pk', None)
                if servicio_id in existentes:
                    rs = existentes.pop(servicio_id)
                    rs.cantidad = cantidad
                    rs.precio_unitario = precio_real
                    rs.fecha_servicio = fecha_servicio
                    rs.save()
                else:
                    ReservaServicio.objects.create(reserva=instance, servicio=servicio_obj, cantidad=cantidad, precio_unitario=precio_real, fecha_servicio=fecha_servicio)
                nuevos_servicios.add(servicio_id)

            # Eliminar los que quedaron en existentes
            for rem in existentes.values():
                rem.delete()

            # Actualizar total con suma calculada
            instance.total = suma

        # Procesar acompañantes: sincronizar asociaciones
        if acompanantes is not None:
            # Construir lista actual de acompanantes por id
            actuales = {ra.acompanante_id: ra for ra in instance.acompanantes.all()}
            titular_count = 0
            for rv in acompanantes:
                v = rv.get('acompanante') if isinstance(rv, dict) and 'acompanante' in rv else rv
                estado = rv.get('estado') if isinstance(rv, dict) else None
                es_titular = rv.get('es_titular', False) if isinstance(rv, dict) else False

                acompanante_obj = None
                if isinstance(v, AcompananteModel):
                    acompanante_obj = v
                elif isinstance(v, int):
                    acompanante_obj = AcompananteModel.objects.get(pk=v)
                elif isinstance(v, dict):
                    documento = v.get('documento')
                    nombre = v.get('nombre')
                    apellido = v.get('apellido')
                    fecha_nacimiento = v.get('fecha_nacimiento')

                    if documento:
                        acompanante_obj = AcompananteModel.objects.filter(documento=documento).first()
                        if not acompanante_obj:
                            missing = []
                            if not nombre:
                                missing.append('nombre')
                            if not apellido:
                                missing.append('apellido')
                            if not fecha_nacimiento:
                                missing.append('fecha_nacimiento')
                            if missing:
                                raise ValidationError({
                                    'acompanantes': f"Faltan campos para crear acompañante con documento '{documento}': {', '.join(missing)}"
                                })
                            acompanante_obj = AcompananteModel.objects.create(
                                documento=documento,
                                nombre=nombre,
                                apellido=apellido,
                                fecha_nacimiento=fecha_nacimiento,
                                nacionalidad=v.get('nacionalidad'),
                                email=v.get('email'),
                                telefono=v.get('telefono'),
                            )
                    else:
                        missing = []
                        if not nombre:
                            missing.append('nombre')
                        if not apellido:
                            missing.append('apellido')
                        if not fecha_nacimiento:
                            missing.append('fecha_nacimiento')
                        if missing:
                            raise ValidationError({'acompanantes': f"Faltan campos para crear acompañante: {', '.join(missing)}"})
                        acompanante_obj = AcompananteModel.objects.create(
                            documento=v.get('documento', ''),
                            nombre=nombre,
                            apellido=apellido,
                            fecha_nacimiento=fecha_nacimiento,
                            nacionalidad=v.get('nacionalidad'),
                            email=v.get('email'),
                            telefono=v.get('telefono'),
                        )
                else:
                    # no se reconoce el formato, saltar
                    continue

                # Ayuda a los analizadores estáticos a inferir el tipo
                acompanante_obj = cast(Acompanante, acompanante_obj)

                if es_titular:
                    titular_count += 1

                acompanante_id = getattr(acompanante_obj, 'pk', None)
                if acompanante_id in actuales:
                    ra = actuales.pop(acompanante_id)
                    ra.estado = estado or ra.estado
                    ra.es_titular = es_titular
                    ra.save()
                else:
                    ReservaAcompanante.objects.create(reserva=instance, acompanante=acompanante_obj, estado=estado or 'CONFIRMADO', es_titular=es_titular)

            # Eliminar asociaciones que no vinieron en el payload
            for rem in actuales.values():
                rem.delete()
                

            if titular_count > 1:
                raise ValidationError({"acompanantes": "Solo puede haber un titular por reserva."})

        instance.save()
        return instance


# Nuevos serializadores para reprogramaciones

class HistorialReprogramacionSerializer(serializers.ModelSerializer):
    reprogramado_por = UsuarioReservaSerializer(read_only=True)
    
    class Meta:
        model = HistorialReprogramacion
        fields = [
            'id', 'fecha_anterior', 'fecha_nueva', 'motivo', 
            'reprogramado_por', 'notificacion_enviada', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'reprogramado_por', 'notificacion_enviada']


class ReprogramacionReservaSerializer(serializers.Serializer):
    """Serializador específico para solicitudes de reprogramación"""
    nueva_fecha = serializers.DateTimeField(
        help_text="Nueva fecha y hora para la reserva"
    )
    motivo = serializers.CharField(
        max_length=500, 
        required=False, 
        allow_blank=True,
        help_text="Motivo de la reprogramación (opcional)"
    )
    
    def validate_nueva_fecha(self, value):
        """Validaciones para la nueva fecha usando reglas dinámicas"""
        ahora = timezone.now()
        
        # No se puede reprogramar a una fecha pasada
        if value <= ahora:
            raise ValidationError("No se puede reprogramar a una fecha pasada.")
        
        # Obtener usuario y roles del contexto
        request = self.context.get('request')
        roles = []
        if request and hasattr(request, 'user'):
            user = request.user
            if isinstance(user, Usuario) and hasattr(user, 'roles'):
                roles = list(user.roles.values_list('nombre', flat=True))
        
        # Aplicar reglas dinámicas de tiempo mínimo
        tiempo_minimo = None
        for rol in roles + ['ALL']:
            regla = ReglasReprogramacion.obtener_regla_activa('TIEMPO_MINIMO', rol)
            if regla:
                tiempo_minimo = regla.obtener_valor()
                break
        
        # Si no hay regla específica, usar 24 horas por defecto
        if tiempo_minimo is None:
            tiempo_minimo = 24
        
        if isinstance(tiempo_minimo, (int, float)):
            tiempo_requerido = ahora + timedelta(hours=tiempo_minimo)
            if value <= tiempo_requerido:
                regla_activa = ReglasReprogramacion.obtener_regla_activa('TIEMPO_MINIMO', roles[0] if roles else 'ALL')
                mensaje = (regla_activa.mensaje_error if regla_activa and regla_activa.mensaje_error 
                          else f"La reprogramación debe hacerse con al menos {tiempo_minimo} horas de anticipación.")
                raise ValidationError(mensaje)
        
        # Aplicar reglas dinámicas de tiempo máximo
        tiempo_maximo = None
        for rol in roles + ['ALL']:
            regla = ReglasReprogramacion.obtener_regla_activa('TIEMPO_MAXIMO', rol)
            if regla:
                tiempo_maximo = regla.obtener_valor()
                break
        
        # Si no hay regla específica, usar 1 año por defecto
        if tiempo_maximo is None:
            tiempo_maximo = 365 * 24  # 1 año en horas
        
        if isinstance(tiempo_maximo, (int, float)):
            tiempo_limite = ahora + timedelta(hours=tiempo_maximo)
            if value > tiempo_limite:
                regla_activa = ReglasReprogramacion.obtener_regla_activa('TIEMPO_MAXIMO', roles[0] if roles else 'ALL')
                mensaje = (regla_activa.mensaje_error if regla_activa and regla_activa.mensaje_error 
                          else f"No se puede reprogramar más de {tiempo_maximo/24:.0f} días en el futuro.")
                raise ValidationError(mensaje)
        
        # Verificar días blackout
        for rol in roles + ['ALL']:
            regla = ReglasReprogramacion.obtener_regla_activa('DIAS_BLACKOUT', rol)
            if regla:
                try:
                    dias_blackout = regla.obtener_valor()
                    if isinstance(dias_blackout, list):
                        dia_semana = value.weekday()  # 0=lunes, 6=domingo
                        nombres_dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
                        if nombres_dias[dia_semana] in [d.lower() for d in dias_blackout]:
                            mensaje = (regla.mensaje_error if regla.mensaje_error 
                                     else f"No se puede reprogramar en {nombres_dias[dia_semana]}.")
                            raise ValidationError(mensaje)
                except:
                    pass
        
        # Verificar horas blackout
        for rol in roles + ['ALL']:
            regla = ReglasReprogramacion.obtener_regla_activa('HORAS_BLACKOUT', rol)
            if regla:
                try:
                    horas_blackout = regla.obtener_valor()
                    if isinstance(horas_blackout, list):
                        hora_nueva = value.hour
                        if hora_nueva in horas_blackout:
                            mensaje = (regla.mensaje_error if regla.mensaje_error 
                                     else f"No se puede reprogramar a las {hora_nueva}:00 horas.")
                            raise ValidationError(mensaje)
                except:
                    pass
        
        return value
    
    def validate(self, attrs):
        """Validaciones adicionales considerando el contexto y reglas dinámicas"""
        request = self.context.get('request')
        reserva = self.context.get('reserva')
        
        if reserva:
            # Validar que la reserva se pueda reprogramar
            if reserva.estado in ['CANCELADA']:
                raise ValidationError("No se puede reprogramar una reserva cancelada.")
            
            # Obtener roles del usuario
            roles = []
            if request and hasattr(request, 'user'):
                user = request.user
                if isinstance(user, Usuario) and hasattr(user, 'roles'):
                    roles = list(user.roles.values_list('nombre', flat=True))
            
            # Aplicar límite dinámico de reprogramaciones
            limite_reprogramaciones = None
            for rol in roles + ['ALL']:
                regla = ReglasReprogramacion.obtener_regla_activa('LIMITE_REPROGRAMACIONES', rol)
                if regla:
                    limite_reprogramaciones = regla.obtener_valor()
                    break
            
            # Si no hay regla específica, usar 3 por defecto
            if limite_reprogramaciones is None:
                limite_reprogramaciones = 3
            
            if isinstance(limite_reprogramaciones, (int, float)):
                if reserva.numero_reprogramaciones >= int(limite_reprogramaciones):
                    regla_activa = ReglasReprogramacion.obtener_regla_activa('LIMITE_REPROGRAMACIONES', roles[0] if roles else 'ALL')
                    mensaje = (regla_activa.mensaje_error if regla_activa and regla_activa.mensaje_error 
                              else f"Esta reserva ya ha sido reprogramada el máximo número de veces permitido ({limite_reprogramaciones}).")
                    raise ValidationError(mensaje)
            
            # Validar que no sea la misma fecha
            nueva_fecha = attrs.get('nueva_fecha')
            if nueva_fecha and reserva.fecha_inicio:
                if nueva_fecha.date() == reserva.fecha_inicio.date():
                    raise ValidationError("La nueva fecha debe ser diferente a la fecha actual.")
            
            # Verificar servicios restringidos
            for rol in roles + ['ALL']:
                regla = ReglasReprogramacion.obtener_regla_activa('SERVICIOS_RESTRINGIDOS', rol)
                if regla:
                    try:
                        servicios_restringidos = regla.obtener_valor()
                        if isinstance(servicios_restringidos, list):
                            servicios_reserva = list(reserva.detalles.values_list('servicio__titulo', flat=True))
                            for servicio in servicios_reserva:
                                if servicio in servicios_restringidos:
                                    mensaje = (regla.mensaje_error if regla.mensaje_error 
                                             else f"El servicio '{servicio}' tiene restricciones para reprogramar.")
                                    raise ValidationError(mensaje)
                    except:
                        pass
        
        return attrs


class ReservaConHistorialSerializer(ReservaSerializer):
    """Extiende ReservaSerializer para incluir información de reprogramaciones"""
    historial_reprogramaciones = HistorialReprogramacionSerializer(many=True, read_only=True)
    puede_reprogramar = serializers.SerializerMethodField()
    
    class Meta(ReservaSerializer.Meta):
        fields = ReservaSerializer.Meta.fields + [
            'fecha_original', 'fecha_reprogramacion', 'motivo_reprogramacion', 
            'numero_reprogramaciones', 'reprogramado_por', 'historial_reprogramaciones',
            'puede_reprogramar'
        ]
        read_only_fields = getattr(ReservaSerializer.Meta, 'read_only_fields', []) + [
            'fecha_original', 'fecha_reprogramacion', 'numero_reprogramaciones', 
            'reprogramado_por', 'historial_reprogramaciones'
        ]
    
    def get_puede_reprogramar(self, obj):
        """Determina si la reserva puede ser reprogramada"""
        if obj.estado in ['CANCELADA']:
            return False
        
        if obj.numero_reprogramaciones >= 3:
            return False
        
        # Verificar que la fecha de inicio no sea muy próxima (menos de 24 horas)
        ahora = timezone.now()
        if obj.fecha_inicio <= ahora + timedelta(hours=24):
            return False
        
        return True


# ============================================================================
# SERIALIZADORES PARA REGLAS DE REPROGRAMACIÓN
# ============================================================================

class ReglasReprogramacionSerializer(serializers.ModelSerializer):
    """Serializador para gestionar reglas de reprogramación."""
    
    valor_calculado = serializers.SerializerMethodField()
    es_aplicable = serializers.SerializerMethodField()
    
    class Meta:
        from .models import ReglasReprogramacion
        model = ReglasReprogramacion
        fields = [
            'id', 'nombre', 'tipo_regla', 'aplicable_a',
            'valor_numerico', 'valor_decimal', 'valor_texto', 'valor_booleano',
            'fecha_inicio_vigencia', 'fecha_fin_vigencia', 'activa', 'prioridad',
            'mensaje_error', 'condiciones_extras', 'valor_calculado', 'es_aplicable',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_valor_calculado(self, obj):
        """Retorna el valor interpretado de la regla."""
        return obj.obtener_valor()
    
    def get_es_aplicable(self, obj):
        """Verifica si la regla es aplicable al usuario actual."""
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            return True
        
        user = request.user
        if isinstance(user, Usuario) and hasattr(user, 'roles'):
            roles = list(user.roles.values_list('nombre', flat=True))
            for rol in roles:
                if obj.es_aplicable_a_rol(rol):
                    return True
        return False
    
    def validate(self, attrs):
        """Validación completa de reglas."""
        # Validar que al menos un valor esté definido
        valores = [
            attrs.get('valor_numerico'),
            attrs.get('valor_decimal'), 
            attrs.get('valor_texto'),
            attrs.get('valor_booleano')
        ]
        
        if all(v is None or v == '' for v in valores):
            raise ValidationError("Debe definir al menos un valor para la regla.")
        
        # Validar fechas de vigencia
        fecha_inicio = attrs.get('fecha_inicio_vigencia')
        fecha_fin = attrs.get('fecha_fin_vigencia')
        
        if fecha_inicio and fecha_fin and fecha_inicio >= fecha_fin:
            raise ValidationError({
                'fecha_fin_vigencia': 'La fecha de fin debe ser posterior a la fecha de inicio.'
            })
        
        # Validaciones específicas por tipo de regla
        tipo_regla = attrs.get('tipo_regla')
        
        if tipo_regla in ['TIEMPO_MINIMO', 'TIEMPO_MAXIMO'] and not attrs.get('valor_numerico'):
            raise ValidationError({
                'valor_numerico': f'El tipo de regla {tipo_regla} requiere un valor numérico (horas).'
            })
        
        if tipo_regla in ['LIMITE_REPROGRAMACIONES', 'LIMITE_DIARIO', 'LIMITE_SEMANAL', 'LIMITE_MENSUAL']:
            valor = attrs.get('valor_numerico')
            if not valor or valor < 0:
                raise ValidationError({
                    'valor_numerico': f'El tipo de regla {tipo_regla} requiere un valor numérico positivo.'
                })
        
        if tipo_regla == 'DESCUENTO_PENALIZACION':
            valor = attrs.get('valor_decimal')
            if valor is None or valor < 0 or valor > 100:
                raise ValidationError({
                    'valor_decimal': 'La penalización debe ser un porcentaje entre 0 y 100.'
                })
        
        if tipo_regla in ['DIAS_BLACKOUT', 'HORAS_BLACKOUT', 'SERVICIOS_RESTRINGIDOS']:
            if not attrs.get('valor_texto'):
                raise ValidationError({
                    'valor_texto': f'El tipo de regla {tipo_regla} requiere valores en formato texto/JSON.'
                })
        
        return attrs


class ConfiguracionGlobalSerializer(serializers.ModelSerializer):
    """Serializador para configuraciones globales."""
    
    valor_tipado = serializers.SerializerMethodField()
    
    class Meta:
        from .models import ConfiguracionGlobalReprogramacion
        model = ConfiguracionGlobalReprogramacion
        fields = [
            'id', 'clave', 'valor', 'descripcion', 'tipo_valor',
            'activa', 'valor_tipado', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_valor_tipado(self, obj):
        """Retorna el valor convertido al tipo correcto."""
        try:
            return obj.obtener_valor_tipado()
        except:
            return obj.valor
    
    def validate_valor(self, value):
        """Valida que el valor sea compatible con el tipo especificado."""
        initial_data = getattr(self, 'initial_data', {})
        tipo_valor = initial_data.get('tipo_valor', 'STRING') if initial_data else 'STRING'
        
        if tipo_valor == 'INTEGER':
            try:
                int(value)
            except ValueError:
                raise ValidationError("El valor debe ser un número entero válido.")
        
        elif tipo_valor == 'DECIMAL':
            try:
                float(value)
            except ValueError:
                raise ValidationError("El valor debe ser un número decimal válido.")
        
        elif tipo_valor == 'BOOLEAN':
            if value.lower() not in ['true', 'false', '1', '0', 'yes', 'no', 'si']:
                raise ValidationError("El valor debe ser un booleano válido (true/false, 1/0, etc.).")
        
        elif tipo_valor == 'JSON':
            import json
            try:
                json.loads(value)
            except json.JSONDecodeError:
                raise ValidationError("El valor debe ser un JSON válido.")
        
        return value


class ValidadorReglasSerializer(serializers.Serializer):
    """Serializador para validar si una reprogramación cumple con las reglas."""
    
    reserva_id = serializers.IntegerField()
    nueva_fecha = serializers.DateTimeField()
    motivo = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        """Aplica todas las reglas activas y retorna errores si las viola."""
        from .models import Reserva, ReglasReprogramacion
        
        reserva_id = attrs.get('reserva_id')
        nueva_fecha = attrs.get('nueva_fecha')
        
        # Obtener la reserva
        try:
            reserva = Reserva.objects.get(pk=reserva_id)
        except Reserva.DoesNotExist:
            raise ValidationError({'reserva_id': 'Reserva no encontrada.'})
        
        # Obtener usuario y roles
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            raise ValidationError('Usuario no autenticado.')
        
        user = request.user
        roles = []
        if isinstance(user, Usuario) and hasattr(user, 'roles'):
            roles = list(user.roles.values_list('nombre', flat=True))
        
        errores = []
        
        # Aplicar cada tipo de regla
        for rol in roles + ['ALL']:
            # Tiempo mínimo de anticipación
            regla = ReglasReprogramacion.obtener_regla_activa('TIEMPO_MINIMO', rol)
            if regla:
                horas_minimas = regla.obtener_valor()
                if horas_minimas is not None and isinstance(horas_minimas, (int, float)):
                    tiempo_anticipacion = nueva_fecha - timezone.now()
                    if tiempo_anticipacion.total_seconds() < (horas_minimas * 3600):
                        errores.append(regla.mensaje_error or 
                                     f"Debe reprogramar con al menos {horas_minimas} horas de anticipación.")
            
            # Tiempo máximo para reprogramar
            regla = ReglasReprogramacion.obtener_regla_activa('TIEMPO_MAXIMO', rol)
            if regla:
                horas_maximas = regla.obtener_valor()
                if horas_maximas is not None and isinstance(horas_maximas, (int, float)):
                    tiempo_hasta_fecha = nueva_fecha - timezone.now()
                    if tiempo_hasta_fecha.total_seconds() > (horas_maximas * 3600):
                        errores.append(regla.mensaje_error or 
                                     f"No puede reprogramar con más de {horas_maximas} horas de anticipación.")
            
            # Límite de reprogramaciones
            regla = ReglasReprogramacion.obtener_regla_activa('LIMITE_REPROGRAMACIONES', rol)
            if regla:
                limite = regla.obtener_valor()
                if limite is not None and isinstance(limite, (int, float)):
                    if reserva.numero_reprogramaciones >= int(limite):
                        errores.append(regla.mensaje_error or 
                                     f"Ha alcanzado el límite de {limite} reprogramaciones para esta reserva.")
            
            # Días blackout
            regla = ReglasReprogramacion.obtener_regla_activa('DIAS_BLACKOUT', rol)
            if regla:
                try:
                    import json
                    dias_blackout = regla.obtener_valor()
                    if isinstance(dias_blackout, list):
                        dia_semana = nueva_fecha.weekday()  # 0=lunes, 6=domingo
                        nombres_dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
                        if nombres_dias[dia_semana] in [d.lower() for d in dias_blackout]:
                            errores.append(regla.mensaje_error or 
                                         f"No se puede reprogramar en {nombres_dias[dia_semana]}.")
                except:
                    pass
            
            # Horas blackout
            regla = ReglasReprogramacion.obtener_regla_activa('HORAS_BLACKOUT', rol)
            if regla:
                try:
                    horas_blackout = regla.obtener_valor()
                    if isinstance(horas_blackout, list):
                        hora_nueva = nueva_fecha.hour
                        if hora_nueva in horas_blackout:
                            errores.append(regla.mensaje_error or 
                                         f"No se puede reprogramar a las {hora_nueva}:00 horas.")
                except:
                    pass
        
        if errores:
            raise ValidationError({'reglas_violadas': errores})
        
        return attrs


class ResumenReglasSerializer(serializers.Serializer):
    """Serializador para mostrar un resumen de reglas aplicables a un usuario."""
    
    def to_representation(self, instance):
        """Genera resumen de reglas activas."""
        from .models import ReglasReprogramacion
        
        request = self.context.get('request')
        roles = ['ALL']
        
        if request and hasattr(request, 'user'):
            user = request.user
            if isinstance(user, Usuario) and hasattr(user, 'roles'):
                roles.extend(list(user.roles.values_list('nombre', flat=True)))
        
        resumen = {}
        
        for tipo_regla, descripcion in ReglasReprogramacion.TIPOS_REGLA:
            for rol in roles:
                regla = ReglasReprogramacion.obtener_regla_activa(tipo_regla, rol)
                if regla and tipo_regla not in resumen:
                    resumen[tipo_regla] = {
                        'descripcion': descripcion,
                        'valor': regla.obtener_valor(),
                        'aplicable_a': regla.aplicable_a,
                        'mensaje': regla.mensaje_error or f"Regla: {descripcion}",
                        'activa_desde': regla.fecha_inicio_vigencia,
                        'activa_hasta': regla.fecha_fin_vigencia,
                    }
        
        return {
            'reglas_activas': resumen,
            'total_reglas': len(resumen),
            'roles_usuario': roles[1:] if len(roles) > 1 else ['No autenticado']
        }
