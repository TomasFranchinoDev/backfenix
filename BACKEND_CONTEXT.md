# Fenix B2B API (Backend)

## 1. Introducción
Backend REST para una plataforma B2B de ventas por catálogo, gestión de órdenes y administración de productos.

El servicio expone una API construida con Django + Django Ninja, con autenticación JWT de Supabase para clientes y control de permisos de administrador para endpoints internos.

## 2. Tecnologías Utilizadas
- 🐍 Python 3
- 🌐 Django 4.2
- ⚡ Django Ninja (API REST + OpenAPI)
- 🔐 PyJWT (validación de tokens)
- ☁️ Supabase Auth (origen de identidad JWT)
- 🗄️ PostgreSQL (entorno productivo mediante `DATABASE_URL`) / SQLite (desarrollo local)
- 🔄 django-cors-headers
- ⚙️ python-dotenv
- 🔌 dj-database-url

## 3. Instalación y Configuración
### Requisitos
- Python 3.10+
- pip
- Base de datos PostgreSQL (recomendada para producción)

### Pasos
```bash
# 1) Entrar al backend
cd backend

# 2) Crear entorno virtual
python -m venv venv

# 3) Activar entorno (PowerShell)
.\venv\Scripts\Activate.ps1

# 4) Instalar dependencias
pip install django django-ninja django-cors-headers python-dotenv dj-database-url PyJWT psycopg2-binary

# 5) Migraciones
python manage.py migrate

# 6) Ejecutar servidor
python manage.py runserver
```

### Variables de entorno (`.env`)
> Nota: No existe un `.env.example` versionado en el repositorio. Este ejemplo se documenta como escenario recomendado.

```env
SECRET_KEY=django-insecure-cambiar-en-produccion
DEBUG=True
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DBNAME
SUPABASE_JWT_SECRET=tu_jwt_secret_de_supabase
```

### URLs base
- API base: `http://localhost:8000/api/`
- Documentación Swagger UI (Django Ninja): `http://localhost:8000/api/docs`
- OpenAPI JSON: `http://localhost:8000/api/openapi.json`

## 4. Endpoints de la API
Formato de errores de negocio en este backend: `{"detail": "mensaje"}`.

Además, Django Ninja puede responder con errores de validación (`422`) cuando el payload no cumple el esquema.

## GET /api/catalog/productos
Descripción: Lista productos activos del catálogo, incluyendo imágenes.

Autenticación: No.

Respuesta exitosa (`200`):
```json
[
  {
    "id": "7c790c2d-20f2-438c-84f5-5b94f6b39851",
    "nombre": "Bolso Premium",
    "descripcion": "Bolso de cuero",
    "precio_base": "14990.00",
    "sku": "BOL-001",
    "esquema_opciones": {
      "color": ["negro", "marron"]
    },
    "imagenes": [
      {
        "id": "96f8ff35-88c7-45b9-9623-03f7046dc6ff",
        "url": "https://cdn.site/img1.jpg",
        "es_principal": true,
        "orden": 0
      }
    ]
  }
]
```

Códigos de error:
```json
{
  "detail": "Error interno"
}
```
HTTP: `500` (si ocurre error no controlado)

## GET /api/users/me
Descripción: Retorna el perfil del cliente autenticado.

Autenticación: Sí, Bearer JWT (Supabase).

Headers:
```http
Authorization: Bearer <token>
```

Respuesta exitosa (`200`):
```json
{
  "id": "2b973a80-486c-4db6-8d5a-3119a7ea4d95",
  "email": "cliente@empresa.com",
  "nombre_completo": "Ana Perez",
  "telefono": "+56911111111",
  "empresa": "Comercial Andes",
  "creado_en": "2026-04-19T12:00:00Z"
}
```

Códigos de error:
```json
{
  "detail": "Token inválido"
}
```
HTTP: `401`

## POST /api/orders/crear
Descripción: Crea una orden para el cliente autenticado a partir de un carrito.

Autenticación: Sí, Bearer JWT (Supabase).

Payload de entrada:
```json
{
  "items": [
    {
      "producto_id": "7c790c2d-20f2-438c-84f5-5b94f6b39851",
      "cantidad": 2,
      "variantes": {
        "color": "negro",
        "manija": "cordon"
      }
    }
  ],
  "notas_cliente": "Entregar en horario AM"
}
```

Respuesta exitosa (`200`):
```json
{
  "codigo_orden": "ORD-A1B2C3",
  "total": "29980.00"
}
```

Códigos de error:
```json
{
  "detail": "La orden debe incluir al menos un item"
}
```
HTTP: `400`

```json
{
  "detail": "Producto inválido o inactivo: <uuid>"
}
```
HTTP: `400`

```json
{
  "detail": "El token ha expirado"
}
```
HTTP: `401`

## GET /api/orders/mis-ordenes
Descripción: Lista órdenes del cliente autenticado, ordenadas por fecha descendente.

Autenticación: Sí, Bearer JWT (Supabase).

Respuesta exitosa (`200`):
```json
[
  {
    "codigo_orden": "ORD-A1B2C3",
    "estado": "PENDIENTE",
    "total": "29980.00",
    "creado_en": "2026-04-19T12:00:00+00:00"
  }
]
```

Códigos de error:
```json
{
  "detail": "Token inválido"
}
```
HTTP: `401`

## POST /api/admin/productos
Descripción: Crea un producto nuevo (incluye imágenes y esquema de opciones).

Autenticación: Sí, Bearer JWT de usuario administrador.

Payload de entrada:
```json
{
  "nombre": "Mochila Urbana",
  "descripcion": "Modelo 2026",
  "precio_base": "21990.00",
  "sku": "MOCH-2026",
  "esquema_opciones": {
    "color": ["negro", "azul"]
  },
  "activo": true,
  "imagenes": [
    {
      "url": "https://cdn.site/mochila-1.jpg",
      "es_principal": true,
      "orden": 0
    }
  ],
  "imagen_principal_url": "https://cdn.site/mochila-1.jpg"
}
```

Respuesta exitosa (`200`):
```json
{
  "id": "bf49ea4f-4cde-4a89-a4d8-20c19af314fc",
  "nombre": "Mochila Urbana",
  "descripcion": "Modelo 2026",
  "precio_base": "21990.00",
  "sku": "MOCH-2026",
  "esquema_opciones": {
    "color": ["negro", "azul"]
  },
  "activo": true,
  "imagenes": [
    {
      "id": "54be3f63-f5ec-45d7-8038-dcbe15d54865",
      "url": "https://cdn.site/mochila-1.jpg",
      "es_principal": true,
      "orden": 0
    }
  ]
}
```

Códigos de error:
```json
{
  "detail": "Acceso denegado. Se requieren permisos de administrador."
}
```
HTTP: `403`

## PUT /api/admin/productos/{producto_id}
Descripción: Actualiza campos de producto y/o su set de imágenes.

Autenticación: Sí, Bearer JWT de usuario administrador.

Payload de entrada (parcial):
```json
{
  "precio_base": "23990.00",
  "imagenes": [
    {
      "url": "https://cdn.site/mochila-2.jpg",
      "es_principal": true,
      "orden": 0
    }
  ]
}
```

Respuesta exitosa (`200`): Producto actualizado (mismo formato de `POST /api/admin/productos`).

Códigos de error:
```json
{
  "detail": "Producto no encontrado"
}
```
HTTP: `404`

```json
{
  "detail": "No se enviaron campos para actualizar"
}
```
HTTP: `400`

```json
{
  "detail": "La imagen principal indicada no existe en el producto"
}
```
HTTP: `400`

## DELETE /api/admin/productos/{producto_id}
Descripción: Baja lógica del producto (`activo=false`).

Autenticación: Sí, Bearer JWT de usuario administrador.

Respuesta exitosa (`200`):
```json
{
  "detail": "Producto desactivado correctamente"
}
```

Códigos de error:
```json
{
  "detail": "Producto no encontrado"
}
```
HTTP: `404`

## GET /api/admin/ordenes
Descripción: Lista todas las órdenes para gestión administrativa, incluyendo datos de cliente.

Autenticación: Sí, Bearer JWT de usuario administrador.

Respuesta exitosa (`200`):
```json
[
  {
    "id": "0abfdf20-bf5a-4128-9e87-d2a43e2b2980",
    "codigo_orden": "ORD-A1B2C3",
    "estado": "PENDIENTE",
    "total": "29980.00",
    "detalle_carrito": {
      "items": []
    },
    "notas_cliente": "Entregar en horario AM",
    "creado_en": "2026-04-19T12:00:00+00:00",
    "cliente": {
      "id": "2b973a80-486c-4db6-8d5a-3119a7ea4d95",
      "email": "cliente@empresa.com",
      "nombre_completo": "Ana Perez",
      "telefono": "+56911111111",
      "empresa": "Comercial Andes"
    }
  }
]
```

Códigos de error:
```json
{
  "detail": "Acceso denegado. Se requieren permisos de administrador."
}
```
HTTP: `403`

## PATCH /api/admin/ordenes/{orden_id}/estado
Descripción: Cambia el estado de una orden existente.

Autenticación: Sí, Bearer JWT de usuario administrador.

Payload de entrada:
```json
{
  "estado": "EN_PREPARACION"
}
```

Respuesta exitosa (`200`):
```json
{
  "detail": "Estado de la orden actualizado correctamente"
}
```

Códigos de error:
```json
{
  "detail": "Orden no encontrada"
}
```
HTTP: `404`

```json
{
  "detail": "Estado inválido. Usa uno de: CANCELADA, DESPACHADO, EN_PREPARACION, LISTO, PENDIENTE"
}
```
HTTP: `400`

## 5. Estructura de Directorios
```text
backend/
├─ manage.py
├─ .env
├─ config/
│  ├─ settings.py
│  ├─ urls.py
│  ├─ api.py
│  └─ admin_api.py
├─ users/
│  ├─ models.py
│  ├─ api.py
│  ├─ auth.py
│  └─ schemas.py
├─ catalog/
│  ├─ models.py
│  ├─ api.py
│  └─ schemas.py
└─ orders/
   ├─ models.py
   ├─ api.py
   └─ schemas.py
```

## 6. Base de Datos
Esquema principal orientado a catálogo y órdenes:

- `Cliente`:
  - PK UUID alineada con `auth.users` de Supabase (`id`)
  - Datos de negocio (`email`, `nombre_completo`, `telefono`, `empresa`)
  - Flag de autorización `es_admin`

- `Producto`:
  - PK UUID
  - Información comercial (`nombre`, `descripcion`, `precio_base`, `sku`, `activo`)
  - Campo JSON `esquema_opciones` para variantes dinámicas

- `ProductoImagen`:
  - PK UUID
  - FK a `Producto` (1:N)
  - URL de imagen, prioridad (`orden`) y bandera `es_principal`

- `Orden`:
  - PK UUID
  - Código legible `ORD-XXXXXX` único
  - FK `cliente` (protege eliminación)
  - Estado del flujo (`PENDIENTE`, `EN_PREPARACION`, `LISTO`, `DESPACHADO`, `CANCELADA`)
  - Snapshot de carrito en JSON (`detalle_carrito`) para trazabilidad
  - Total monetario y notas del cliente

### Relación principal
- Un `Cliente` puede tener muchas `Orden`.
- Un `Producto` puede tener muchas `ProductoImagen`.
- Las órdenes guardan un snapshot JSON de productos/variantes para mantener historial aunque el catálogo cambie.

---

### Supuestos documentados
- Dependencias instaladas por `pip` al no existir un `requirements.txt` en el repositorio.
- Ejemplo de `.env` documentado por ausencia de `.env.example` versionado.
- Formato de errores genéricos (`500`) y de validación (`422`) basado en comportamiento estándar de Django Ninja.
