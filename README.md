# Evaluación 2 — SDD + Harness Engineering + Codex multiagente

Proyecto de referencia de **login completo**: React 18 + Vite + Tailwind, FastAPI + SQLAlchemy async + PostgreSQL, JWT en memoria y dark/light.

## Arquitectura de trabajo

- `specs/`: qué construir, contrato, criterios, plan, tareas y trazabilidad (SDD).
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
# El script crea .env con secretos aleatorios y, si npm existe, genera frontend/package-lock.json.
docker compose up --build -d
```

- Web: http://localhost:5173
- API Docs: http://localhost:8000/docs
- Salud API: http://localhost:8000/health
- La base y tablas **solo se crean automáticamente para desarrollo** (`DEV_CREATE_TABLES=true`). Para producción se necesitan migraciones/versionado de esquema.
- El proyecto no contiene usuarios ni contraseñas por defecto.

### Crear un usuario de prueba

Con los contenedores arriba (comando interactivo, no guarda la contraseña en el repositorio):

```powershell
docker compose exec backend python -m scripts.create_user --correo admin@practica.com
```

El comando solicita una contraseña de forma segura. Después entra desde la interfaz con ese correo y la contraseña que hayas elegido. El JSON de la SPEC que menciona `admin123` es **solo un ejemplo de contrato**, no una cuenta preparada.

### Detener los servicios

```powershell
docker compose down
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

Para backend sin Docker, configurar `DATABASE_URL` PostgreSQL y `JWT_SECRET` antes de correr pytest. Para frontend ejecutar `npm install` en `frontend/`. No se incluye `package-lock.json` porque este entorno de elaboración no permite resolver npm; **generarlo una vez con `npm install`, versionarlo, y después usar `npm ci`**. El CI falla si no existe este lockfile, deliberadamente para asegurar instalaciones reproducibles.

## Colaboración GitHub

1. Crear repositorio vacío en GitHub y subir el contenido (`git init`, `git add .`, `git commit`, conectar `origin`, `git push`).
2. Versionar `frontend/package-lock.json` tras `npm install`.
3. Cada integrante trabaja en `feature/<nombre>` y abre PR contra `main`.
4. Proteger `main`: exigir checks del workflow `CI`, revisión de PR y CODEOWNERS tras sustituir valores de ejemplo.
5. Toda modificación de SPEC/contrato/Harness debe ir en PR revisado. **No editar criterios esperados para pasar un test**.

## CD / despliegue

- `cd.yml`: al hacer push a `main`, crea y publica imágenes de backend/frontend en GitHub Container Registry (GHCR); esto **no despliega por sí solo a un servidor**.
- Despliegue real: ejecución manual `workflow_dispatch` indicando `image_tag=sha-<commit>` previamente publicado por CI, entorno `production` y secrets `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY`, `DEPLOY_KNOWN_HOSTS`; en el servidor se requiere Docker, directorio remoto con `compose.prod.yml` y `.env` secreto preparado. También necesitará autenticar GHCR para leer imágenes privadas.
- Configurar `production` en GitHub Settings > Environments con revisores y restricciones adecuadas (según disponibilidad del plan).
- Ver instrucciones y lista exacta en `docs/deploy.md`.

## Nota de seguridad

Demo educativa, **no producción lista**. Faltan migraciones, rate limiting, auditoría de sesión, revocación/rotación de JWT y secretos gestionados. JWT en memoria se pierde al recargar, por diseño. El tema sí persiste en `localStorage`.

## Guía del flujo del agente

`spec.md` → `plan.md` → `tasks.md` → Codex delega roles → código → `harness/scripts/verify.py` → PR → CI → review → merge. Ejemplo de solicitud en `docs/agent-workflow.md`.
