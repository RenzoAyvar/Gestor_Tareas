# Deploy GitHub Actions (dos etapas)

## 1. CI obligatorio

GitHub Actions `CI` corre en PR y `main` tres gates: SPEC, backend+Postgres 16 y frontend. Antes del primer PR ejecutar `cd frontend && npm install`, **versionar package-lock.json**, y configurar branch protection para exigir: `Harness SPEC`, `Backend / PostgreSQL`, `Frontend / Vitest / Build` (nombres tal cual GitHub los muestre). Ajustar CODEOWNERS a equipos reales.

## 2. Publicación de imágenes GHCR

`CD - GHCR y despliegue aprobado` publica imágenes `ghcr.io/<owner>/evaluacion2-{backend,frontend}:sha-<commit>` cuando CI de `main` termina exitoso. El `workflow_dispatch` manual solo despliega una imagen **ya publicada**. Publicar **no es desplegar** al servidor. Los paquetes pueden ser privados; Docker del servidor necesitará `docker login ghcr.io` autorizado.

## 3. Configuración del servidor (requisito antes de activar deploy)

Servidor Linux con Docker Engine + Compose y SSH. Preparar `/opt/evaluacion-2/compose.prod.yml` (de este repo) y `/opt/evaluacion-2/.env` basado en `.env.production.example`, con secretos privados y permisos restringidos; no subir `.env` al repositorio. DNS/TLS y HTTPS con proxy externo o gateway gestionado (el ejemplo escucha 8080 HTTP, NO es un endpoint HTTPS listo para Internet).

- Crear imágenes accesibles desde el servidor (hacer público GHCR o autenticar el `docker` del servidor con credencial de lectura `read:packages`).
- Configurar GitHub Environments `production` con aprobadores/restricciones de ramas cuando el plan lo permita.
- Crear **environment secrets**: `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY` (clave privada del usuario de despliegue), `DEPLOY_KNOWN_HOSTS` (huella SSH obtenida/verificada **fuera de banda**, nunca confiar ciegamente en ssh-keyscan del propio workflow).
- Preparar permisos del usuario remoto para Docker, acceso a `/opt/evaluacion-2` y puerto expuesto.

## 4. Bootstrap de tablas una sola vez

Este proyecto de demostración no incluye migraciones Alembic. Con valores `GHCR_OWNER` / `IMAGE_TAG` exportados y con `.env` configurado, ejecutar en el servidor **antes del primer despliegue funcional**:

```bash
cd /opt/evaluacion-2
export GHCR_OWNER='nombre-owner-github-en-minusculas'
export IMAGE_TAG='sha-COMMIT_PUBLICADO'
docker compose --env-file .env -f compose.prod.yml up -d db
# Crea las tablas explícitamente; en producción madura usar migraciones.
docker compose --env-file .env -f compose.prod.yml run --rm -e ALLOW_SCHEMA_INIT=yes backend python -m scripts.init_schema
```

El comando anterior requiere que la imagen de backend ya esté publicada y accesible. Crear primer usuario por CLI interactiva si procede, sin credenciales hardcodeadas:

```bash
docker compose --env-file .env -f compose.prod.yml run --rm backend python -m scripts.create_user --correo admin@practica.com
```

## 5. Despliegue manual protegido

En GitHub Actions seleccionar `CD - GHCR y despliegue aprobado` → Run workflow sobre `main` → indicar `image_tag=sha-<SHA del commit>` de la imagen publicada por CI. Tras la aprobación del environment `production`, se conecta mediante SSH con verificación de host y ejecuta `docker compose pull` + `up -d` en `/opt/evaluacion-2`. Si el servidor o los secretos faltan, falla explícitamente. **No simula éxito**.

## Riesgos pendientes antes de producción

Agregar migraciones, TLS, rotación de secretos, control de intentos de login, seguridad de sesiones/refresh tokens, observabilidad, rollback automatizado, escaneo SCA/containers, procesos para restauración PostgreSQL, tests e2e con HTTPS y gestión de autorización en endpoints protegidos.
