# Evaluación 2 — SDD + Harness Engineering + Codex multiagente

Proyecto de referencia de **login completo**: React 18 + Vite + Tailwind, FastAPI + SQLAlchemy async + PostgreSQL, JWT en memoria y dark/light.

## Arquitectura de trabajo

- `specs/<módulo>/<nombre>.scps`: especificación compacta por módulo (máximo 150 líneas) y `traceability.json` asociado.
- `AGENTS.md` + `.codex/agents/`: orquestación y roles frontend/backend/QA/DevOps.
- `harness/`: controles de calidad, scripts reproducibles y políticas (incluye CI GitHub Actions).
- `frontend/`, `backend/`: implementación real.
- `.github/workflows/ci.yml`: valida cada PR. `cd.yml`: publica imágenes en GHCR y permite desplegar con aprobación y configuración del servidor.

## Requisitos

- Para todo con contenedores: Docker Desktop + Docker Compose.
- Para usar agentes: Codex instalado, autenticado y con soporte de subagentes.
- Para GitHub: repositorio propio con permisos de GitHub Actions.

## Arrancar con Docker (Windows PowerShell)

```powershell
cd 'D:\proyect\evaluacion 2'
powershell -ExecutionPolicy Bypass -File .\scripts\setup-windows.ps1
# Crea .env (DB), backend/.env (JWT), frontend/.env (Vite) y verifica el lockfile.
docker compose -f docker-compose.yml up --build -d
```

- Web: http://localhost:5173
- API Docs: http://localhost:8000/docs
- Salud API: http://localhost:8000/health
- La base y tablas **solo se crean automáticamente para desarrollo** (`DEV_CREATE_TABLES=true`). Para producción se necesitan migraciones/versionado de esquema.
- El proyecto no contiene usuarios ni contraseñas por defecto.

### Archivos de entorno

- `.env`: únicamente `POSTGRES_USER`, `POSTGRES_PASSWORD` y `POSTGRES_DB`.
- `backend/.env`: `JWT_SECRET`, expiración y creación de tablas en desarrollo.
- `frontend/.env`: destino del proxy Vite para ejecución local.

Los tres archivos reales están ignorados por Git. Sus plantillas `.env.example` sí se versionan.

### Crear un usuario de prueba

Con los contenedores arriba (comando interactivo, no guarda la contraseña en el repositorio):

```powershell
docker compose -f docker-compose.yml exec backend python -m scripts.create_user --correo admin@practica.com
```

El comando solicita una contraseña de forma segura. Después entra desde la interfaz con ese correo y la contraseña que hayas elegido. El JSON de la SPEC que menciona `admin123` es **solo un ejemplo de contrato**, no una cuenta preparada.

Abre http://localhost:5173 y usa el mismo correo y contraseña ingresados en el comando. No existe registro público ni usuario predeterminado.

### Detener los servicios

```powershell
docker compose -f docker-compose.yml down
# No ejecutes `down -v` salvo que quieras borrar datos de PostgreSQL.
```

## Validar con el Harness

Comprobaciones de archivos/contrato (sin instalar dependencias):

```powershell
python harness/scripts/verify.py --scope spec
```

Comprobación completa (requiere Python 3.11, dependencias de backend, Node 20 y paquetes de frontend):

```powershell
python harness/scripts/verify.py --scope all
```

Para backend sin Docker, configurar `DATABASE_URL` y ejecutar Uvicorn con `--env-file backend/.env`. Para frontend, ejecutar `npm ci` en `frontend/`; Vite carga `frontend/.env`.

## Colaboración GitHub

1. Crear repositorio vacío en GitHub y subir el contenido (`git init`, `git add .`, `git commit`, conectar `origin`, `git push`).
2. Mantener versionado `frontend/package-lock.json` y usar `npm ci`.
3. Cada integrante trabaja en `feature/<nombre>` y abre PR contra `main`.
4. Proteger `main`: exigir checks del workflow `CI`, revisión de PR y CODEOWNERS tras sustituir valores de ejemplo.
5. Toda modificación de SPEC/contrato/Harness debe ir en PR revisado. **No editar criterios esperados para pasar un test**.

## CD / despliegue

- `cd.yml`: al hacer push a `main`, crea y publica imágenes de backend/frontend en GitHub Container Registry (GHCR); esto **no despliega por sí solo a un servidor**.
- Despliegue real: ejecución manual `workflow_dispatch` indicando `image_tag=sha-<commit>` previamente publicado por CI, entorno `production` y secrets `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY`, `DEPLOY_KNOWN_HOSTS`; en el servidor se requieren Docker, `compose.prod.yml`, `.env` para PostgreSQL y `backend/.env` para JWT. También necesitará autenticar GHCR para leer imágenes privadas.
- Configurar `production` en GitHub Settings > Environments con revisores y restricciones adecuadas (según disponibilidad del plan).
- Ver instrucciones y lista exacta en `docs/deploy.md`.

## Nota de seguridad

Demo educativa, **no producción lista**. Faltan migraciones, rate limiting, auditoría de sesión, revocación/rotación de JWT y secretos gestionados. JWT en memoria se pierde al recargar, por diseño. El tema sí persiste en `localStorage`.

## Guía del flujo del agente

`<módulo>/<nombre>.scps` → trazabilidad → Codex delega roles → código → `harness/scripts/verify.py` → PR → CI → review → merge. Ejemplo en `docs/agent-workflow.md`.
