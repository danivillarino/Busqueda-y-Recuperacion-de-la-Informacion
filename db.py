#Acceso a las tablas MySQL del índice invertido y del índice FULLTEXT.

from pathlib import Path

import mysql.connector

from config import MYSQL_CONFIG


# Modificadores de MATCH ... AGAINST permitidos. Se eligen de esta lista
# cerrada porque el modificador no puede enviarse como parámetro de la consulta.
MODOS_FULLTEXT = {
    "natural": "IN NATURAL LANGUAGE MODE",
    "booleano": "IN BOOLEAN MODE",
    "expansion": "IN NATURAL LANGUAGE MODE WITH QUERY EXPANSION",
}


def obtener_conexion():
    #Abre una conexión a la base configurada en las variables de entorno.
    return mysql.connector.connect(**MYSQL_CONFIG)


def _ejecutar(consulta, parametros=(), modo=None):
    #Ejecuta una consulta y cierra sus recursos, propagando cualquier error.
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute(consulta, parametros)
        if modo == "uno":
            return cursor.fetchone()
        if modo == "todos":
            return cursor.fetchall()
        conexion.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conexion.close()


def crear_tablas():
    #Ejecuta las sentencias de esquema.sql en la base configurada.
    ruta_esquema = Path(__file__).with_name("esquema.sql")
    contenido = ruta_esquema.read_text(encoding="utf-8")
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        for sentencia in contenido.split(";"):
            if sentencia.strip():
                cursor.execute(sentencia)
        _agregar_columna_fulltext(cursor)
        _terminos_sensibles_a_acentos(cursor)
        conexion.commit()
    finally:
        cursor.close()
        conexion.close()


def _agregar_columna_fulltext(cursor):
    #Actualiza una tabla documentos creada con el esquema anterior (sin texto).
    cursor.execute(
        """
        SELECT COUNT(*) FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'documentos' AND COLUMN_NAME = 'contenido'
        """
    )
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "ALTER TABLE documentos ADD COLUMN contenido MEDIUMTEXT NOT NULL"
        )

    cursor.execute(
        """
        SELECT COUNT(*) FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'documentos'
          AND INDEX_NAME = 'ft_documentos_contenido'
        """
    )
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "ALTER TABLE documentos "
            "ADD FULLTEXT KEY ft_documentos_contenido (contenido)"
        )


def _terminos_sensibles_a_acentos(cursor):
    #Usa comparación binaria en termino para tablas creadas con el esquema anterior.
    #
    #Con utf8mb4_general_ci MySQL considera iguales "busqueda" y "búsqueda",
    #mientras que el indexador los cuenta como términos distintos; eso
    #provocaba claves duplicadas en diccionario.
    cursor.execute(
        """
        SELECT COUNT(*) FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE() AND COLUMN_NAME = 'termino'
          AND TABLE_NAME IN ('diccionario', 'posting')
          AND COLLATION_NAME <> 'utf8mb4_bin'
        """
    )
    if cursor.fetchone()[0] == 0:
        return
    # MySQL no permite cambiar una columna usada en una llave foránea, así que
    # se quita la FK, se cambian ambas columnas y se vuelve a crear.
    tipo = "VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL"
    cursor.execute("DELETE FROM posting")
    cursor.execute("DELETE FROM diccionario")
    cursor.execute(
        """
        SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'posting'
          AND CONSTRAINT_NAME = 'fk_posting_termino'
        """
    )
    if cursor.fetchone()[0]:
        cursor.execute("ALTER TABLE posting DROP FOREIGN KEY fk_posting_termino")
    cursor.execute(f"ALTER TABLE diccionario MODIFY termino {tipo}")
    cursor.execute(
        f"""
        ALTER TABLE posting
            MODIFY termino {tipo},
            ADD CONSTRAINT fk_posting_termino
                FOREIGN KEY (termino) REFERENCES diccionario (termino)
                ON DELETE CASCADE
        """
    )


def limpiar_indice():
    #Elimina los registros del índice en orden compatible con las FK.
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM posting")
        cursor.execute("DELETE FROM diccionario")
        cursor.execute("DELETE FROM documentos")
        conexion.commit()
    finally:
        cursor.close()
        conexion.close()


def insertar_documento(nombre_archivo, contenido=""):
    #Inserta un documento con su texto completo y devuelve el doc_id asignado.
    return _ejecutar(
        "INSERT INTO documentos (nombre_archivo, contenido) VALUES (%s, %s)",
        (nombre_archivo, contenido),
    )


def insertar_diccionario(termino, num_docs, total_frecuencias):
    #Inserta un término en el diccionario.
    _ejecutar(
        """
        INSERT INTO diccionario (termino, num_docs, total_frecuencias)
        VALUES (%s, %s, %s)
        """,
        (termino, num_docs, total_frecuencias),
    )


def insertar_posting(termino, doc_id, frecuencia, nombre_archivo, fragmento):
    _ejecutar(
        """
        INSERT INTO posting
            (termino, doc_id, frecuencia, nombre_archivo, fragmento)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (termino, doc_id, frecuencia, nombre_archivo, fragmento),
    )


def obtener_total_documentos():
    fila = _ejecutar("SELECT COUNT(*) FROM documentos", modo="uno")
    return fila[0]


def obtener_diccionario_termino(termino):
    return _ejecutar(
        """
        SELECT num_docs, total_frecuencias
        FROM diccionario
        WHERE termino = %s
        """,
        (termino,),
        modo="uno",
    )


def obtener_posting_termino(termino):
    filas = _ejecutar(
        """
        SELECT doc_id, frecuencia, nombre_archivo, fragmento
        FROM posting
        WHERE termino = %s
        ORDER BY doc_id
        """,
        (termino,),
        modo="todos",
    )
    return list(filas)


def obtener_postings_documento(doc_id):
    filas = _ejecutar(
        """
        SELECT termino, frecuencia
        FROM posting
        WHERE doc_id = %s
        ORDER BY termino
        """,
        (doc_id,),
        modo="todos",
    )
    return list(filas)


def obtener_resultados_fulltext(consulta, modo="natural"):
    #Devuelve [(nombre_archivo, contenido, relevancia)] ordenados por MySQL.
    #
    #MATCH ... AGAINST calcula la relevancia con el índice FULLTEXT; el mismo
    #predicado en WHERE descarta los documentos sin coincidencias y ORDER BY
    #produce el ranking. Los empates se resuelven por nombre de archivo.
    modificador = MODOS_FULLTEXT[modo]
    filas = _ejecutar(
        f"""
        SELECT nombre_archivo, contenido,
               MATCH (contenido) AGAINST (%s {modificador}) AS relevancia
        FROM documentos
        WHERE MATCH (contenido) AGAINST (%s {modificador})
        ORDER BY relevancia DESC, nombre_archivo ASC
        """,
        (consulta, consulta),
        modo="todos",
    )
    return list(filas)
