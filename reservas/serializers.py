
from rest_framework import serializers
from .models import Reserva, ReservaServicio, Acompanante, ReservaAcompanante
from authz.models import Usuario
from catalogo.models import Servicio
from decimal import Decimal
from rest_framework.exceptions import ValidationError
from rest_framework.fields import Field
from typing import cast

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
        read_only_fields = ["estado", "usuario"]

    def create(self, validated_data):
        from .models import ReservaServicio, ReservaAcompanante, Acompanante as AcompananteModel

        detalles = validated_data.pop('detalles', [])
        # Prefer validated nested data; when nested serializer is read-only for 'acompanante'
        # the client's nested object may not appear in validated_data. Fall back to raw
        # request data to accept companion objects sent by the frontend.
        if 'acompanantes' in validated_data:
            acompanantes = validated_data.pop('acompanantes', [])
        else:
            request = self.context.get('request')
            acompanantes = []
            if request is not None:
                acompanantes = request.data.get('acompanantes', [])

        # Calcular precio real desde catalogo y total
        suma = Decimal('0')
        detalles_para_crear = []
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

            # Ayuda a los analizadores estáticos a inferir el tipo
            servicio_obj = cast(Servicio, servicio_obj)

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
                else:
                    # Sin documento, requerimos los campos primarios para crear acompañante
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
