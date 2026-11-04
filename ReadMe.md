# Proyecto de indización y búsqueda

Aplicación web en Python y Flask para cargar documentos `.txt`, construir un
índice invertido en MySQL/MariaDB y buscar documentos por relevancia.

## Estado actual

Ya están implementados:

- Interfaz Flask para cargar archivos `.txt`, hacer consultas y descargar los
  documentos cargados.
- Validación de extensión y nombre de archivo durante la carga.
- Plantillas HTML y estilos en `static/css/style.css`.
- Configuración de conexión y operaciones de base de datos en `config.py` y
  `db.py`.
- Esquema de las tablas `documentos`, `diccionario` y `posting` en
  `esquema.sql`.
- Cuatro documentos de ejemplo en `datos_prueba/`.

**Pendiente para que funcione el flujo completo:** `indexador.py` y
`buscador.py` todavía contienen indicaciones, no implementaciones. Por eso la
interfaz puede abrirse, pero cargar archivos e iniciar una búsqueda requieren
que se completen e integren esos módulos.

## Requisitos

- Python 3.10 o posterior.
- MySQL o MariaDB. XAMPP puede proporcionar MariaDB; inicia el servicio
  **MySQL** desde el panel de XAMPP.
- Dependencias de Python declaradas en `requirements.txt`.

## Instalación

Desde la carpeta del proyecto, instala las dependencias:

```powershell
py -m pip install -r requirements.txt
```

## Preparar la base de datos

En phpMyAdmin (`http://localhost/phpmyadmin`), abre la pestaña **SQL** y crea
una base y un usuario para el proyecto. Cambia la contraseña de ejemplo por
una propia:

```sql
CREATE DATABASE indice_busqueda
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'indice_app'@'localhost' IDENTIFIED BY 'CAMBIA_ESTA_CLAVE';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, REFERENCES
  ON indice_busqueda.* TO 'indice_app'@'localhost';
```

Si ya existe la base o el usuario, no repitas los comandos `CREATE`; usa
phpMyAdmin para conceder los permisos o actualizar la contraseña.

Configura las variables de conexión en la misma terminal desde la que ejecutarás
Python. En **PowerShell**:

```powershell
$env:MYSQL_HOST = "localhost"
$env:MYSQL_PORT = "3306"
$env:MYSQL_USER = "indice_app"
$env:MYSQL_PASSWORD = "TU_CONTRASEÑA"
$env:MYSQL_DATABASE = "indice_busqueda"
```

En **CMD**:

```cmd
set "MYSQL_HOST=localhost"
set "MYSQL_PORT=3306"
set "MYSQL_USER=indice_app"
set "MYSQL_PASSWORD=TU_CONTRASEÑA"
set "MYSQL_DATABASE=indice_busqueda"
```

Reemplaza `TU_CONTRASEÑA` por la contraseña elegida al crear el usuario. Las
variables configuradas así duran mientras esa ventana siga abierta. No subas
contraseñas reales al repositorio; `.env.example` solo muestra nombres y
valores de ejemplo y no se carga automáticamente.

Una vez creada la base, crea las tablas desde la carpeta del proyecto:

```powershell
py -c "import db; db.crear_tablas(); print('Tablas creadas')"
```

## Ejecutar la aplicación

Cuando `indexador.py` y `buscador.py` estén implementados, inicia el servidor:

```powershell
py app.py
```

Abre <http://127.0.0.1:5000/> en el navegador. Selecciona los archivos `.txt`
desde `datos_prueba/` en el formulario para cargarlos e indexarlos. Después usa
**Buscar** para consultar y los nombres de los resultados para descargar los
documentos.

Los archivos de la colección se guardan en `archivos_subidos/`. Al cargar una
colección, el indexador debe reconstruir el índice en la base de datos, según
el contrato del proyecto.

## Estructura principal

```text
app.py                  Aplicación Flask y rutas
config.py               Configuración de MySQL y rutas
db.py                   Acceso a datos MySQL/MariaDB
esquema.sql             Definición de las tablas
indexador.py            Lectura e indexación de documentos (pendiente)
buscador.py             Búsqueda tf-idf (pendiente)
templates/              Vistas HTML de la aplicación
static/css/style.css    Estilos de la interfaz
archivos_subidos/       Colección cargada por la aplicación
datos_prueba/           Documentos de ejemplo para probar
```