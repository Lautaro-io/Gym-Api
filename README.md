# GymApi

API REST para la gestión de un gimnasio: socios, roles, perfiles deportivos, ejercicios, rutinas y pagos.

Backend construido con **FastAPI + SQLAlchemy 2** sobre **SQL Server**, con autenticación **JWT** y autorización por roles.

## Características

- Registro y login de usuarios con JWT (OAuth2 password flow).
- Gestión de socios con roles `admin`, `profesor` y `cliente`.
- Asignación de roles y habilitación para entrenar.
- Baja lógica de usuarios (conserva pagos, rutinas e historial).
- Perfiles deportivos por socio (objetivo, nivel, días por semana, lesiones, etc.).
- Catálogo de ejercicios por grupo muscular, con carga masiva desde un script.
- Rutinas asignadas a socios, con ejercicios, series, repeticiones, descansos y orden.
- Registro de pagos e historial por socio.

## Tecnologías

| Componente | Versión / Detalle |
|---|---|
| Python | 3.14 |
| FastAPI | 0.141.1 |
| SQLAlchemy | 2.0.53 |
| SQL Server | vía `pyodbc` + ODBC Driver 18 |
| Pydantic | v2 |
| Autenticación | JWT (`PyJWT`) + hash de contraseñas (`pwdlib`/Argon2) |

## Requisitos

- Python 3.14.
- SQL Server accesible (local o remoto) con el **ODBC Driver 18 for SQL Server** instalado.
- Git.

## Instalación

```bash
git clone https://github.com/Lautaro-io/Gym-Api.git
cd Gym-Api
```

Crear y activar el entorno virtual:

```powershell
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

Instalar dependencias:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Configuración

Copiar el archivo de ejemplo y completar las variables:

```powershell
copy .env.example .env
```

```bash
cp .env.example .env
```

Contenido esperado de `.env`:

```env
DATABASE_URL="mssql+pyodbc://@localhost\SQLEXPRESS/gym_api?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes"
SECRET_KEY="cambia-esta-clave-por-una-segura"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

- `DATABASE_URL`: cadena de conexión de SQLAlchemy a SQL Server.
- `SECRET_KEY`: clave usada para firmar los JWT (usar una clave segura en producción).

## Base de datos

1. Crear una base de datos vacía en SQL Server (por ejemplo `gym_api`).
2. Apuntar `DATABASE_URL` a esa base.
3. Al iniciar la aplicación se crean las tablas faltantes automáticamente (`init_db()` → `create_all`).

> El proyecto no usa migraciones: `create_all` crea tablas nuevas, pero **no modifica tablas existentes**. Si se agrega o cambia una columna, hay que aplicar el `ALTER TABLE` manualmente.

## Ejecución

Desde la raíz del proyecto:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

La API queda disponible en:

- API: http://127.0.0.1:8000
- Documentación interactiva (Swagger): http://127.0.0.1:8000/docs
- Esquema OpenAPI: http://127.0.0.1:8000/openapi.json

## Roles y permisos

| Rol | Alcance |
|---|---|
| `admin` | Acceso total: usuarios, roles, habilitaciones, perfiles deportivos, pagos, ejercicios y rutinas. |
| `profesor` | Puede leer el listado de socios y gestionar ejercicios, rutinas y sus ejercicios. No puede editar usuarios, roles ni pagos. Los `admin` también pasan estos permisos. |
| `cliente` | Acceso a sus propios datos: `GET/PATCH /users/me`, `GET /sport-profiles/me`, `GET /routines/me`, `GET /payment/me`. Puede leer ejercicios. |

### Detalle por operación

- **Usuarios**: lectura (`GET`) para `admin` y `profesor`; escritura, habilitación, cambio de rol y baja solo `admin`.
- **Perfiles deportivos**: escritura y listados solo `admin`; el cliente lee los suyos en `/sport-profiles/me`.
- **Ejercicios**: lectura para cualquier usuario autenticado; alta/edición/baja para `profesor` y `admin`.
- **Rutinas**: alta/edición/baja para `profesor` y `admin`; el cliente consulta las suyas.
- **Pagos**: alta y consultas generales solo `admin`; el cliente consulta su historial en `/payment/me`.

## Endpoints

### Autenticación

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| `POST` | `/auth/register` | Público | Registro de socio. Crea el usuario con rol `cliente` y estado `pendiente_habilitacion`. |
| `POST` | `/auth/login` | Público | Login con form data OAuth2 (`username=<email>`, `password=<clave>`). Devuelve `access_token`. |

### Usuarios

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| `GET` | `/users/me` | Autenticado | Datos del usuario logueado. |
| `PATCH` | `/users/me` | Autenticado | Edita los propios datos (`email`, `name`, `lastname`, `dni`, `phone`). |
| `GET` | `/users` | `profesor` / `admin` | Lista todos los socios. |
| `GET` | `/users/{id}` | `profesor` / `admin` | Detalle de un socio. |
| `PATCH` | `/users/{id}` | `admin` | Edita un socio. |
| `PATCH` | `/users/{id}/habilitar` | `admin` | Habilita al socio para entrenar. |
| `PATCH` | `/users/{id}/rol` | `admin` | Asigna rol (`admin`, `profesor` o `cliente`). No permite cambiar el propio rol. |
| `DELETE` | `/users/{id}` | `admin` | Baja lógica: el usuario pasa a `inactivo` y conserva su historial. |

### Perfiles deportivos

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| `GET` | `/sport-profiles/me` | Autenticado | Perfiles del usuario logueado. |
| `GET` | `/sport-profiles` | `admin` | Lista todos los perfiles. |
| `GET` | `/sport-profiles/{id}` | `admin` | Detalle de un perfil. |
| `POST` | `/sport-profiles` | `admin` | Crea un perfil para un socio. |
| `PATCH` | `/sport-profiles/{id}` | `admin` | Actualiza un perfil. |
| `DELETE` | `/sport-profiles/{id}` | `admin` | Elimina un perfil. |

### Ejercicios

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| `GET` | `/exercises` | Autenticado | Lista ejercicios. Filtro opcional `?muscular_group=pecho`. |
| `GET` | `/exercises/{id}` | Autenticado | Detalle de un ejercicio. |
| `POST` | `/exercises` | `profesor` / `admin` | Crea un ejercicio. Devuelve `409` si el nombre ya existe. |
| `PATCH` | `/exercises/{id}` | `profesor` / `admin` | Actualiza un ejercicio. |
| `DELETE` | `/exercises/{id}` | `profesor` / `admin` | Elimina un ejercicio. |

Grupos musculares válidos: `pecho`, `espalda`, `pierna`, `hombro`, `biceps`, `triceps`, `abdomen`, `gluteo`, `full_body`.

### Rutinas

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| `GET` | `/routines/me` | Autenticado | Rutinas del usuario logueado (con sus ejercicios). |
| `GET` | `/routines` | `profesor` / `admin` | Lista todas las rutinas. |
| `GET` | `/routines/{id}` | Autenticado | Detalle de una rutina con sus ejercicios. |
| `POST` | `/routines` | `profesor` / `admin` | Crea una rutina para un socio. |
| `PATCH` | `/routines/{id}` | `profesor` / `admin` | Actualiza fecha o estado de la rutina. |
| `DELETE` | `/routines/{id}` | `profesor` / `admin` | Elimina una rutina y sus ejercicios. |

#### Ejercicios de una rutina

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| `GET` | `/routines/{routine_id}/exercises` | `profesor` / `admin` | Lista los ejercicios de la rutina. |
| `POST` | `/routines/{routine_id}/exercises` | `profesor` / `admin` | Agrega un ejercicio a la rutina. |
| `PATCH` | `/routines/{routine_id}/exercises/{id}` | `profesor` / `admin` | Actualiza series, repeticiones, descanso, día u orden. |
| `DELETE` | `/routines/{routine_id}/exercises/{id}` | `profesor` / `admin` | Quita un ejercicio de la rutina. |

Campos de un ejercicio de rutina:

```json
{
  "exercise_id": 1,
  "day": "lunes",
  "sets": 4,
  "repetitions": "8-12",
  "position": 1,
  "rest": 90
}
```

- `day`: día de la semana.
- `sets`: cantidad de series.
- `repetitions`: repeticiones (texto, admite rangos como `"8-12"`).
- `position`: orden dentro de la rutina.
- `rest`: descanso en segundos.

### Pagos

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| `GET` | `/payment/me` | Autenticado | Historial de pagos del usuario logueado. |
| `GET` | `/payment` | `admin` | Lista todos los pagos. |
| `GET` | `/payment/{id}` | `admin` | Detalle de un pago. |
| `POST` | `/payment` | `admin` | Registra un pago para un socio. |

Métodos de pago válidos: `tarjeta`, `efectivo`, `transferencia`, `mercado_pago`.

## Ejemplos de uso

### Registro

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "socio@example.com",
    "password": "clave1234",
    "name": "Juan",
    "lastname": "Pérez",
    "dni": "12345678",
    "phone": "1123456789"
  }'
```

### Login

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=socio@example.com&password=clave1234"
```

### Asignar rol de profesor (admin)

```bash
curl -X PATCH http://127.0.0.1:8000/users/5/rol \
  -H "Authorization: Bearer <token-admin>" \
  -H "Content-Type: application/json" \
  -d '{"rol": "profesor"}'
```

### Crear una rutina y agregarle un ejercicio

```bash
curl -X POST http://127.0.0.1:8000/routines \
  -H "Authorization: Bearer <token-profesor>" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 5, "date_generated": "2026-10-23", "state": true}'
```

```bash
curl -X POST http://127.0.0.1:8000/routines/1/exercises \
  -H "Authorization: Bearer <token-profesor>" \
  -H "Content-Type: application/json" \
  -d '{"exercise_id": 1, "day": "lunes", "sets": 4, "repetitions": "8-12", "position": 1, "rest": 90}'
```

## Primer administrador

El registro crea siempre usuarios `cliente`. Para designar al primer administrador hay que actualizarlo directamente en la base:

```sql
UPDATE [user] SET rol = 'ADMIN' WHERE email = 'admin@example.com';
```

A partir de ahí, el resto de los roles se asignan con `PATCH /users/{id}/rol`.

## Carga inicial de ejercicios

El script `seed_exercises.py` carga un catálogo inicial de ejercicios (47 ejercicios en los 9 grupos musculares). Es **idempotente**: si se ejecuta varias veces, no duplica los existentes.

```powershell
.\.venv\Scripts\python.exe seed_exercises.py
```

Salida esperada:

```
Ejercicios creados: 47 | saltados (ya existían): 0
```

## Estructura del proyecto

```
GymApi/
├── controllers/      # Routers de FastAPI (capa HTTP)
├── services/         # Lógica de negocio y validaciones
├── repositories/     # Acceso a datos (SQLAlchemy)
├── models/           # Modelos ORM
├── schemas/          # Schemas Pydantic (entrada/salida)
├── security/         # JWT y permisos por rol
├── db.py             # Conexión, sesión e init_db()
├── main.py           # Aplicación FastAPI y registro de routers
├── seed_exercises.py # Carga inicial de ejercicios
├── requirements.txt
└── .env.example
```

Arquitectura en capas: `controllers → services → repositories → models`. Los schemas se usan en services y controllers; los repositories solo trabajan con entidades ORM.

## Notas técnicas

- **Enums**: SQLAlchemy guarda los enums por *nombre* (`ADMIN`, `PENDIENTE_HABILITACION`, `PECHO`), mientras que la API los expone por *valor* en minúscula (`admin`, `pendiente_habilitacion`, `pecho`). En SQL manual hay que usar los nombres en mayúscula.
- **`user` es palabra reservada**: en SQL crudo debe citarse como `[user]`.
- **Baja de usuarios**: `DELETE /users/{id}` no elimina el registro; lo pasa a `inactivo` para conservar pagos y rutinas. Se puede reactivar con `PATCH /users/{id}/habilitar`.
- **Sin migraciones**: `create_all` no altera tablas existentes; los cambios de esquema se aplican a mano.
- **CORS**: habilitado para todos los orígenes (configuración de desarrollo).
- El proyecto no incluye todavía una suite de tests automatizados.
