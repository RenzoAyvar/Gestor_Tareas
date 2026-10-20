# Plan técnico — SPEC 001

1. Backend: modelo `User` con correo único y password_hash, capa DB async, esquema Pydantic, servicio Auth, router mínimo, JWT de entorno.
2. Frontend: API Fetch, validaciones puras, hook useLogin con token en memoria, LoginForm accesible, App con placeholder Planificador.
3. Tema: hook useTheme, CSS variables en html[data-theme], persistencia únicamente de preferencia.
4. QA: tests de endpoint HTTP con PostgreSQL real de pruebas, tests unitarios frontend/Vitest, Harness de trazabilidad y ejecución reproducible.
5. DevOps: Docker Compose desarrollo; contenedores optimizados prod; PR CI (PostgreSQL service, pytest, Vitest, build); publicación GHCR y despliegue opcional protegido.

## Decisiones y dependencias

- `POST /auth/login` es el contrato único; frontend Vite usa proxy a `backend:8000` en Docker y nginx reverse proxy en producción.
- `DEV_CREATE_TABLES=true` crea tablas solo para demo. No utilizar en producción: implementar migraciones Alembic en la SPEC de hardening.
- Se evita endpoint público de registro. Alta del usuario de demo mediante CLI interactiva, no cuentas hardcodeadas.
- Token solo RAM: un refresh cierra la sesión. Acceso seguro a otras páginas requiere validación JWT en endpoints futuros.
- `SPEC 008` no está implementada: solo placeholder de navegación después del login.
