# Infraestructura, despliegue y recuperación

Guía canónica para operar HHL ERP en un servidor Linux doméstico con Docker Compose y Cloudflare Tunnel. El contrato ejecutable reside en [Compose](../docker-compose.yml), los [Dockerfiles del backend](../backend/Dockerfile) y [frontend](../frontend/Dockerfile), la [configuración de Nginx](../frontend/nginx.conf) y la [plantilla de entorno](../.env.example). La evidencia de lo realmente ejecutado se registra únicamente en [PROJECT_STATE](PROJECT_STATE.md#validación-de-infraestructura-docker-y-cierre-documental).

Los comandos de esta guía son para **Bash en Linux**, desde la raíz del checkout, salvo donde se indique otra ubicación. Requieren Docker Engine mantenido, versión 28 o posterior, y el plugin `docker compose` con soporte para `--wait`. Instalar Docker según su [guía oficial para Ubuntu](https://docs.docker.com/engine/install/ubuntu/). Los ejemplos de SSH, UFW y systemd corresponden a Ubuntu/Debian; adaptar el nombre de la unidad SSH y la subred a la máquina real.

## Topología y límites de acceso

- `db` mantiene PostgreSQL en el volumen lógico `postgres_data`, montado en `/var/lib/postgresql/data`. No publica el puerto 5432 al host.
- `backend` escucha internamente en 8000 y se conecta a `db:5432`. Su imagen ejecuta con UID/GID `10001:10001`. Compose espera la salud de PostgreSQL, aplica las migraciones y solo entonces ejecuta Uvicorn. Si falla la migración, el proceso termina sin arrancar la API.
- `frontend` sirve los estáticos con Nginx en 80. Su build recibe `VITE_API_BASE_URL=/`; la configuración actual del cliente convierte ese valor en rutas del mismo origen. Nginx conserva `/api/v1` al reenviar `/api/` a `http://backend:8000/api/`, y las rutas de navegación usan el fallback a `index.html`.
- `cloudflared`, habilitado por el perfil `tunnel`, recibe el tráfico de Cloudflare y lo entrega a `http://frontend:80`. Este es el único origen HTTP que se publica mediante el túnel.

Los cuatro servicios comparten `erp_internal_net`, una red bridge con `internal: true`. `db` y `backend` pertenecen únicamente a esa red, sin salida directa a Internet ni puertos publicados al host. Por esa misma red, `frontend` alcanza `backend:8000` y recibe tráfico de `cloudflared`. El conector también pertenece a `tunnel_egress_net`, que le proporciona salida hacia Cloudflare. [Redes internas de Compose](https://docs.docker.com/reference/compose-file/networks/#internal).

`frontend` también pertenece a `frontend_local_net`, una red bridge estándar exclusiva de ese servicio. Docker Engine omite el mapeo al host cuando el contenedor está conectado únicamente a una red interna. La segunda red permite aplicar el mapeo `127.0.0.1:${FRONTEND_PORT:-8080}:80` para pruebas desde el host. Mantener el enlace explícito a `127.0.0.1` para limitar el acceso al loopback. [Publicación de puertos en Docker Engine](https://docs.docker.com/engine/network/port-publishing/).

Compose antepone el nombre del proyecto a las redes y al volumen, por ejemplo `<proyecto>_postgres_data`. Conservar el directorio/nombre de proyecto utilizado en el primer despliegue: cambiarlo, incluso mediante `-p`, puede seleccionar un volumen nuevo y dar la impresión de que se perdió la base. No borrar el volumen anterior para resolverlo.

## Preparar el entorno

Crear el archivo raíz sin sobrescribir una configuración existente:

```bash
umask 077
test -e .env || cp .env.example .env
chmod 600 .env
openssl rand -hex 32
```

Editar `.env` con un editor local y colocar la clave generada en `POSTGRES_PASSWORD`. `POSTGRES_USER` y `POSTGRES_DB` admiten en esta receta letras, números y guion bajo. Usar la contraseña hexadecimal indicada por la plantilla: Compose inserta los valores directamente en `DATABASE_URL`, sin codificar caracteres reservados de una URI. Las tres variables son obligatorias y Compose rechaza valores vacíos. Cambiarlas en `.env` después de inicializar el volumen **no cambia** el usuario, la clave ni la base ya creados; planificar la rotación con PostgreSQL y actualizar luego la conexión de la API.

Mantener `ENV=production`. `ENV=development` activa la identidad Dummy y simula permisos locales; usarlo únicamente en pruebas aisladas, sin túnel. En `production` el Dummy permanece deshabilitado y las funciones que exigen identidad no disponen aún de un proveedor real. **Esto no implementa autenticación ni protege automáticamente los flujos antiguos compatibles.** La sesión y la autorización reales siguen pendientes del [Módulo 2](07_fase4_evolucion_y_resiliencia.md#módulo-2-identidad-y-seguridad); el comportamiento del proveedor se define en la [configuración del backend](../backend/README.md#configuración-local).

`FRONTEND_PORT` selecciona el puerto de loopback; su valor predeterminado es 8080. `TUNNEL_TOKEN` puede permanecer vacío para el stack local y debe completarse antes de activar `tunnel`: el propio conector rechaza un token ausente o inválido. No usar el `.env` de `backend/` para Compose, ni añadir credenciales a variables `VITE_*`.

El [gitignore raíz](../.gitignore) excluye los archivos `.env*` reales y permite `.env.example`; los contextos de construcción también excluyen esos archivos. Restringir acceso a `.env` y respaldarlo cifrado fuera del repositorio. Validar sin imprimir las variables resueltas, porque la salida completa de `docker compose config` puede revelar secretos:

```bash
docker compose config --quiet
```

## Operación con Docker Compose

Construir y arrancar únicamente el stack local:

```bash
docker compose build backend frontend
docker compose up -d --wait db backend frontend
docker compose ps
```

Los healthchecks encadenan `db`, `backend` y `frontend`; el del backend consulta `/health` dentro del contenedor. Las migraciones se ejecutan en cada arranque de `backend`. La política `unless-stopped` reinicia los servicios tras un fallo, pero no resuelve una migración incompatible. Revisar sus logs y el procedimiento específico de [migraciones del backend](../backend/README.md#migraciones-con-alembic) antes de intervenir en el esquema.

Con el puerto predeterminado, comprobar desde el servidor:

```bash
curl --fail http://127.0.0.1:8080/
curl --fail http://127.0.0.1:8080/proyectos
docker compose logs --tail=100 db backend frontend
docker compose logs --follow --tail=100 backend
```

Adaptar 8080 si se cambió `FRONTEND_PORT`. Una respuesta de la SPA solo confirma entrega estática: comprobar también una llamada real de `/api/v1` acorde con el contrato y los permisos disponibles. Los endpoints de identidad pueden fallar mientras el Módulo 2 no esté implementado. Para una revisión remota, preferir Cloudflare Access o un reenvío SSH local desde la estación administradora; no ampliar el mapeo Docker a la LAN.

Tras configurar el túnel como se indica en la sección siguiente:

```bash
docker compose --profile tunnel up -d --build --wait
docker compose --profile tunnel logs --follow --tail=100 cloudflared
```

`--wait` espera los servicios con healthcheck; `cloudflared` no tiene uno, por lo que un contenedor arrancado no acredita conexión al edge. Confirmar el estado en Cloudflare, sus logs y una solicitud autorizada al hostname. La semántica de arranque se documenta en [Compose up](https://docs.docker.com/reference/cli/docker/compose/up/).

Detener solo el túnel, detener todo conservando contenedores o retirar el stack conservando los datos son acciones distintas:

```bash
docker compose --profile tunnel stop cloudflared
docker compose --profile tunnel stop
docker compose --profile tunnel down
```

Elegir la acción necesaria; no es preciso ejecutar las tres. **No añadir `-v`/`--volumes` a `down` ni ejecutar limpiezas de volúmenes:** el volumen `postgres_data` contiene los datos de negocio y el registro de operaciones. [Compose down](https://docs.docker.com/reference/cli/docker/compose/down/) conserva por defecto los volúmenes nombrados.

Para actualizar, realizar primero un backup, fijar el commit de aplicación de destino y revisar sus migraciones. Conservar el nombre del proyecto, reconstruir `backend`/`frontend` y ejecutar `up` nuevamente; si se recrea `backend`, recrear también `frontend` para renovar la resolución del upstream de Nginx. Las etiquetas actuales de imágenes son móviles; registrar los identificadores/digests desplegados antes de actualizarlas. No asumir que revertir una imagen revierte una migración ni hacer downgrade de producción sin un plan de recuperación.

## Cloudflare Tunnel y Zero Trust

1. Usar una cuenta Cloudflare con control del dominio y crear primero una aplicación de **Cloudflare Access** para el hostname, con política Allow limitada a las personas/grupos autorizados y MFA según la organización. Proteger también `/api/` y evitar políticas Bypass. Habilitar la validación del token de Access en el conector mediante **Protect with Access**, con el Audience de esa aplicación. Access añade una barrera externa; no crea actores ni roles dentro del ERP. Seguir la [guía oficial de aplicaciones protegidas](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app/).
2. Crear en el panel Zero Trust un túnel gestionado remotamente y obtener su token de conector. Guardarlo como `TUNNEL_TOKEN` en el `.env` raíz. Compose lo entrega por entorno; el comando es `tunnel --no-autoupdate run`, sin credenciales en los argumentos. La [referencia de parámetros del túnel](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/run-parameters/#token) describe esa variable.
3. Añadir al túnel una ruta de aplicación para el hostname elegido, por ejemplo `erp.example.com`, con tipo **HTTP**, servicio **`frontend:80`**, equivalente a **`http://frontend:80`**, y sin limitar la ruta a `/api/`. Así la SPA y la API comparten origen. `localhost` dentro de `cloudflared` identificaría al propio conector, no a Nginx. La [configuración de rutas](https://developers.cloudflare.com/tunnel/concepts/routing/) vincula el hostname con el servicio interno.
4. Activar el perfil con el comando de operación anterior. Verificar que un usuario no autorizado queda bloqueado por Access, que uno autorizado carga la SPA y que el tráfico API llega a `backend` conservando `/api/v1`.

No abrir ni redirigir puertos en el router: **cero port-forwarding** para HTTP, PostgreSQL o la API. El conector establece conexiones salientes; mantener DNS y salida hacia los destinos requeridos por Cloudflare. Si se restringe el tráfico saliente, consultar sus [requisitos de firewall del túnel](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/tunnel-with-firewall/). El tramo interno hasta Nginx usa HTTP en la red Docker; no afirmar que hay TLS entre contenedores.

Para revocar una exposición, detener `cloudflared` y deshabilitar la ruta en Cloudflare. Si se filtra `TUNNEL_TOKEN`, rotarlo en Cloudflare, actualizar `.env` y recrear el conector; no basta con borrar una copia local del secreto.

## Hardening del servidor Linux y de la LAN

Estas acciones se aplican manualmente en el anfitrión, no dentro de los contenedores. Mantener el sistema y Docker actualizados, un usuario administrador individual con `sudo`, espacio de disco supervisado y hora sincronizada. Limitar quién accede al socket o al grupo `docker`: su control equivale a privilegios elevados sobre el host. No exponer el daemon por TCP.

### SSH exclusivamente con llaves

Desde la estación administradora, generar una llave con frase de paso si aún no existe e instalar **solo la clave pública** en la cuenta no-root del servidor. Sustituir `operador` y la IP de ejemplo:

```bash
ssh-keygen -t ed25519 -a 100 -f ~/.ssh/hhl_admin
ssh-copy-id -i ~/.ssh/hhl_admin.pub operador@192.168.50.10
ssh -i ~/.ssh/hhl_admin -o PasswordAuthentication=no -o KbdInteractiveAuthentication=no operador@192.168.50.10
```

No sobrescribir una llave existente. Antes de endurecer SSH, verificar en esa nueva sesión que la llave y `sudo` funcionan; mantener otra sesión abierta y acceso por consola para recuperación. En Ubuntu/Debian, comprobar que `/etc/ssh/sshd_config` incluye `sshd_config.d/*.conf` y crear `/etc/ssh/sshd_config.d/00-hhl-hardening.conf` mediante `sudoedit` con:

```text
PubkeyAuthentication yes
AuthenticationMethods publickey
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
```

Validar y recargar desde el servidor:

```bash
sudo /usr/sbin/sshd -t
sudo /usr/sbin/sshd -T | grep -E '^(pubkeyauthentication|authenticationmethods|passwordauthentication|kbdinteractiveauthentication|permitrootlogin) '
sudo systemctl reload ssh
```

Confirmar los valores efectivos y probar otra conexión por llave antes de cerrar las sesiones previas. OpenSSH suele usar el primer valor encontrado; revisar directivas anteriores y bloques `Match` si el resultado no coincide, utilizando `sshd -T -C` para el contexto de conexión real. Algunas distribuciones llaman `sshd` a la unidad systemd. Referencias: [OpenSSH sshd_config](https://man.openbsd.org/sshd_config) y [operación SSH en Ubuntu](https://documentation.ubuntu.com/server/how-to/security/openssh-server/).

### UFW y fail2ban

Instalar las herramientas desde los repositorios del sistema:

```bash
sudo apt-get update
sudo apt-get install ufw fail2ban python3-systemd
```

Antes de habilitar UFW, reemplazar la subred de ejemplo por la VLAN/subred de administración y confirmar que contiene la IP desde la que se está conectado. El ejemplo usa SSH en 22; adaptar si el servidor escucha en otro puerto:

```bash
ADMIN_SUBNET=192.168.50.0/24
SSH_PORT=22
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from "$ADMIN_SUBNET" to any port "$SSH_PORT" proto tcp
sudo ufw status numbered
sudo ufw enable
sudo ufw status verbose
```

Revisar y retirar reglas permisivas preexistentes, como `OpenSSH ALLOW Anywhere`, antes de dar por restringido el acceso. Mantener activa la cobertura IPv6 de UFW y aplicar también allí la denegación entrante; añadir una regla SSH IPv6 solo si existe una subred de administración IPv6 autorizada. No permitir 80, 443, 8080, 8000 ni 5432 hacia la LAN para este stack. La [guía de UFW de Ubuntu](https://documentation.ubuntu.com/server/how-to/security/firewalls/) explica las reglas por origen.

Crear `/etc/fail2ban/jail.d/hhl-sshd.local` mediante `sudoedit`:

```ini
[sshd]
enabled = true
backend = systemd
port = 22
banaction = ufw
findtime = 10m
maxretry = 5
bantime = 1h
```

Adaptar también aquí el puerto SSH. El backend systemd lee el journal sin `logpath`; `python3-systemd` aporta su integración en estos sistemas. Validar antes de reiniciar:

```bash
sudo fail2ban-client -t
sudo systemctl enable --now fail2ban
sudo systemctl restart fail2ban
sudo fail2ban-client status sshd
```

Las opciones proceden de la [configuración oficial de fail2ban](https://github.com/fail2ban/fail2ban/blob/master/config/jail.conf); la [acción UFW](https://github.com/fail2ban/fail2ban/blob/master/config/action.d/ufw.conf) requiere que UFW esté habilitado. Comprobar sus logs y el jail efectivo; fail2ban complementa las llaves y la restricción por subred.

### Precaución crítica: Docker puede saltarse UFW

Docker configura reglas de firewall/NAT, por defecto mediante iptables, para publicar puertos. Ese tráfico puede desviarse antes de las cadenas que filtra UFW: `deny incoming` no basta para proteger un contenedor publicado en `0.0.0.0`. No solucionar el problema deshabilitando la gestión de iptables de Docker, porque puede romper su aislamiento y conectividad. Véase [Docker y UFW](https://docs.docker.com/engine/network/packet-filtering-firewalls/#docker-and-ufw).

La mitigación de este proyecto es no publicar `db`/`backend`, enlazar el frontend estrictamente a `127.0.0.1` y recibir tráfico externo a través de Cloudflare Tunnel y Access. Exigir Docker Engine 28 o posterior: Docker documenta que versiones anteriores podían permitir acceso desde el mismo segmento L2 a puertos publicados en localhost. No habilitar enrutamiento directo a las subredes Docker. Véase [publicación de puertos y alcance de localhost](https://docs.docker.com/engine/network/port-publishing/).

Desde el host comprobar `docker compose ps` y `sudo ss -lntp`; si Docker no utiliza un proxy de usuario, confirmar también los bindings con `docker inspect`. Desde otro equipo de la LAN, comprobar que la IP LAN del servidor no acepta conexiones al puerto del frontend, 8000 ni 5432. Esta prueba remota es necesaria para verificar el aislamiento efectivo, no solo el YAML.

### Segmentar la red doméstica

Ubicar el servidor en una VLAN/segmento distinto de dispositivos domésticos, IoT e invitados. En el router/firewall entre segmentos, denegar acceso lateral por defecto, permitir SSH únicamente desde administración y habilitar las salidas necesarias del servidor hacia DNS, actualizaciones, backups y Cloudflare. No habilitar UPnP ni reglas automáticas de port-forwarding para el servidor. Una VLAN sin reglas entre segmentos no aporta por sí sola este aislamiento.

## Backups de PostgreSQL

Respaldar la base completa, incluidos esquema, datos y `alembic_version`. **La tabla `operations` conserva las claves históricas de deduplicación:** omitirla, truncarla o restaurar solo las tablas de negocio puede permitir repetir efectos ya confirmados. La conservación y reconciliación se justifican en el [ADR de idempotencia](adr/0002-idempotencia-offline.md#recuperación-y-conservación).

Los siguientes comandos usan las herramientas del propio contenedor PostgreSQL y no requieren publicar 5432 ni instalar clientes en el host. `pg_dump` obtiene una instantánea consistente de una base; el formato custom se restaura con `pg_restore`. No incluye roles/tablespaces globales del clúster. Para este stack, el usuario y la base se provisionan desde la configuración preservada; si se añadieron roles externos, respaldar también esos objetos con `pg_dumpall --globals-only`. Referencia: [pg_dump de PostgreSQL 17](https://www.postgresql.org/docs/17/app-pgdump.html).

Guardar el respaldo fuera del checkout, con permisos privados. Ejecutar este bloque como una unidad; el archivo parcial solo se renombra si el dump termina correctamente:

```bash
(
  set -euo pipefail
  umask 077
  BACKUP_DIR=/var/backups/hhl-erp
  install -d -m 700 "$BACKUP_DIR"
  BACKUP_NAME="hhl-$(date -u +%Y%m%dT%H%M%SZ)-$$.dump"
  BACKUP_FILE="$BACKUP_DIR/$BACKUP_NAME"
  docker compose exec -T db sh -ec '
    exec pg_dump --username="$POSTGRES_USER" --dbname="$POSTGRES_DB" --format=custom
  ' > "$BACKUP_FILE.partial"
  test -s "$BACKUP_FILE.partial"
  mv -- "$BACKUP_FILE.partial" "$BACKUP_FILE"
  docker compose exec -T db pg_restore --list < "$BACKUP_FILE" > "$BACKUP_FILE.toc"
  (cd "$BACKUP_DIR" && sha256sum "$BACKUP_NAME" > "$BACKUP_NAME.sha256")
  printf 'Backup creado: %s\n' "$BACKUP_FILE"
)
```

Provisionar previamente `BACKUP_DIR` con propietario del operador si no tiene permiso de crear directorios bajo `/var/backups`; no abrir permisos globales para resolverlo. Se usa `exec -T` para no asignar una pseudo-TTY al flujo del archivo, según [Compose exec](https://docs.docker.com/reference/cli/docker/compose/exec/). Un índice legible y un checksum no prueban una restauración completa.

Conservar copias cifradas fuera del servidor, con retención definida según el máximo de pérdida tolerable y acceso limitado. Respaldar además `.env` de forma cifrada, el commit desplegado y la configuración de Cloudflare/Access. El volumen persistente no reemplaza un backup, y copiar en caliente los archivos de `postgres_data` no sustituye este dump. Programar la ejecución en el servidor y ensayar la recuperación periódicamente; esta guía no instala un temporizador.

## Restauración y recuperación

### Ensayo en una base nueva

Usar primero una instancia/servidor de recuperación aislado con PostgreSQL 17, el commit correspondiente al respaldo y su configuración. No iniciar el túnel. Si el ensayo se hace en el servidor actual, crear una base **nueva**, `hhl_restore_check`, y comprobar que no coincide con `POSTGRES_DB`. No reutilizar ni borrar una base de ensayo existente sin revisar su contenido.

Seleccionar un archivo concreto y verificar su checksum antes de restaurar. Sustituir la ruta del ejemplo; no elegir automáticamente el backup más reciente:

```bash
(
  set -euo pipefail
  BACKUP_FILE=/var/backups/hhl-erp/hhl-FECHA-PID.dump
  test -s "$BACKUP_FILE"
  (cd "$(dirname -- "$BACKUP_FILE")" && sha256sum --check "$(basename -- "$BACKUP_FILE").sha256")
  docker compose exec -T db sh -ec '
    test "$POSTGRES_DB" != hhl_restore_check
    exec createdb --username="$POSTGRES_USER" --owner="$POSTGRES_USER" --template=template0 hhl_restore_check
  '
  docker compose exec -T db sh -ec '
    exec pg_restore --username="$POSTGRES_USER" --dbname=hhl_restore_check \
      --no-owner --no-privileges --single-transaction --exit-on-error
  ' < "$BACKUP_FILE"
  docker compose exec -T db sh -ec '
    exec psql --username="$POSTGRES_USER" --dbname=hhl_restore_check \
      --set=ON_ERROR_STOP=1 --command="SELECT version_num FROM alembic_version; SELECT count(*) AS operations_total FROM operations;"
  '
)
```

Comprobar cada código de salida y detenerse ante cualquier fallo; no continuar con una restauración parcial. `--single-transaction` hace atómica la restauración del contenido y `--no-owner --no-privileges` adapta los objetos al usuario creado para este despliegue. La creación de la base es un paso separado. Véanse [pg_restore](https://www.postgresql.org/docs/17/app-pgrestore.html) y [psql con ON_ERROR_STOP](https://www.postgresql.org/docs/17/app-psql.html).

Comparar cantidades de proyectos, gastos y operaciones con el corte esperado y revisar integridad de importes e identidades. Un `count(*)` correcto no acredita por sí solo integridad funcional. Antes de aceptar el backup, probar también con el código compatible las lecturas y la recuperación de una operación confirmada, en el entorno aislado y con identidad autorizada.

### Recuperar el servicio

En una recuperación real, detener las entradas y los escritores antes de cambiar datos; si aún es posible, generar primero un respaldo adicional del estado dañado para análisis:

```bash
docker compose --profile tunnel stop cloudflared frontend backend
```

Preferir restaurar en un servidor/volumen nuevo con la configuración recuperada y arrancar primero solo `db`. Así se conserva el volumen original para volver atrás. Si debe restaurarse la base configurada en una instancia ya provisionada, confirmar explícitamente que es el destino correcto, que no contiene datos a conservar y que está **vacía**. El siguiente comando escribe en `POSTGRES_DB`; no usarlo sobre la base productiva activa ni añadir `--clean` para forzar una restauración sobre datos existentes:

```bash
(
  set -euo pipefail
  BACKUP_FILE=/var/backups/hhl-erp/hhl-FECHA-PID.dump
  test -s "$BACKUP_FILE"
  (cd "$(dirname -- "$BACKUP_FILE")" && sha256sum --check "$(basename -- "$BACKUP_FILE").sha256")
  docker compose up -d --wait db
  docker compose exec -T db sh -ec '
    exec pg_restore --username="$POSTGRES_USER" --dbname="$POSTGRES_DB" \
      --no-owner --no-privileges --single-transaction --exit-on-error
  ' < "$BACKUP_FILE"
)
```

No iniciar el backend antes de restaurar: su arranque aplicaría migraciones sobre el destino vacío. Tras una restauración exitosa, verificar el esquema, `operations` y los datos de negocio como en el ensayo, reconstruir las imágenes del commit elegido y levantar solo la aplicación local:

```bash
docker compose build backend frontend
docker compose up -d --wait db backend frontend
docker compose logs --tail=100 backend frontend
```

El backend aplicará las migraciones pendientes de ese commit; revisar antes su compatibilidad con el respaldo. Validar los flujos permitidos y el aislamiento desde la LAN. Reactivar `cloudflared` solo después de estas comprobaciones y de revisar la política de Access, usando el comando de activación de [operación Compose](#operación-con-docker-compose).

Restaurar un backup anterior retrocede también `operations`. Los comandos confirmados después de su corte pueden haber perdido sus claves de deduplicación aunque los clientes conserven respuestas o envíos pendientes. Mantener el acceso cerrado y reconciliar ese intervalo y las colas antes de permitir reintentos; no asumir que restaurar una copia antigua garantiza la deduplicación de operaciones posteriores al backup.
