# Proyecto de indizacion y busqueda

Carpeta base dividida segun las responsabilidades del documento del equipo.
Los archivos de codigo contienen comentarios de orientacion, no implementaciones.

Completar cada archivo siguiendo el contrato entre modulos. Respetar las
bibliotecas permitidas, los nombres de tablas y funciones, las rutas Flask y
las formulas tf-idf indicadas en el documento de trabajo.

Antes de entregar, agregar archivos .txt de prueba, verificar la integracion,
crear la captura captura.png y preparar el ZIP con el nombre acordado.

---
# División del trabajo: módulo de indización y búsqueda

Equipo de 4 personas · Entrega: 4 de noviembre · Archivo: `Apellido1Apellido2Apellido3Apellido4.zip`

## 1. Objetivo y restricciones

Aplicación web (Python + Flask + MySQL) que carga archivos `.txt`, genera el índice invertido de toda la carpeta del servidor y permite buscar. Los resultados muestran enlace de descarga, fragmento de 50 caracteres y similitud coseno, ordenados por relevancia tf-idf.

- Prohibido usar bibliotecas que calculen tf, idf o matrices (numpy, sklearn, pandas). Solo `math`, `re`, `collections`, `os`.
- Se permite Flask y un conector de MySQL (`mysql-connector-python` o `pymysql`).
- El índice se reconstruye completo cada vez que se carga una colección.
- Entregable: el proyecto y una captura de pantalla de una búsqueda, todo en un ZIP.

## 2. Estructura de carpetas

```
proyecto/
  app.py                 # Persona 4
  config.py              # Persona 1 (credenciales y rutas)
  db.py                  # Persona 1
  esquema.sql            # Persona 1
  indexador.py           # Persona 2
  buscador.py            # Persona 3
  templates/
    cargar.html          # Persona 4
    buscar.html          # Persona 4
    resultados.html      # Persona 4
  archivos_subidos/      # carpeta del servidor con los .txt
  captura.png
```

## 3. Nombres acordados (no cambiar sin avisar)

### Base de datos

- Base de datos: `indice_busqueda`
- Tabla `documentos`: `doc_id` (INT, PK, auto), `nombre_archivo` (VARCHAR 255, único)
- Tabla `diccionario`: `termino` (VARCHAR 100, PK), `num_docs` (INT), `total_frecuencias` (INT)
- Tabla `posting`: `termino` (VARCHAR 100), `doc_id` (INT), `frecuencia` (INT), `nombre_archivo` (VARCHAR 255), `fragmento` (VARCHAR 50); clave primaria compuesta (`termino`, `doc_id`)

### Rutas y constantes

- `CARPETA_ARCHIVOS = "archivos_subidos"`
- `LONGITUD_FRAGMENTO = 50`
- Rutas Flask: `/` (cargar), `/buscar` (consulta), `/descargar/<nombre>` (descarga)

## 4. Responsabilidades y funciones

### Persona 1: Base de datos (`db.py`, `esquema.sql`, `config.py`)

- `obtener_conexion()` devuelve una conexión a MySQL.
- `crear_tablas()` ejecuta el script `esquema.sql`.
- `limpiar_indice()` vacía `documentos`, `diccionario` y `posting` antes de reconstruir.
- `insertar_documento(nombre_archivo)` devuelve el `doc_id`.
- `insertar_diccionario(termino, num_docs, total_frecuencias)`
- `insertar_posting(termino, doc_id, frecuencia, nombre_archivo, fragmento)`
- `obtener_total_documentos()` devuelve N.
- `obtener_diccionario_termino(termino)` devuelve `(num_docs, total_frecuencias)` o `None`.
- `obtener_posting_termino(termino)` devuelve lista de `(doc_id, frecuencia, nombre_archivo, fragmento)`.
- `obtener_postings_documento(doc_id)` devuelve lista de `(termino, frecuencia)`; la necesita el buscador para la norma del documento.

También debe documentar cómo crear la base y el usuario en MySQL.

### Configuración de MySQL (Persona 1)

Instala el conector con `pip install mysql-connector-python`. Antes de iniciar
la aplicación, entra a MySQL como administrador y crea la base y el usuario
(cambia la contraseña de ejemplo por una segura):

```sql
CREATE DATABASE indice_busqueda
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
CREATE USER 'indice_app'@'localhost' IDENTIFIED BY 'CAMBIA_ESTA_CLAVE';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, REFERENCES
  ON indice_busqueda.* TO 'indice_app'@'localhost';
```

Configura las variables `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`,
`MYSQL_PASSWORD` y `MYSQL_DATABASE` en el entorno del proceso que ejecuta
Python. `.env.example` muestra los nombres y valores de referencia; no se carga
automáticamente. Mantén las credenciales reales fuera del repositorio.

Con la base de datos creada, ejecuta `crear_tablas()` desde `db.py` para generar
las tablas. El esquema puede volver a ejecutarse sin borrar los datos
existentes. `limpiar_indice()` elimina los registros actuales en el orden
adecuado antes de reconstruir el índice.

### Ejecutar la aplicación web (Persona 4)

Instala las dependencias con `py -m pip install -r requirements.txt`, configura
las variables de MySQL indicadas arriba en la misma terminal y ejecuta:

```powershell
py app.py
```

Abre `http://127.0.0.1:5000/` para cargar uno o varios `.txt`; la aplicación
guarda los archivos en `archivos_subidos/` e indexa la colección. Usa el enlace
**Buscar** para enviar una consulta. Los cuatro archivos de `datos_prueba/` se
pueden seleccionar desde el formulario. La ruta `/descargar/<nombre>` descarga
un documento de la colección.

### Persona 2: Indexador (`indexador.py`)

- `leer_archivo(ruta)` devuelve el texto (probar con `utf-8` y `latin-1`).
- `tokenizar(texto)` pasa a minúsculas, quita signos y devuelve lista de términos.
- `quitar_stopwords(tokens)` filtra una lista de stopwords en español.
- `contar_frecuencias(tokens)` devuelve `{termino: frecuencia}` con un diccionario de Python.
- `extraer_fragmento(texto, termino)` devuelve hasta 50 caracteres alrededor de la primera aparición del término.
- `indexar_coleccion(carpeta)` recorre los `.txt`, limpia el índice, procesa cada archivo y llena las tres tablas. Calcula `num_docs` y `total_frecuencias` por término.

Acordar con la Persona 1 si el fragmento se guarda por (término, documento), como se indica arriba.

### Persona 3: Buscador (`buscador.py`)

- `calcular_idf(N, df)` devuelve `math.log10(N / df)`.
- `calcular_tf(frecuencia)` devuelve la frecuencia, o `1 + log10(frecuencia)` si el equipo prefiere tf logarítmico (definirlo y mantenerlo).
- `construir_vector_consulta(tokens)` devuelve `{termino: peso tf-idf}`.
- `construir_vector_documento(doc_id)` devuelve `{termino: peso tf-idf}` usando `obtener_postings_documento`.
- `norma(vector)` devuelve la raíz de la suma de cuadrados.
- `similitud_coseno(vec_a, vec_b)` calcula producto punto entre producto de normas, a mano.
- `buscar(consulta)` devuelve una lista de `(nombre_archivo, fragmento, coseno)` ordenada de mayor a menor coseno. Para la consulta debe usar las mismas funciones `tokenizar` y `quitar_stopwords` del indexador.

Casos límite: consulta vacía, término inexistente (df = 0) y documentos con norma 0.

### Persona 4: Aplicación web e integración (`app.py`, `templates/`)

- `cargar_archivos()` recibe el formulario con varios `.txt`, los guarda en `archivos_subidos/` y llama a `indexar_coleccion(CARPETA_ARCHIVOS)`.
- `pagina_busqueda()` muestra el cuadro de búsqueda.
- `resultados()` llama a `buscar(consulta)` y muestra nombre con enlace, fragmento y coseno.
- `descargar(nombre)` usa `send_from_directory`.
- Validar que solo se acepten archivos `.txt` y usar `secure_filename`.
- Preparar 4 o 5 archivos de prueba, tomar la captura (`captura.png`), escribir un `README.md` breve con instrucciones y armar el ZIP.

## 5. Contrato entre módulos

| Función | Quién la implementa | Quién la usa |
| --- | --- | --- |
| `indexar_coleccion(carpeta)` | Persona 2 | Persona 4 |
| `buscar(consulta)` | Persona 3 | Persona 4 |
| `tokenizar`, `quitar_stopwords` | Persona 2 | Persona 3 |
| Funciones `obtener_*` de `db.py` | Persona 1 | Personas 3 y 4 |
| Funciones `insertar_*`, `limpiar_indice` | Persona 1 | Persona 2 |

## 6. Fórmulas a implementar

- `idf(t) = log10(N / df(t))`, con N = total de documentos y df = `num_docs` del diccionario.
- `peso(t, d) = tf(t, d) × idf(t)`
- `coseno(q, d) = Σ(q_i × d_i) / (‖q‖ × ‖d‖)`

## 7. Calendario sugerido

1. Hoy, primera hora: todos revisan este documento, fijan nombres de tablas y funciones, y crean el repositorio o la carpeta compartida.
2. Cada persona programa su módulo con datos de prueba propios.
3. Integración: Persona 4 conecta todo y el equipo prueba junto con los mismos archivos `.txt`.
4. Últimas horas: captura de pantalla, README, nombrar el ZIP correctamente y verificar que abre y corre.

## 8. Lista de verificación final

- [ ] Las tres tablas guardan todos los campos pedidos
- [ ] El índice se regenera al cargar una colección
- [ ] Los resultados muestran enlace, fragmento de 50 caracteres y coseno
- [ ] Orden descendente por relevancia
- [ ] Sin numpy, sklearn ni pandas
- [ ] Captura de pantalla incluida
- [ ] ZIP con el formato `Apellido1Apellido2Apellido3Apellido4.zip`
