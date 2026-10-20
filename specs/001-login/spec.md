# SPEC 001 — Sistema de Login (orientada a IA)

## 1. Metadatos y Tech Stack

**Estado:** Propuesta de referencia; aprobar en equipo antes de producción.  
**Objetivo:** autenticar con correo y contraseña contra PostgreSQL, emitir JWT utilizado por el frontend en funcionalidades posteriores. Incluye tema dark/light. En esta iteración, el Planificador de Visitas (SPEC 008) es una **pantalla placeholder**; no se implementa la funcionalidad del planificador.

**Backend:** Python 3.11, FastAPI 0.115.6, SQLAlchemy 2.0.36 + asyncpg, PostgreSQL 16, passlib[bcrypt] 1.7.4, python-jose 3.3.0, Pydantic 2.10.4, pytest 8.3.4. Contenedor `backend`.

**Frontend:** React 18.3.1, JavaScript/JSX, Vite 5.4, TailwindCSS 3.4, Fetch API (sin axios), Vitest 2.1.9. Contenedor `frontend`.

## 2. Archivos Involucrados (Rutas / Paths)

**Para tareas que cambian la funcionalidad del login**, la IA solo puede editar las siguientes rutas. El **scaffolding inicial** (package.json, FastAPI main, DB, Docker, CI/Harness, tests UI y el placeholder de planificador) se creó como tarea separada y documentada; su existencia **no habilita cambios arbitrarios** durante un cambio de login.

**Backend:**
- `[EDITAR]` `backend/app/api/auth.py` — POST /auth/login, sin lógica de negocio.
- `[EDITAR]` `backend/app/models/schemas.py` — LoginRequest/LoginResponse.
- `[EDITAR]` `backend/app/services/auth_service.py` — busca usuario, verifica bcrypt, JWT.
- `[EDITAR]` `backend/app/core/security.py` — bcrypt/JWT.
- `[NUEVO]` `backend/tests/test_auth_endpoint.py` — integración HTTP contra PostgreSQL de pruebas.

**Frontend:**
- `[EDITAR]` `frontend/src/api/authApi.js` — fetch y AuthError.
- `[EDITAR]` `frontend/src/hooks/useLogin.js` — estado/sesión/login/logout.
- `[EDITAR]` `frontend/src/validation/validateLogin.js` — validaciones.
- `[EDITAR]` `frontend/src/components/LoginForm.jsx` — formulario.
- `[EDITAR]` `frontend/src/hooks/useTheme.js`, `frontend/src/components/ThemeToggle.jsx`, `frontend/src/index.css` — tema.

## 3. Flujo del Sistema

```mermaid
sequenceDiagram
    participant UI as frontend/LoginForm.jsx
    participant Service as frontend/authApi.js
    participant API as backend/auth.py
    participant DB as PostgreSQL users
    UI->>UI: validateLogin(correo, password)
    UI->>Service: login({correo, password})
    Service->>API: POST /auth/login
    API->>DB: buscar correo normalizado
    DB-->>API: password_hash
    API->>API: validar bcrypt
    alt Éxito
        API-->>Service: 200 {correo, token, token_type}
        Service-->>UI: JWT solo en memoria; mostrar Planificador placeholder (SPEC 008)
    else Error
        API-->>Service: 401
        Service-->>UI: mostrar mensaje genérico
    end
```

## 4. Reglas de Negocio (Business Logic)

**Frontend:**
- Ambos campos obligatorios: `El correo es obligatorio.` / `La contraseña es obligatoria.`
- Espacios en correo: `El correo no debe contener espacios en blanco.`
- Formato inválido: `Ingresá un correo válido.`
- No llamar al backend si existen errores de formulario.
- Botón `Iniciar sesión`; al enviar `Iniciando sesión…`, deshabilitado.

**Backend:**
- Body sin `correo` / `password`, campo vacío, o correo con cualquier carácter de espacio en blanco → 422.
- El correo se normaliza con `strip().lower()` para consulta tras validar que la entrada no contiene espacios. Se resuelve así la tensión entre "normalizar" y "rechazar espacios": **el valor enviado con espacios se rechaza**, y la normalización de email válido sigue aplicándose.
- Bcrypt valida contraseña; `password_hash` nunca sale de la API.
- Mismo 401 para correo no existente y contraseña incorrecta, sin revelar cuál falló.

**JWT:** firmado con `JWT_SECRET` desde entorno, HS256; `JWT_EXPIRE_MINUTES` predeterminado 60. El token en frontend **solo en memoria**, no en localStorage, sessionStorage ni cookies. Se pierde al recargar (comportamiento esperado de esta iteración).

**Errores UI** (no mostrar errores crudos del backend):

| Situación | Mensaje |
|---|---|
| Error de red | `No se pudo conectar con el servidor.` |
| HTTP 400 / 401 | `Correo o contraseña incorrectos.` |
| Otro error | `No se pudo iniciar sesión. Intentá de nuevo.` |

**Tema:** CSS variables en `index.css`, `data-theme` en `<html>`. Persistir `localStorage["practica-1:theme"]`; sin preferencia usar `prefers-color-scheme`. No guardar JWT con la preferencia.

## 5. Contrato API

**POST** `/auth/login`, `Content-Type: application/json`.

Request:
```json
{"correo":"admin@practica.com","password":"admin123"}
```

200:
```json
{"correo":"admin@practica.com","token":"eyJhbGciOiJIUzI1Ni...","token_type":"bearer"}
```

401:
```json
{"detail":"Correo o contraseña incorrectos."}
```

422: detalle de validación estándar FastAPI (`detail: [...]`, campo `loc`, `msg`, `type`). Ejemplo ilustrativo del campo correo:
```json
{"detail":[{"loc":["body","correo"],"msg":"Value error, El correo no debe contener espacios en blanco.","type":"value_error"}]}
```

Este último ejemplo muestra el formato conceptual: FastAPI/Pydantic pueden incluir datos adicionales en cada elemento y cambiar serialización de detalles.

## 6. Instrucciones de Ejecución para Agentes

1. `backend`: mantener auth router/service cumpliendo contrato.
2. `frontend`: enviar `{correo,password}`, consumir `{correo,token}` y token_type.
3. `frontend`: LoginForm con Tailwind, errores por campo bajo inputs; error general con `role="alert"`.
4. `qa`: pruebas de respuesta 200, 401 por usuario inexistente, 401 contraseña inválida, 422 por campos ausentes y correo con espacios; UI sin red cuando input inválido.
5. `devops`: garantizar variables env, docker/CI/Harness y protección de secretos.

### Criterios de aceptación (IDs de trazabilidad)

- **AC-001**: credenciales correctas permiten acceso al placeholder del Planificador de Visitas (la implementación del planificador es SPEC 008).
- **AC-002**: contraseña incorrecta muestra `Correo o contraseña incorrectos.`.
- **AC-003**: campos vacíos presentan errores sin llamar al backend.
- **AC-004**: tema dark/light sobrevive a recarga.
- **AC-005**: username inexistente no revela existencia y devuelve 401.
- **AC-006**: body inválido o correo con espacios devuelve 422.
- **AC-007**: token JWT firmado HS256, expira en 60 minutos y se guarda solo en memoria del frontend.
