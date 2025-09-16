# API Contract — Reservas

Este documento reúne los endpoints, cuerpos de petición y respuestas de la API relacionados con el caso de uso "Reserva", listo para ser consumido por el frontend.

Base URL: `/api`
Autenticación: JWT — enviar encabezado `Authorization: Bearer <access_token>` en todas las peticiones que lo requieran.

## Autenticación

- POST `/api/auth/login/`
  - Request:
    ```json
    {
      "email": "cliente@example.com",
      "password": "Secret123"
    }
    ```
  - Response 200:
    ```json
    {
      "access": "<jwt_access_token>",
      "refresh": "<jwt_refresh_token>"
    }
    ```

- POST `/api/auth/refresh/`
  - Request:
    ```json
    { "refresh": "<jwt_refresh_token>" }
    ```
  - Response 200:
    ```json
    { "access": "<new_access_token>" }
    ```

## Endpoints de Reservas

Todas requieren `Authorization: Bearer <access>` y retornan JSON.

- Permisos:
  - `ADMIN`, `OPERADOR`: ven todas las reservas.
- Response 200 (lista paginada):
  ```json
  [
    {
      "id": 12,
      "usuario": {"id": 3, "nombres": "Juan", "apellidos":"Perez", "email":"juan@x"},
      "fecha_inicio": "2025-09-20T09:00:00Z",
      "estado": "PENDIENTE",
      "cupon": null,
      "total": "120.00",
      "moneda": "BOB",
      "detalles": [
        {"servicio":5,"tipo":"TOUR","titulo":"City Tour","cantidad":2,"precio_unitario":"60.00","fecha_servicio":"2025-09-20T09:00:00Z"}
      ],
      "acompanantes": [],
      "created_at": "2025-09-01T08:00:00Z",
      "updated_at": "2025-09-01T08:00:00Z"
    }
  ]
  ```

## Crear reserva

- POST `/api/reservas/`
- Roles permitidos: `CLIENTE`, `ADMIN`, `OPERADOR`.
- Body (ejemplo):
  ```json
  {
    "fecha_inicio": "2025-09-20T09:00:00Z",
    "cupon": null,
    "total": "120.00",
    "moneda": "BOB",
    "detalles": [
      {"servicio": 5, "cantidad": 2, "precio_unitario": "60.00", "fecha_servicio": "2025-09-20T09:00:00Z"}
    ]
  }
  ```
- Notas:
  - Si el rol es `CLIENTE`, `usuario` será establecido desde `request.user` y no puede ser enviado en el body (es `read_only`).
  - `acompanantes` no es aceptado en este serializer por defecto; crear acompañantes y asociarlos requiere llamadas separadas o usar el payload anidado de creación (`acompanantes`) si el backend lo acepta.
  - Response 201: objeto `Reserva` creado.

## Obtener detalle de reserva

- GET `/api/reservas/{id}/`
- Response 200: objeto `Reserva` (igual estructura que en el listado, con `detalles` y `acompanantes`).

## Actualizar reserva

- PATCH `/api/reservas/{id}/` (o PUT)
- Permisos: solo `ADMIN` y `OPERADOR` pueden actualizar.
- Nota: `estado` y `usuario` son `read_only` en el serializer. Para cambio de estado se recomienda implementar actions dedicadas en backend.

## Eliminar reserva

- DELETE `/api/reservas/{id}/`
- Permisos: solo `ADMIN`.

## Acciones de estado (nuevas)

- POST `/api/reservas/{id}/cancelar/` -> marca `estado = "CANCELADA"`.
  - Permisos: `ADMIN`, `OPERADOR`, o `CLIENTE` (si es su propia reserva).
  - Response 200: objeto `Reserva` actualizado.

- POST `/api/reservas/{id}/pagar/` -> marca `estado = "PAGADA"`.
  - Permisos: `ADMIN`, `OPERADOR`, o `CLIENTE` (si es su propia reserva).
  - Response 200: objeto `Reserva` actualizado.

- POST `/api/reservas/{id}/reprogramar/` -> acepta `{ "fecha_inicio": "ISO_DATETIME" }` y marca `estado = "REPROGRAMADA"`.
  - Permisos: `ADMIN`, `OPERADOR`, o `CLIENTE` (si es su propia reserva).
  - Request example:
    ```json
    { "fecha_inicio": "2025-09-22T10:00:00Z" }
    ```
  - Response 200: objeto `Reserva` actualizado.

## Acompañantes

1) Crear acompañante
- POST `/api/acompanantes/`
- Body (ejemplo):
  ```json
  {
    "documento": "12345678",
    "nombre": "Ana",
    "apellido": "Gomez",
    "fecha_nacimiento": "1990-04-05",
    "nacionalidad": "Bolivia",
    "email": "ana@example.com",
    "telefono": "71111111"
  }
  ```
- Response 201: objeto `Acompanante` con `id`.

2) Obtener acompañante
- GET `/api/acompanantes/{id}/`

## Asociar Acompañante a Reserva (ReservaAcompanante)

- POST `/api/reserva-acompanantes/`
- Body ejemplo:
  ```json
  {
    "reserva": 13,
    "acompanante": 7,
    "estado": "CONFIRMADO",
    "es_titular": true
  }
  ```
- Note: El sistema impone una restricción para que solo exista un `es_titular=true` por reserva.

- Añadir endpoints/actions para cambiar `estado` (pagar, cancelar, reprogramar). Ejemplos:
  - POST `/api/reservas/{id}/cancelar/`
  - POST `/api/reservas/{id}/pagar/`
  - POST `/api/reservas/{id}/reprogramar/` (aceptar nueva `fecha_inicio`)
-- Añadir filtros en `ReservaViewSet` por `estado`, `fecha_inicio` y búsqueda por `acompanante.documento`.

## Ejemplo de flujo completo (cliente)
1. Login -> obtener `access`.
2. Crear/seleccionar acompañante -> POST `/api/acompanantes/`.
3. Crear reserva -> POST `/api/reservas/` con `detalles`.
4. Asociar acompañante a reserva -> POST `/api/reserva-acompanantes/`.
5. (Opcional) Pagar / Cambiar estado -> (accion por implementar)
---

- O implemento en backend las `actions` recomendadas (p.ej. `cancelar`, `pagar`).

Indica cuál opción prefieres.