# Deploy GitHub Actions (dos etapas)

## 1. CI obligatorio

GitHub Actions `CI` corre en PR y `main` tres gates: SPEC, backend+Postgres 16 y frontend. Antes del primer PR ejecutar `cd frontend && npm install`, **versionar package-lock.json**, y configurar branch protection para exigir: `Harness SPEC`, `Backend / PostgreSQL`, `Frontend / Vitest / Build` (nombres tal cual GitHub los muestre). Ajustar CODEOWNERS a equipos reales.

## 2. Publicación de imágenes GHCR

`CD - GHCR y despliegue aprobado` publica imágenes `ghcr.io/<owner>/evaluacion2-{backend,frontend}:sha-<commit>` cuando CI de `main` termina exitoso. El `workflow_dispatch` manual solo despliega una imagen **ya publicada**. Publicar **no es desplegar** al servidor. Los paquetes pueden ser privados; Docker del servidor necesitará `docker login ghcr.io` autorizado.

## 3. Acceso AWS del workflow y servidor administrado

El despliegue no usa SSH ni claves permanentes de AWS. El job `deploy` solicita credenciales temporales mediante GitHub OIDC y ejecuta un documento `AWS-RunShellScript` sobre una única EC2 administrada por Systems Manager. Configurar GitHub Environment `production` con aprobación humana y restricción a `main`.

- La EC2 debe aparecer `Online` en SSM y su perfil debe incluir `AmazonSSMManagedInstanceCore`.
- El rol OIDC debe confiar únicamente en `repo:RenzoAyvar/Gestor_Tareas:environment:production` y permitir `ssm:SendCommand` sobre la instancia objetivo y `AWS-RunShellScript`, además de las lecturas necesarias para consultar el estado del comando.
- Crear las **environment variables** `AWS_ROLE_ARN`, `AWS_REGION` y `EC2_INSTANCE_ID`. El ARN del rol no es un secreto; no se almacenan Access Keys en GitHub.
- Crear imágenes accesibles desde el servidor: hacer públicos los paquetes GHCR o autenticar Docker previamente con una credencial de lectura. El workflow no transporta tokens GHCR dentro de comandos SSM.

El comando remoto instala Docker/Compose si faltan, actualiza `compose.prod.yml` desde el commit del workflow y crea `/opt/evaluacion-2/.env` y `/opt/evaluacion-2/backend/.env` con secretos aleatorios solo cuando esos archivos todavía no existen. Los conserva en despliegues posteriores, con modo `0600`, y nunca imprime sus valores.

## 4. Bootstrap de tablas y usuario inicial

Este proyecto de demostración no incluye migraciones Alembic. En el primer `workflow_dispatch`, seleccionar `initialize_schema=true`; en despliegues posteriores dejarlo en `false`. La creación del usuario continúa siendo una operación separada e interactiva mediante SSM/Session Manager, para no transportar su contraseña en inputs, logs o parámetros de Run Command:

```bash
cd /opt/evaluacion-2
export GHCR_OWNER='nombre-owner-github-en-minusculas'
export IMAGE_TAG='sha-COMMIT_PUBLICADO'
docker compose --env-file .env -f compose.prod.yml run --rm backend python -m scripts.create_user --correo admin@practica.com
```

## 5. Despliegue manual protegido

En GitHub Actions seleccionar `CD - GHCR y despliegue aprobado` → Run workflow sobre `main` → indicar `image_tag=sha-<SHA del commit>` de la imagen publicada por CI. En el primer despliegue marcar también `initialize_schema`. Tras aprobar el environment `production`, GitHub asume el rol OIDC, comprueba que la EC2 esté `Online`, envía el despliegue por SSM y espera su resultado. Si la autorización, la instancia, GHCR o los contenedores fallan, el job muestra la salida remota y termina con error. **No simula éxito**.

## Riesgos pendientes antes de producción

Agregar migraciones, TLS, rotación de secretos, control de intentos de login, seguridad de sesiones/refresh tokens, observabilidad, rollback automatizado, escaneo SCA/containers, procesos para restauración PostgreSQL, tests e2e con HTTPS y gestión de autorización en endpoints protegidos.
