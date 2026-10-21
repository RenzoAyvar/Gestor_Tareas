# Desplegar la demo en AWS EC2

Esta guía ofrece dos caminos alternativos para ejecutar `compose.prod.yml` en Amazon Linux 2023:

1. **Terraform:** crea una VPC dedicada y una EC2 preparada para administrar con Systems Manager (SSM).
2. **EC2 manual:** creas la instancia y su red desde la consola de AWS, y luego instalas Docker.

En ambos casos el despliegue de la aplicación es manual: Terraform y la consola no publican ni descargan imágenes por sí solos. Es una demo de una sola instancia, no una configuración lista para producción. La región predeterminada de Terraform es `us-east-1`; revisa precios y disponibilidad.

## Requisitos comunes

- Cuenta AWS con permisos para crear/administrar los recursos que elijas.
- AWS CLI configurada y Terraform CLI 1.6 o posterior para la ruta Terraform.
- Docker Compose para desarrollo local no es necesario en el servidor: la instancia lo instalará.
- Un commit de `main` cuyo CI terminó correctamente y cuyas imágenes ya se publicaron en GHCR. El workflow `CD - GHCR y despliegue aprobado` publica imágenes, pero no despliega automáticamente a esta EC2.
- Permisos de lectura de GHCR si los paquetes son privados.

No guardes credenciales AWS, tokens de GHCR ni secretos de la aplicación en Git, Terraform, `user-data` o comandos que los dejen en el historial. Para administrar la instancia se recomienda SSM; no hace falta abrir SSH en ninguno de los dos caminos.

## Paso 1: publicar y elegir las imágenes

En GitHub, comprueba que CI para el commit de `main` haya pasado y que las imágenes del mismo commit estén publicadas. El tag sigue el formato `sha-` más el SHA completo de 40 caracteres, por ejemplo `sha-<SHA-completo>`. Anota ese tag; usarás el mismo para backend y frontend.

El owner de GHCR es el owner del repositorio en minúsculas. Para este repositorio:

```bash
export GHCR_OWNER='renzoayvar'
export IMAGE_TAG='sha-<SHA-completo-publicado>'
```

Si GHCR es privado, inicia sesión en Docker **desde la instancia** con un token de GitHub de alcance mínimo `read:packages`. Ejecuta `sudo docker login ghcr.io`; Docker solicitará el usuario y luego la contraseña. Usa el token como contraseña y no lo incluyas directamente en el comando.

## Opción A: crear la infraestructura con Terraform

### A.1 Configurar y revisar

En PowerShell, desde la raíz del repositorio:

```powershell
Set-Location .\infra\terraform\ec2
Copy-Item .\terraform.tfvars.example .\terraform.tfvars
notepad .\terraform.tfvars
```

Revisa al menos `aws_region` y `allowed_http_cidr`. Limita este último a tu IP/red de prueba en formato CIDR (por ejemplo, `203.0.113.10/32`) cuando corresponda. El valor `0.0.0.0/0` permite que cualquiera en Internet intente acceder al sitio HTTP.

Si usas un perfil de AWS o IAM Identity Center/SSO, autentícate antes de Terraform; por ejemplo:

```powershell
aws sso login --profile mi-perfil
$env:AWS_PROFILE = 'mi-perfil'
```

Reemplaza `mi-perfil` por el nombre configurado en AWS CLI.

Inicializa y valida, y revisa cuidadosamente el plan antes de crear recursos:

```powershell
terraform init
terraform fmt -check
terraform validate
terraform plan -var-file="terraform.tfvars"
```

### A.2 Crear la EC2 y conectarse

Solo después de revisar la cuenta, región y recursos del plan:

```powershell
terraform apply -var-file="terraform.tfvars"
```

Confirma la operación cuando Terraform lo solicite. No uses `-auto-approve`. Al terminar, consulta los datos de conexión:

```powershell
terraform output
$instanceId = terraform output -raw instance_id
$region = terraform output -raw aws_region
aws ssm start-session --target $instanceId --region $region
```

También puedes abrir Session Manager desde la consola AWS. La identidad que ejecuta la sesión necesita permisos de SSM; el perfil IAM de la instancia creado por Terraform le permite registrarse en Systems Manager. El bootstrap instala Docker y Compose. Si SSM aún no muestra la instancia como administrada, espera unos minutos y revisa el estado de la instancia y el log `/var/log/user-data-bootstrap.log`.

La URL y la IP pública se consultan con:

```powershell
terraform output url
terraform output public_ip
```

### A.3 Preparar archivos en el servidor

Terraform no copia archivos ni inicia la aplicación. En la sesión SSM, crea el directorio y coloca la versión aprobada de `compose.prod.yml` en `/opt/evaluacion-2/compose.prod.yml` mediante el canal operativo aprobado. Crea también `/opt/evaluacion-2/backend/`.

Si el repositorio es público, puedes descargar el Compose del mismo commit de las imágenes. En la sesión SSM:

```bash
export GHCR_OWNER='renzoayvar'
export IMAGE_TAG='sha-<SHA-completo-publicado>'
COMMIT_SHA="${IMAGE_TAG#sha-}"
sudo curl --fail --location \
  "https://raw.githubusercontent.com/RenzoAyvar/Gestor_Tareas/${COMMIT_SHA}/compose.prod.yml" \
  --output /opt/evaluacion-2/compose.prod.yml
sudo chmod 0644 /opt/evaluacion-2/compose.prod.yml
```

Reemplaza el placeholder por el SHA real. Para un repositorio privado, usa un mecanismo de transferencia aprobado; no añadas credenciales de GitHub a la URL ni al `user-data`.

Continúa con el [paso 3: configurar y ejecutar la aplicación](#paso-3-configurar-y-ejecutar-la-aplicación).

## Opción B: crear una EC2 manualmente

### B.1 Lanzar la instancia

En la consola AWS, abre **EC2 → Launch instance** y configura:

1. Nombre descriptivo para la demo.
2. AMI **Amazon Linux 2023**, arquitectura **64-bit (x86)**.
3. Tipo `t3.small` como punto de partida; revisa costos y dimensiona según necesidad.
4. Una VPC/subred pública con ruta a un Internet Gateway y una IPv4 pública. Si no tienes una VPC predeterminada, crea una VPC, una subred pública y una ruta al Internet Gateway. Asigna una Elastic IP si necesitas conservar la dirección al reemplazar o detener la instancia.
5. Disco raíz EBS gp3 cifrado, de al menos 30 GiB.
6. Un Security Group con entrada TCP/80 limitada a tu IP/red de prueba. No abras PostgreSQL (5432), backend (8000) ni SSH (22) a Internet. La salida debe permitir HTTPS para SSM y descargar paquetes/imágenes.
7. Un perfil IAM de instancia que incluya `AmazonSSMManagedInstanceCore`. La identidad operadora también necesita permisos para iniciar una sesión SSM.

Inicia la instancia y espera a que aparezca como **Managed node** en Systems Manager. Si usas una instancia existente, verifica igualmente arquitectura, red pública, reglas del Security Group, perfil IAM y espacio disponible.

### B.2 Instalar Docker y Compose

Conéctate mediante **EC2 → Connect → Session Manager** o AWS CLI:

```powershell
aws ssm start-session --target i-0123456789abcdef0 --region us-east-1
```

Reemplaza el ID y la región del ejemplo por los de tu instancia.

En la terminal Linux de EC2 instala Docker y el plugin de Compose (el mismo mecanismo y versión que usa el bootstrap Terraform):

```bash
sudo dnf install -y docker curl
sudo install -d -m 0755 /usr/local/lib/docker/cli-plugins
sudo curl --fail --show-error --silent --location --retry 5 \
  "https://github.com/docker/compose/releases/download/v2.32.4/docker-compose-linux-x86_64" \
  --output /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod 0755 /usr/local/lib/docker/cli-plugins/docker-compose
sudo systemctl enable --now docker
sudo docker compose version
```

Crea los directorios y copia `/opt/evaluacion-2/compose.prod.yml` desde una fuente aprobada:

```bash
sudo install -d -m 0750 /opt/evaluacion-2/backend
sudo chown -R ec2-user:ec2-user /opt/evaluacion-2
```

Si el repositorio es público, también puedes descargar `compose.prod.yml` desde el mismo commit que las imágenes, usando el comando `curl` de la opción Terraform. Para subirlo desde Windows con SCP, configura un par de claves y permite temporalmente TCP/22 **solo desde tu IP `/32`**; desde la raíz del repositorio ejecuta:

```powershell
$publicIp = '203.0.113.10'
scp -i .\mi-clave.pem .\compose.prod.yml "ec2-user@${publicIp}:/tmp/compose.prod.yml"
```

Sustituye `203.0.113.10` por la IPv4 pública real.

Luego, en la sesión SSM, instala el archivo y cierra el acceso SSH temporal:

```bash
sudo install -o root -g root -m 0644 /tmp/compose.prod.yml /opt/evaluacion-2/compose.prod.yml
rm -f /tmp/compose.prod.yml
```

No abras SSH si puedes usar un canal aprobado como repositorio accesible desde la instancia o transferencia administrada. Nunca dejes TCP/22 abierto a `0.0.0.0/0`.

Obtén la URL de la aplicación en la consola EC2 (o consulta la Elastic IP asignada) y continúa con el [paso 3](#paso-3-configurar-y-ejecutar-la-aplicación).

## Paso 3: configurar y ejecutar la aplicación

Estos pasos son comunes a las dos opciones. Ejecuta los comandos en la terminal Linux de EC2, desde `/opt/evaluacion-2`, usando el tag publicado en el paso 1:

```bash
cd /opt/evaluacion-2
export GHCR_OWNER='renzoayvar'
export IMAGE_TAG='sha-<SHA-completo-publicado>'
```

Crea los archivos de entorno directamente en el servidor. No uses los archivos `.env.example` como si fueran secretos reales. Las contraseñas de PostgreSQL deben ser URL-safe porque `compose.prod.yml` construye `DATABASE_URL` mediante interpolación.

```bash
sudo install -o root -g root -m 0600 /dev/null /opt/evaluacion-2/.env
sudo install -o root -g root -m 0600 /dev/null /opt/evaluacion-2/backend/.env
sudoedit /opt/evaluacion-2/.env
sudoedit /opt/evaluacion-2/backend/.env
```

En `/opt/evaluacion-2/.env`, configura solo estos valores:

```dotenv
POSTGRES_USER=eval2
POSTGRES_PASSWORD=<secreto-fuerte-url-safe>
POSTGRES_DB=eval2db
```

En `/opt/evaluacion-2/backend/.env`, configura:

```dotenv
JWT_SECRET=<secreto-aleatorio-de-al-menos-32-caracteres>
JWT_EXPIRE_MINUTES=60
```

Puedes generar un secreto aleatorio con `openssl rand -hex 32`; copia su salida al archivo sin publicarla ni guardarla en Git. Conserva permisos restringidos:

```bash
sudo chmod 600 /opt/evaluacion-2/.env /opt/evaluacion-2/backend/.env
```

Comprueba la configuración y descarga las imágenes:

```bash
sudo env GHCR_OWNER="$GHCR_OWNER" IMAGE_TAG="$IMAGE_TAG" \
  docker compose --env-file .env -f compose.prod.yml config --quiet
sudo env GHCR_OWNER="$GHCR_OWNER" IMAGE_TAG="$IMAGE_TAG" \
  docker compose --env-file .env -f compose.prod.yml pull
```

Si las imágenes son privadas, inicia sesión en GHCR como se indica en el paso 1. Ejecuta Docker con `sudo` de forma consistente para que Compose use las mismas credenciales y pueda leer los archivos protegidos.

### Paso 4: inicializar la base y crear un usuario (primera instalación)

La imagen no contiene un usuario predeterminado ni crea tablas automáticamente en producción. Arranca PostgreSQL y crea el esquema explícitamente una sola vez:

```bash
sudo env GHCR_OWNER="$GHCR_OWNER" IMAGE_TAG="$IMAGE_TAG" \
  docker compose --env-file .env -f compose.prod.yml up -d db
sudo env GHCR_OWNER="$GHCR_OWNER" IMAGE_TAG="$IMAGE_TAG" \
  docker compose --env-file .env -f compose.prod.yml \
  run --rm -e ALLOW_SCHEMA_INIT=yes backend python -m scripts.init_schema
```

Si necesitas el usuario inicial, créalo interactivamente; el programa solicita la contraseña sin mostrarla:

```bash
sudo env GHCR_OWNER="$GHCR_OWNER" IMAGE_TAG="$IMAGE_TAG" \
  docker compose --env-file .env -f compose.prod.yml \
  run --rm backend python -m scripts.create_user --correo admin@practica.com
```

No repitas la inicialización del esquema como mecanismo de migración. Este proyecto de demo aún no incluye Alembic.

### Paso 5: iniciar y comprobar

Inicia los servicios:

```bash
sudo env GHCR_OWNER="$GHCR_OWNER" IMAGE_TAG="$IMAGE_TAG" \
  docker compose --env-file .env -f compose.prod.yml up -d --remove-orphans
sudo env GHCR_OWNER="$GHCR_OWNER" IMAGE_TAG="$IMAGE_TAG" \
  docker compose --env-file .env -f compose.prod.yml ps
```

Revisa los logs si algún servicio no queda activo:

```bash
sudo env GHCR_OWNER="$GHCR_OWNER" IMAGE_TAG="$IMAGE_TAG" \
  docker compose --env-file .env -f compose.prod.yml logs --tail=100
```

Abre `http://<IP-pública>` desde una red permitida por el Security Group. El frontend escucha en TCP/80 por defecto. No expongas `/docs`, PostgreSQL ni el puerto interno del backend. Esta demo sirve HTTP, no HTTPS; no la uses para transmitir credenciales por Internet sin añadir TLS y las protecciones necesarias.

## Actualizar o revertir una versión

Selecciona otro tag `sha-<SHA-completo>` que ya esté publicado. En una nueva sesión SSH/SSM, exporta el owner y tag deseados, y repite `docker compose pull` y `docker compose up -d --remove-orphans` del paso 3/5. Para revertir, usa el tag SHA de la versión anterior. No cambies tags entre el pull y el up.

El workflow CD incluido requiere SSH y no es compatible con la instancia Terraform, que deliberadamente no abre SSH. En esta guía el despliegue es manual vía SSM; no cambies el Security Group para habilitar el workflow sin una revisión separada.

## Eliminar recursos y evitar costos

### Entorno creado con Terraform

Desde `infra/terraform/ec2`, con la misma cuenta, perfil, región, `terraform.tfvars` y estado que usaste al crear:

```powershell
terraform destroy -var-file="terraform.tfvars"
```

Revisa la cuenta, región y plan de destrucción, y confirma solo si estás seguro. Esto elimina la instancia, la Elastic IP y los recursos administrados por el módulo. El disco raíz se elimina al terminar la instancia. Se borrarán permanentemente la base PostgreSQL, los archivos locales, los `.env` y las imágenes cacheadas; verifica antes cualquier respaldo que necesites. No borres el estado de Terraform antes de destruir.

### Instancia creada manualmente

Termina la instancia desde EC2 y comprueba/elimina los recursos creados para esta demo que no se eliminen con ella, incluidos Elastic IP, volúmenes EBS, snapshots, reglas y perfil IAM dedicado. Verifica en la consola que no queden recursos facturables. La terminación elimina los datos locales si el volumen está configurado para borrarse.

Detener una EC2 no equivale a eliminarla: EBS y algunas direcciones IPv4 pueden seguir generando cargos. AWS también puede facturar uso ya incurrido.

## Límites y riesgos

- Una sola instancia y un solo punto de fallo; PostgreSQL usa un volumen local de EC2, sin backups administrados ni alta disponibilidad.
- HTTP/IP pública, sin TLS, dominio, balanceador, RDS, NAT ni backend remoto de estado Terraform.
- El placeholder actual no persiste `tasks.json`.
- Los secretos y su rotación son responsabilidad del operador.
- Restringe el CIDR HTTP, protege los `.env`, mantén privadas las credenciales y verifica respaldos antes de destruir.
