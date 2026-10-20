# Demo AWS EC2 con Terraform

Módulo independiente y desechable para alojar manualmente `compose.prod.yml` en una única instancia. No modifica ni ejecuta el Compose de desarrollo, no crea recursos al editar estos archivos y no despliega imágenes. La región predeterminada es `us-east-1`; revisa precios y disponibilidad antes de crear recursos.

## Prerrequisitos

- Terraform CLI 1.6 o posterior y AWS CLI.
- Una cuenta AWS y credenciales locales mediante perfil AWS o AWS IAM Identity Center/SSO. No compartas claves ni las guardes en Terraform.
- Permisos para VPC, rutas, Security Groups, EC2, EBS, Elastic IP, IAM role/profile y Systems Manager. La identidad operadora necesita permisos de Session Manager aparte del perfil de instancia.
- El agente SSM necesita conectividad saliente; este diseño la provee por la subred pública. No abre SSH.

## Preparar y revisar

Desde este directorio, copia `terraform.tfvars.example` a `terraform.tfvars` y ajusta `aws_region` y `allowed_http_cidr`. El valor `0.0.0.0/0` hace el sitio HTTP públicamente accesible; limita el CIDR si solo se requiere acceso desde una red de prueba.

```powershell
terraform init
terraform fmt -check
terraform validate
terraform plan -var-file="terraform.tfvars"
```

Revisa el plan. No se incluye auto-apply ni despliegue automático. Cuando el equipo apruebe la creación, aplicar el mismo plan explícitamente. El estado local no se versiona y **es necesario para administrar y destruir** los recursos: mantenlo privado y respáldalo de forma segura. No pierdas ni borres el estado antes de destruir.

## Acceso y despliegue manual

1. Usa el output `instance_id` para conectar con Session Manager desde la consola AWS o `aws ssm start-session`; usa `public_ip`/`url` para el sitio. No habilites SSH.
2. Copia manualmente la versión aprobada de `compose.prod.yml` a `/opt/evaluacion-2/compose.prod.yml` por el canal operativo aprobado. Terraform no copia configuración ni ejecuta `docker compose up`.
3. Crea `/opt/evaluacion-2/.env` con `POSTGRES_USER`, `POSTGRES_PASSWORD` y `POSTGRES_DB` solamente. Usa una contraseña de PostgreSQL URL-safe porque el Compose construye `DATABASE_URL` con interpolación. Crea `/opt/evaluacion-2/backend/.env` con `JWT_SECRET` (secreto aleatorio de al menos 32 caracteres) y, opcionalmente, `JWT_EXPIRE_MINUTES=60`. Protege ambos archivos (`chmod 600`) y ejecútalos como root con `sudo`; así no es necesario dar acceso al grupo Docker. No guardes estos valores en Terraform, user-data, Git o comandos registrados.
4. Si GHCR es privado, autentica Docker para lectura en GHCR manualmente desde la instancia con un token de alcance mínimo; no lo agregues a Terraform. Ejecuta Docker con `sudo` para que use las mismas credenciales y archivos. El CD actual requiere SSH y no es compatible con esta instancia sin cambios de infraestructura, por eso el despliegue queda manual por SSM en este alcance.
5. Desde `/opt/evaluacion-2`, exporta `GHCR_OWNER` (en minúsculas) e `IMAGE_TAG` (por ejemplo, `sha-<commit>` previamente publicado); `WEB_PORT` por defecto es 80. Usa el mismo tag en pull y up:

   ```bash
   export GHCR_OWNER="renzoayvar"
   export IMAGE_TAG="sha-<commit>"
   sudo env GHCR_OWNER="$GHCR_OWNER" IMAGE_TAG="$IMAGE_TAG" docker compose --env-file .env -f compose.prod.yml config --quiet
   sudo env GHCR_OWNER="$GHCR_OWNER" IMAGE_TAG="$IMAGE_TAG" docker compose --env-file .env -f compose.prod.yml pull
   sudo env GHCR_OWNER="$GHCR_OWNER" IMAGE_TAG="$IMAGE_TAG" docker compose --env-file .env -f compose.prod.yml up -d --remove-orphans
   ```

   Verifica login y persistencia antes de usarla. Para rollback, repite pull/up con el tag SHA previo.

El volumen de PostgreSQL persiste reinicios de contenedores y reemplazos de frontend, pero está en el disco local de la EC2. El placeholder actual no persiste `tasks.json`.

## Destruir para detener costos

Desde el mismo directorio y con el mismo perfil, región, `terraform.tfvars` y estado con que se creó el entorno:

```powershell
terraform destroy -var-file="terraform.tfvars"
```

Confirma el plan de destrucción. Esto elimina la instancia, libera la Elastic IP y elimina VPC, subred, gateway, rutas, Security Group y rol/perfil IAM administrados por este módulo. El disco raíz está marcado `delete_on_termination`; no se crean volúmenes o snapshots retenidos. Se borrarán de forma permanente la base PostgreSQL, cualquier archivo local, `.env` y las imágenes cacheadas. Haz y verifica un respaldo externo antes si necesitas conservar datos. No ejecutes `terraform destroy` sin revisar cuenta, región y estado.

Detener la instancia no equivale a destruir: puede seguir facturándose EBS e IPv4 pública. Tras destruir, comprueba en la consola AWS que no queden recursos manuales fuera del estado, especialmente snapshots, volúmenes o Elastic IP. AWS puede facturar uso ya incurrido y otros servicios de la cuenta.

## Límites

Solo demo: una instancia y un punto de fallo; IPv4/HTTP pública; sin TLS, dominio, RDS, NAT, balanceador, alta disponibilidad, backups, backend remoto de estado ni protección contra destrucción. La imagen AL2023 se obtiene del parámetro público regional de AWS; Compose se instala desde una versión fija oficial. Los secretos son responsabilidad del operador.
