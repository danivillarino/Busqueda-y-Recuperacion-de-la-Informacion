"""Búsqueda por relevancia con el índice FULLTEXT de MySQL/MariaDB.

Sustituye el cálculo manual de tf-idf, normas y coseno de `buscador.py` por
las funciones de búsqueda de texto completo del servidor: MATCH ... AGAINST
calcula la relevancia y ORDER BY produce el ranking (ver
`db.obtener_resultados_fulltext`).
"""

from db import MODOS_FULLTEXT, obtener_resultados_fulltext
from indexador import buscar_posicion, extraer_fragmento, quitar_stopwords, tokenizar


MODOS = tuple(MODOS_FULLTEXT)


def _terminos_fragmento(consulta):
    """Términos de la consulta útiles para ubicar el fragmento.

    En modo booleano se omiten las palabras excluidas con `-`, porque no
    aparecen en los documentos devueltos.
    """
    excluidos = {
        termino
        for palabra in consulta.split()
        if palabra.startswith("-")
        for termino in tokenizar(palabra)
    }
    tokens = tokenizar(consulta)
    return [t for t in quitar_stopwords(tokens) or tokens if t not in excluidos]


def _fragmento(texto, terminos):
    """Fragmento de 50 caracteres alrededor del primer término que aparece."""
    for termino in terminos:
        if buscar_posicion(texto, termino) >= 0:
            return extraer_fragmento(texto, termino)
    # Con expansión de consulta un documento puede coincidir solo por
    # términos añadidos por MySQL; se muestra el inicio del texto.
    return extraer_fragmento(texto, "")


def buscar_fulltext(consulta, modo="natural"):
    """Busca con MATCH ... AGAINST y devuelve [(nombre_archivo, fragmento, relevancia)].

    El orden lo decide MySQL: relevancia descendente y, en empates, nombre de
    archivo ascendente.
    """
    if modo not in MODOS_FULLTEXT:
        raise ValueError(f"Modo FULLTEXT desconocido: {modo}")
    if not consulta or not consulta.strip():
        return []

    terminos = _terminos_fragmento(consulta)
    return [
        (nombre_archivo, _fragmento(contenido, terminos), float(relevancia))
        for nombre_archivo, contenido, relevancia in obtener_resultados_fulltext(
            consulta.strip(), modo
        )
    ]
