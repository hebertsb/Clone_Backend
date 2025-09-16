from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.nombre

class UsuarioManager(BaseUserManager):
    def create_user(self, usuario, correo, nombre, apellido, contraseña=None, **extra_fields):
        if not usuario:
            raise ValueError('El campo usuario es obligatorio')
        if not correo:
            raise ValueError('El campo correo es obligatorio')
        correo = self.normalize_email(correo)
        user = self.model(
            usuario=usuario,
            correo=correo,
            nombre=nombre,
            apellido=apellido,
            **extra_fields
        )
        user.set_password(contraseña)
        user.save(using=self._db)
        return user

    def create_superuser(self, usuario, correo, nombre, apellido, contraseña=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('estado', 'ACTIVO')
        return self.create_user(usuario, correo, nombre, apellido, contraseña, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    ESTADOS = (("ACTIVO","ACTIVO"),("INACTIVO","INACTIVO"),("BLOQUEADO","BLOQUEADO"))
    nombres = models.CharField(max_length=150)
    apellidos = models.CharField(max_length=150)
    email = models.EmailField(max_length=254, unique=True)
    telefono = models.CharField(max_length=25, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    genero = models.CharField(max_length=1, choices=(('M','Masculino'),('F','Femenino')), blank=True, null=True)
    documento_identidad = models.CharField(max_length=30, blank=True, null=True)
    pais = models.CharField(max_length=50, blank=True, null=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default="ACTIVO")
    roles = models.ManyToManyField(Rol, related_name="usuarios", blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombres', 'apellidos']

    objects = UsuarioManager()

    def __str__(self):
        return f"{self.nombres} {self.apellidos} <{self.email}>"
