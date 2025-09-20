from authz.models import Usuario, Rol

print('=== VERIFICANDO USUARIO DE PRUEBA ===')
user = Usuario.objects.get(email='test@autonoma.edu.bo')
print(f'Usuario: {user.email}')
print(f'Roles actuales: {list(user.roles.values_list("nombre", flat=True))}')

print('\n=== ROLES DISPONIBLES ===')
roles = Rol.objects.all()
for rol in roles:
    print(f'- {rol.nombre}')

print('\n=== ASIGNANDO ROL ADMIN AL USUARIO DE PRUEBA ===')
try:
    rol_admin = Rol.objects.get(nombre='ADMIN')
    user.roles.add(rol_admin)
    print(f'✅ Rol ADMIN asignado a {user.email}')
    print(f'Roles actuales: {list(user.roles.values_list("nombre", flat=True))}')
except Rol.DoesNotExist:
    print('❌ No existe el rol ADMIN')
    print('Creando rol ADMIN...')
    rol_admin = Rol.objects.create(nombre='ADMIN')
    user.roles.add(rol_admin)
    print(f'✅ Rol ADMIN creado y asignado a {user.email}')