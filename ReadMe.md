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
- Módulo de indexación `indexador.py`: lectura UTF-8/latin-1, tokenización,
  stopwords en español, frecuencias, fragmentos e índice invertido.
- Módulo de búsqueda `buscador.py`: pesos tf-idf, normas, similitud coseno,
  ranking descendente y casos límite (consulta vacía, término inexistente,
  normas cero).

Con la base de datos configurada, el flujo de carga, indexación y búsqueda está
implementado.

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

## Probar la aplicación

Desde la terminal en la que configuraste las variables de MySQL, inicia el
servidor:

```powershell
py app.py
```

1. Abre <http://127.0.0.1:5000/> y carga los cuatro archivos `.txt` de
   `datos_prueba/`. La página debe confirmar que fueron indexados.
2. Usa **Buscar** y prueba, por ejemplo, `energia renovable` y
   `recuperacion informacion`. Deben aparecer documentos pertinentes, con un
   fragmento de hasta 50 caracteres y una similitud entre 0 y 1.
3. Abre un enlace de resultado: debe descargarse el documento correspondiente.
4. Vuelve a cargar los mismos archivos y busca otra vez. La carga reconstruye
   el índice; no debe duplicar documentos ni postings.

Los archivos de la colección se guardan en `archivos_subidos/`. Cada carga
reconstruye el índice completo en la base de datos, según el contrato del
proyecto.

Para comprobar las tablas en phpMyAdmin, ejecuta:

```sql
SELECT COUNT(*) AS documentos FROM documentos;
SELECT COUNT(*) AS terminos FROM diccionario;
SELECT COUNT(*) AS postings FROM posting;

SELECT termino, num_docs, total_frecuencias
FROM diccionario
WHERE termino IN ('energia', 'informacion');
```

Con los cuatro documentos de ejemplo debe haber 4 filas en `documentos`; las
otras tablas deben contener términos y postings. En `diccionario`, `num_docs`
cuenta los documentos que contienen el término y `total_frecuencias` suma sus
apariciones en toda la colección.

Para verificar la lectura y normalización sin iniciar Flask:

```powershell
py -c "from indexador import leer_archivo, tokenizar, quitar_stopwords, contar_frecuencias, extraer_fragmento; from pathlib import Path; p=Path('datos_prueba/energia_renovable.txt'); texto=leer_archivo(p); tokens=quitar_stopwords(tokenizar(texto)); print('Lectura:', bool(texto)); print('Tokens:', tokens[:10]); print('Frecuencias:', contar_frecuencias(tokens)); print('Fragmento <= 50:', len(extraer_fragmento(texto, 'energia')) <= 50)"
```

Para probar ambas codificaciones con texto acentuado, crea dos archivos de
prueba desde PowerShell:

```powershell
py -c "from pathlib import Path; texto='Árbol, corazón y energía.'; Path('datos_prueba/prueba_utf8.txt').write_text(texto, encoding='utf-8'); Path('datos_prueba/prueba_latin1.txt').write_bytes(texto.encode('latin-1'))"
```

Cárgalos desde la aplicación y busca `corazón` o `energía`; ambos documentos
deben aparecer. Puedes borrar esos dos archivos de `datos_prueba/` después de
probarlos.

## Estructura principal

```text
app.py                  Aplicación Flask y rutas
config.py               Configuración de MySQL y rutas
db.py                   Acceso a datos MySQL/MariaDB
esquema.sql             Definición de las tablas
indexador.py            Lectura e indexación de documentos (pendiente)
buscador.py             Búsqueda tf-idf (implementado)
templates/              Vistas HTML de la aplicación
static/css/style.css    Estilos de la interfaz
archivos_subidos/       Colección cargada por la aplicación
datos_prueba/           Documentos de ejemplo para probar
```