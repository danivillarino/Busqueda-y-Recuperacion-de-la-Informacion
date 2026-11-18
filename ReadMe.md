# Proyecto de indización y búsqueda con FULLTEXT

Aplicación web en Python y Flask para cargar documentos `.txt` y buscarlos por
relevancia. Esta versión agrega a la actividad anterior (índice invertido con
tf-idf) un segundo buscador basado en los índices **FULLTEXT** de
MySQL/MariaDB, y permite comparar ambos sistemas desde la interfaz.

# Integrantes del equipo:
- Baeza Estrella Andrea
- Gómez Manzanero Erick Gilberto
- Magaña Mis Marco Antonio
- Villarino Budip Daniela

## Qué cambió respecto a "Indización y búsqueda"

- **Texto completo en la base de datos.** La tabla `documentos` tiene una
  columna `contenido MEDIUMTEXT` con un índice `FULLTEXT`
  (`ft_documentos_contenido`). Cada vez que se carga una colección,
  `indexar_coleccion` guarda ahí el texto de cada archivo.
- **Relevancia y ranking con funciones de MySQL.** `buscador_fulltext.py`
  sustituye el cálculo manual de tf-idf, normas y coseno por
  `MATCH (contenido) AGAINST (...)`. La consulta está en
  `db.obtener_resultados_fulltext`:

  ```sql
  SELECT nombre_archivo, contenido,
         MATCH (contenido) AGAINST (%s IN NATURAL LANGUAGE MODE) AS relevancia
  FROM documentos
  WHERE MATCH (contenido) AGAINST (%s IN NATURAL LANGUAGE MODE)
  ORDER BY relevancia DESC, nombre_archivo ASC
  ```

  Se pueden elegir los tres modos de búsqueda de texto completo: lenguaje
  natural, booleano (`+palabra`, `-palabra`, `"frase"`, `prefijo*`) y
  lenguaje natural con expansión de consulta.
- **El buscador tf-idf se conserva** (`buscador.py`, tablas `diccionario` y
  `posting`) para poder comparar. En la página **Buscar** se elige el sistema:
  FULLTEXT, tf-idf o **Comparar ambos**, que muestra los dos rankings lado a
  lado.
- **Corrección:** la columna `termino` de `diccionario` y `posting` ahora usa
  `utf8mb4_bin`. Con la colación anterior MySQL consideraba iguales
  `busqueda` y `búsqueda`, el indexador los contaba como términos distintos y
  la carga fallaba con "Duplicate entry".
- Se agregó `datos_prueba/motores_busqueda.txt`, con acentos, para probar
  esa diferencia entre sistemas.

## Requisitos

- Python 3.10 o posterior.
- MySQL 5.6+ o MariaDB 10.0+ (índices FULLTEXT en InnoDB). XAMPP proporciona
  MariaDB; inicia el servicio **MySQL** desde el panel de XAMPP.
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

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES
  ON indice_busqueda.* TO 'indice_app'@'localhost';
```

Si ya tienes la base de la actividad anterior, no repitas los `CREATE`; solo
ejecuta el `GRANT` para agregar los permisos `ALTER` e `INDEX`, que se
necesitan para actualizar la tabla `documentos`.

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
variables configuradas así duran mientras esa ventana siga abierta.

Como alternativa, copia `.env.example` como `.env` y escribe ahí tus valores:
`config.py` lo carga automáticamente al iniciar. Las variables definidas en la
terminal tienen prioridad sobre las del `.env`. El archivo `.env` está en
`.gitignore`; no subas contraseñas reales al repositorio.

Crea las tablas (o actualiza las de la actividad anterior) desde la carpeta
del proyecto:

```powershell
py -c "import db; db.crear_tablas(); print('Tablas listas')"
```

`crear_tablas()` crea las tablas que falten y, si `documentos` viene de la
versión anterior, le agrega la columna `contenido` con su índice FULLTEXT y
cambia `termino` a `utf8mb4_bin`. Se puede ejecutar varias veces.

## Probar la aplicación

Desde la terminal en la que configuraste las variables de MySQL, inicia el
servidor:

```powershell
py app.py
```

1. Abre <http://127.0.0.1:5000/> y carga los cinco archivos `.txt` de
   `datos_prueba/`. La página debe confirmar que fueron indexados.
2. En **Buscar**, deja el sistema **FULLTEXT de MySQL** y prueba
   `recuperacion informacion`. Deben aparecer documentos con enlace, un
   fragmento de hasta 50 caracteres y su relevancia `MATCH … AGAINST`.
3. Prueba el modo **Booleano** con `energ*` (prefijo) o
   `"recuperacion de informacion"` (frase exacta).
4. Elige **Comparar ambos sistemas** y busca `busqueda`: FULLTEXT encuentra
   también `motores_busqueda.txt`, que escribe la palabra con acento; tf-idf
   no.
5. Abre un enlace de resultado: debe descargarse el documento.

Para comprobar el índice FULLTEXT en phpMyAdmin:

```sql
SELECT doc_id, nombre_archivo, CHAR_LENGTH(contenido) AS caracteres
FROM documentos;

SELECT nombre_archivo,
       MATCH (contenido) AGAINST ('energia renovable') AS relevancia
FROM documentos
WHERE MATCH (contenido) AGAINST ('energia renovable')
ORDER BY relevancia DESC;
```

## Comparación de ambos sistemas

Resultados con los cinco documentos de `datos_prueba/` en MariaDB 10.4
(XAMPP), modo de lenguaje natural salvo donde se indica:

| Consulta | FULLTEXT (relevancia) | tf-idf (coseno) |
| --- | --- | --- |
| `energia renovable` | energia_renovable 0.6334 | energia_renovable 0.4374 |
| `recuperacion informacion` | recuperacion_informacion 0.1646; aprendizaje_automatico y energia_renovable empatados en 0.0063 | recuperacion_informacion 0.2959; energia_renovable 0.0262; aprendizaje_automatico 0.0261 |
| `busqueda` | 3 documentos, incluido motores_busqueda (dice "búsqueda") | 2 documentos; no encuentra "búsqueda" |
| `búsqueda` | Los mismos 3 documentos | Solo motores_busqueda |
| `energ*` (booleano) | energia_renovable | Sin resultados: no tiene operadores |
| `"recuperacion de informacion"` (booleano) | Solo el documento con la frase exacta | Los 3 documentos con alguna de las palabras |
| `ecosistemas` (con expansión) | Los 5 documentos: la expansión agrega términos y, con una colección tan pequeña, mete ruido | Solo ecosistemas |
| Tiempo medio por consulta | ≈ 26 ms | ≈ 365 ms |

**Ventajas de FULLTEXT**

- Menos código propio: el servidor tokeniza, mantiene el índice al insertar y
  calcula relevancia y ranking. Ya no hace falta mantener `diccionario` ni
  `posting` para buscar.
- Más rápido: una sola consulta SQL. El buscador tf-idf hace muchas
  consultas pequeñas (diccionario y postings de cada documento candidato),
  así que parte de la diferencia se debe a cómo lo implementamos y no solo
  al método.
- Ignora acentos y mayúsculas gracias a la colación (`busqueda` = `búsqueda`).
- Ofrece búsqueda booleana, frases exactas, prefijos y expansión de consulta.

**Ventajas de tf-idf propio**

- Es transparente: conocemos y controlamos cada fórmula
  (`tf = 1 + log10(f)`, `idf = log10(N/df)`, coseno).
- El coseno está normalizado entre 0 y 1 y considera la longitud del
  documento; la relevancia de FULLTEXT no tiene escala fija (con expansión
  llegó a 2.97) y produjo empates que el coseno sí distinguió.
- Usa nuestra lista de stopwords en español. InnoDB trae por defecto una
  lista en inglés e ignora palabras de menos de 3 caracteres
  (`innodb_ft_min_token_size`).
- No depende del motor de base de datos: la fórmula sería la misma con
  otro gestor.

**¿Cuál es mejor?** Para una aplicación real consideramos mejor **FULLTEXT**:
da resultados equivalentes en las consultas simples (el mismo documento queda
primero en todas las pruebas), es más de diez veces más rápido en nuestra
implementación, tolera acentos y agrega operadores de búsqueda sin escribir
código. El tf-idf propio sigue siendo valioso para entender cómo se calcula la
relevancia y cuando se necesita controlar el modelo (stopwords en español,
puntajes normalizados), pero mantenerlo y optimizarlo cuesta más que usar lo
que ya ofrece el gestor.

## Estructura principal

```text
app.py                  Aplicación Flask y rutas
config.py               Configuración de MySQL y rutas
db.py                   Acceso a datos MySQL/MariaDB y consulta FULLTEXT
esquema.sql             Definición de las tablas e índice FULLTEXT
indexador.py            Lectura e indexación (texto completo + índice invertido)
buscador_fulltext.py    Búsqueda con MATCH … AGAINST
buscador.py             Búsqueda tf-idf y coseno (actividad anterior)
templates/              Vistas HTML (comparar.html muestra ambos rankings)
static/css/style.css    Estilos de la interfaz
archivos_subidos/       Colección cargada por la aplicación
datos_prueba/           Documentos de ejemplo para probar
CapturaFulltext.png     Captura de una búsqueda FULLTEXT
CapturaComparacion.png  Captura de la comparación de ambos sistemas
```
