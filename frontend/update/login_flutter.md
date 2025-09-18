# Registro de Usuario desde Flutter

## Endpoint de Registro

- **URL:**  
  - `POST /api/auth/register/`  
  - Alias: `POST /api/auth/registro/`
- **Método:** `POST`
- **Headers:**  
  - `Content-Type: application/json`

### Payload (JSON)

```json
{
  "nombres": "Ana",
  "apellidos": "Gomez",
  "email": "ana@example.com",
  "password": "SecretPass123",
  "password_confirm": "SecretPass123",
  "telefono": "71111111",
  "fecha_nacimiento": "1990-01-01",
  "genero": "F",
  "documento_identidad": "12345678",
  "pais": "BO"
}
```
- **Campos obligatorios:**  
  - `nombres`, `apellidos`, `email`, `password`, `password_confirm`, `telefono`
- **Notas:**  
  - `password` y `password_confirm` deben coincidir.
  - El rol asignado por defecto es `CLIENTE`.

### Respuesta exitosa (`201 Created`)

```json
{
  "access": "<JWT_ACCESS_TOKEN>",
  "refresh": "<JWT_REFRESH_TOKEN>",
  "usuario_id": 123
}
```

### Respuesta de error (`400 Bad Request`)

- Si el email ya existe o hay error de validación:
```json
{
  "email": ["usuario con este email ya existe."],
  "password": ["Las contraseñas no coinciden."]
}
```

---

## Ejemplo de solicitud en Flutter (Dart, usando http)

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<void> registrarUsuario() async {
  final url = Uri.parse('http://<TU_IP_LOCAL>:8000/api/auth/register/');
  final response = await http.post(
    url,
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      "nombres": "Ana",
      "apellidos": "Gomez",
      "email": "ana@example.com",
      "password": "SecretPass123",
      "password_confirm": "SecretPass123",
      "telefono": "71111111",
      "fecha_nacimiento": "1990-01-01",
      "genero": "F",
      "documento_identidad": "12345678",
      "pais": "BO"
    }),
  );

  if (response.statusCode == 201) {
    final data = jsonDecode(response.body);
    print('Registro exitoso. Token: \\${data["access"]}');
  } else {
    print('Error: \\${response.body}');
  }
}
```
- Cambia `<TU_IP_LOCAL>` por la IP de tu servidor backend.

---

## Consideraciones

- El usuario queda autenticado automáticamente tras registrarse (recibe tokens JWT).
- Si el email ya existe, se devuelve error.
- El registro es seguro: las contraseñas se almacenan hasheadas.
- El endpoint está documentado y es estable.
