"""
Validadores dinámicos para el sistema de reprogramaciones.
Este módulo contiene la lógica central de validación que aplica todas las reglas configuradas.
"""

from typing import List, Dict, Any, Optional
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from authz.models import Usuario


class ValidadorReprogramacionDinamico:
    """
    Validador que aplica dinámicamente todas las reglas configuradas.
    Este es el núcleo del sistema de validación flexible.
    """
    
    def __init__(self, usuario: Optional[Usuario] = None):
        self.usuario = usuario
        self.roles = self._obtener_roles_usuario()
        self.errores: List[str] = []
        self.warnings: List[str] = []
    
    def _obtener_roles_usuario(self) -> List[str]:
        """Obtiene los roles del usuario actual."""
        if not self.usuario or not isinstance(self.usuario, Usuario):
            return ['ALL']
        
        try:
            roles = list(self.usuario.roles.values_list('nombre', flat=True))
            return roles + ['ALL']  # Siempre incluir ALL
        except AttributeError:
            return ['ALL']
    
    def validar_reprogramacion_completa(self, reserva, nueva_fecha, motivo: str = "") -> Dict[str, Any]:
        """
        Valida una reprogramación completa aplicando todas las reglas.
        
        Returns:
            Dict con resultado de validación, errores, warnings y datos adicionales.
        """
        from .models import ReglasReprogramacion
        
        self.errores.clear()
        self.warnings.clear()
        
        # Validaciones básicas
        self._validar_fecha_basica(nueva_fecha)
        self._validar_estado_reserva(reserva)
        
        # Aplicar reglas dinámicas
        self._aplicar_reglas_tiempo(nueva_fecha)
        self._aplicar_reglas_limites(reserva)
        self._aplicar_reglas_blackout(nueva_fecha)
        self._aplicar_reglas_servicios(reserva)
        self._aplicar_reglas_capacidad(nueva_fecha, reserva)
        
        # Verificar disponibilidad
        disponibilidad = self._verificar_disponibilidad(nueva_fecha, reserva)
        
        # Calcular penalizaciones
        penalizacion = self._calcular_penalizacion(reserva)
        
        return {
            'valida': len(self.errores) == 0,
            'errores': self.errores,
            'warnings': self.warnings,
            'disponibilidad': disponibilidad,
            'penalizacion': penalizacion,
            'reglas_aplicadas': self._obtener_reglas_aplicadas(),
            'metadatos': {
                'usuario_roles': self.roles,
                'fecha_validacion': timezone.now(),
                'numero_reglas_evaluadas': len(self._obtener_reglas_aplicadas())
            }
        }
    
    def _validar_fecha_basica(self, nueva_fecha):
        """Validaciones básicas de fecha."""
        ahora = timezone.now()
        
        if nueva_fecha <= ahora:
            self.errores.append("No se puede reprogramar a una fecha pasada.")
        
        # Verificar que no sea demasiado lejos en el futuro (2 años)
        if nueva_fecha > ahora + timedelta(days=730):
            self.errores.append("No se puede reprogramar más de 2 años en el futuro.")
    
    def _validar_estado_reserva(self, reserva):
        """Valida el estado de la reserva."""
        if reserva.estado in ['CANCELADA']:
            self.errores.append("No se puede reprogramar una reserva cancelada.")
    
    def _aplicar_reglas_tiempo(self, nueva_fecha):
        """Aplica reglas de tiempo mínimo y máximo."""
        from .models import ReglasReprogramacion
        
        ahora = timezone.now()
        
        # Tiempo mínimo
        for rol in self.roles:
            regla = ReglasReprogramacion.obtener_regla_activa('TIEMPO_MINIMO', rol)
            if regla:
                valor = regla.obtener_valor()
                if isinstance(valor, (int, float)):
                    tiempo_requerido = ahora + timedelta(hours=valor)
                    if nueva_fecha <= tiempo_requerido:
                        mensaje = regla.mensaje_error or f"Debe reprogramar con al menos {valor} horas de anticipación."
                        self.errores.append(mensaje)
                break
        
        # Tiempo máximo
        for rol in self.roles:
            regla = ReglasReprogramacion.obtener_regla_activa('TIEMPO_MAXIMO', rol)
            if regla:
                valor = regla.obtener_valor()
                if isinstance(valor, (int, float)):
                    tiempo_limite = ahora + timedelta(hours=valor)
                    if nueva_fecha > tiempo_limite:
                        mensaje = regla.mensaje_error or f"No puede reprogramar más de {valor/24:.0f} días en el futuro."
                        self.errores.append(mensaje)
                break
    
    def _aplicar_reglas_limites(self, reserva):
        """Aplica reglas de límites de reprogramaciones."""
        from .models import ReglasReprogramacion
        
        # Límite por reserva
        for rol in self.roles:
            regla = ReglasReprogramacion.obtener_regla_activa('LIMITE_REPROGRAMACIONES', rol)
            if regla:
                limite = regla.obtener_valor()
                if isinstance(limite, (int, float)) and reserva.numero_reprogramaciones >= int(limite):
                    mensaje = regla.mensaje_error or f"Ha alcanzado el límite de {limite} reprogramaciones."
                    self.errores.append(mensaje)
                break
        
        # Límite diario (por usuario)
        for rol in self.roles:
            regla = ReglasReprogramacion.obtener_regla_activa('LIMITE_DIARIO', rol)
            if regla and self.usuario:
                limite = regla.obtener_valor()
                if isinstance(limite, (int, float)):
                    hoy = timezone.now().date()
                    from .models import HistorialReprogramacion
                    reprogramaciones_hoy = HistorialReprogramacion.objects.filter(
                        reprogramado_por=self.usuario,
                        created_at__date=hoy
                    ).count()
                    
                    if reprogramaciones_hoy >= int(limite):
                        mensaje = regla.mensaje_error or f"Ha alcanzado el límite diario de {limite} reprogramaciones."
                        self.errores.append(mensaje)
                break
    
    def _aplicar_reglas_blackout(self, nueva_fecha):
        """Aplica reglas de días y horas blackout."""
        from .models import ReglasReprogramacion
        
        # Días blackout
        for rol in self.roles:
            regla = ReglasReprogramacion.obtener_regla_activa('DIAS_BLACKOUT', rol)
            if regla:
                try:
                    dias_blackout = regla.obtener_valor()
                    if isinstance(dias_blackout, list):
                        dia_semana = nueva_fecha.weekday()  # 0=lunes, 6=domingo
                        nombres_dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
                        if nombres_dias[dia_semana] in [d.lower() for d in dias_blackout]:
                            mensaje = regla.mensaje_error or f"No se puede reprogramar en {nombres_dias[dia_semana]}."
                            self.errores.append(mensaje)
                except (ValueError, TypeError):
                    pass
                break
        
        # Horas blackout
        for rol in self.roles:
            regla = ReglasReprogramacion.obtener_regla_activa('HORAS_BLACKOUT', rol)
            if regla:
                try:
                    horas_blackout = regla.obtener_valor()
                    if isinstance(horas_blackout, list):
                        hora_nueva = nueva_fecha.hour
                        if hora_nueva in horas_blackout:
                            mensaje = regla.mensaje_error or f"No se puede reprogramar a las {hora_nueva}:00 horas."
                            self.errores.append(mensaje)
                except (ValueError, TypeError):
                    pass
                break
    
    def _aplicar_reglas_servicios(self, reserva):
        """Aplica reglas específicas de servicios."""
        from .models import ReglasReprogramacion
        
        for rol in self.roles:
            regla = ReglasReprogramacion.obtener_regla_activa('SERVICIOS_RESTRINGIDOS', rol)
            if regla:
                try:
                    servicios_restringidos = regla.obtener_valor()
                    if isinstance(servicios_restringidos, list):
                        servicios_reserva = list(reserva.detalles.values_list('servicio__titulo', flat=True))
                        for servicio in servicios_reserva:
                            if servicio in servicios_restringidos:
                                mensaje = regla.mensaje_error or f"El servicio '{servicio}' tiene restricciones para reprogramar."
                                self.errores.append(mensaje)
                except (ValueError, TypeError):
                    pass
                break
    
    def _aplicar_reglas_capacidad(self, nueva_fecha, reserva):
        """Aplica reglas de capacidad máxima."""
        from .models import ReglasReprogramacion, Reserva
        
        for rol in self.roles:
            regla = ReglasReprogramacion.obtener_regla_activa('CAPACIDAD_MAXIMA', rol)
            if regla:
                try:
                    capacidad_maxima = regla.obtener_valor()
                    if isinstance(capacidad_maxima, (int, float)):
                        # Contar reservas en la nueva fecha
                        reservas_fecha = Reserva.objects.filter(
                            fecha_inicio__date=nueva_fecha.date(),
                            estado__in=['PENDIENTE', 'PAGADA', 'REPROGRAMADA']
                        ).exclude(id=reserva.id).count()
                        
                        if reservas_fecha >= int(capacidad_maxima):
                            mensaje = regla.mensaje_error or f"La fecha alcanzó la capacidad máxima de {capacidad_maxima} reservas."
                            self.errores.append(mensaje)
                except (ValueError, TypeError):
                    pass
                break
    
    def _verificar_disponibilidad(self, nueva_fecha, reserva) -> Dict[str, Any]:
        """Verifica disponibilidad detallada de servicios en la nueva fecha."""
        from .models import Reserva
        
        servicios_ids = list(reserva.detalles.values_list('servicio_id', flat=True))
        
        # Buscar conflictos
        conflictos = Reserva.objects.filter(
            fecha_inicio__date=nueva_fecha.date(),
            estado__in=['PENDIENTE', 'PAGADA', 'REPROGRAMADA'],
            detalles__servicio_id__in=servicios_ids
        ).exclude(id=reserva.id)
        
        return {
            'disponible': not conflictos.exists(),
            'conflictos': conflictos.count(),
            'servicios_conflictivos': list(conflictos.values_list('detalles__servicio__titulo', flat=True))
        }
    
    def _calcular_penalizacion(self, reserva) -> Dict[str, Any]:
        """Calcula penalizaciones por reprogramar."""
        from .models import ReglasReprogramacion
        
        penalizacion_pct = 0
        
        for rol in self.roles:
            regla = ReglasReprogramacion.obtener_regla_activa('DESCUENTO_PENALIZACION', rol)
            if regla:
                valor = regla.obtener_valor()
                if isinstance(valor, (int, float)):
                    penalizacion_pct = valor
                break
        
        penalizacion_monto = 0
        if penalizacion_pct > 0:
            penalizacion_monto = float(reserva.total) * (penalizacion_pct / 100)
        
        return {
            'aplica_penalizacion': penalizacion_pct > 0,
            'porcentaje': penalizacion_pct,
            'monto': penalizacion_monto,
            'total_con_penalizacion': float(reserva.total) + penalizacion_monto
        }
    
    def _obtener_reglas_aplicadas(self) -> List[Dict[str, Any]]:
        """Obtiene información de todas las reglas que se aplicaron."""
        from .models import ReglasReprogramacion
        
        reglas_aplicadas = []
        
        tipos_reglas = [
            'TIEMPO_MINIMO', 'TIEMPO_MAXIMO', 'LIMITE_REPROGRAMACIONES',
            'LIMITE_DIARIO', 'DIAS_BLACKOUT', 'HORAS_BLACKOUT',
            'SERVICIOS_RESTRINGIDOS', 'CAPACIDAD_MAXIMA', 'DESCUENTO_PENALIZACION'
        ]
        
        for tipo_regla in tipos_reglas:
            for rol in self.roles:
                regla = ReglasReprogramacion.obtener_regla_activa(tipo_regla, rol)
                if regla:
                    reglas_aplicadas.append({
                        'tipo': tipo_regla,
                        'rol': rol,
                        'nombre': regla.nombre,
                        'valor': regla.obtener_valor(),
                        'prioridad': regla.prioridad
                    })
                    break
        
        return reglas_aplicadas
    
    @classmethod
    def validar_rapido(cls, reserva, nueva_fecha, usuario=None) -> bool:
        """Validación rápida que solo retorna True/False."""
        validador = cls(usuario)
        resultado = validador.validar_reprogramacion_completa(reserva, nueva_fecha)
        return resultado['valida']
    
    @classmethod
    def obtener_errores_rapido(cls, reserva, nueva_fecha, usuario=None) -> List[str]:
        """Obtiene solo la lista de errores."""
        validador = cls(usuario)
        resultado = validador.validar_reprogramacion_completa(reserva, nueva_fecha)
        return resultado['errores']


class GeneradorRecomendaciones:
    """Genera recomendaciones inteligentes para reprogramaciones."""
    
    @staticmethod
    def sugerir_fechas_alternativas(reserva, fecha_deseada, usuario=None, cantidad=5) -> List[Dict[str, Any]]:
        """
        Sugiere fechas alternativas basadas en las reglas y disponibilidad.
        """
        from datetime import timedelta
        
        validador = ValidadorReprogramacionDinamico(usuario)
        sugerencias = []
        
        # Probar fechas cercanas a la deseada
        for dias_offset in range(-7, 15):  # Una semana antes, dos semanas después
            if dias_offset == 0:
                continue  # Saltar la fecha deseada original
            
            fecha_candidata = fecha_deseada + timedelta(days=dias_offset)
            
            # Probar diferentes horas si es necesario
            for hora_offset in [0, 1, -1, 2, -2]:
                fecha_con_hora = fecha_candidata + timedelta(hours=hora_offset)
                
                resultado = validador.validar_reprogramacion_completa(reserva, fecha_con_hora)
                
                if resultado['valida']:
                    disponibilidad = resultado['disponibilidad']
                    
                    sugerencias.append({
                        'fecha': fecha_con_hora,
                        'disponible': disponibilidad['disponible'],
                        'conflictos': disponibilidad['conflictos'],
                        'penalizacion': resultado['penalizacion'],
                        'score': GeneradorRecomendaciones._calcular_score(fecha_deseada, fecha_con_hora, resultado)
                    })
                    
                    if len(sugerencias) >= cantidad:
                        break
            
            if len(sugerencias) >= cantidad:
                break
        
        # Ordenar por score (mejores primero)
        sugerencias.sort(key=lambda x: x['score'], reverse=True)
        
        return sugerencias[:cantidad]
    
    @staticmethod
    def _calcular_score(fecha_deseada, fecha_candidata, resultado_validacion) -> float:
        """Calcula un score para una fecha candidata."""
        # Penalizar fechas muy lejanas a la deseada
        diferencia_dias = abs((fecha_candidata - fecha_deseada).days)
        score_cercania = max(0, 10 - diferencia_dias)
        
        # Bonus por disponibilidad perfecta
        score_disponibilidad = 5 if resultado_validacion['disponibilidad']['disponible'] else 0
        
        # Penalizar si hay penalizaciones económicas
        score_penalizacion = -2 if resultado_validacion['penalizacion']['aplica_penalizacion'] else 2
        
        return score_cercania + score_disponibilidad + score_penalizacion