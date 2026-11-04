#Acceso a las tablas MySQL del índice invertido.

from pathlib import Path

import mysql.connector

from config import MYSQL_CONFIG


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
        conexion.commit()
    finally:
        cursor.close()
        conexion.close()


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


def insertar_documento(nombre_archivo):
    #Inserta un documento y devuelve el doc_id asignado por MySQL.
    return _ejecutar(
        "INSERT INTO documentos (nombre_archivo) VALUES (%s)",
        (nombre_archivo,),
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
