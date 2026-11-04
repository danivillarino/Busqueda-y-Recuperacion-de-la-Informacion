"""Lectura, normalización e indexación de documentos de texto."""

import os
import re
from collections import Counter

from config import LONGITUD_FRAGMENTO
from db import (
    insertar_diccionario,
    insertar_documento,
    insertar_posting,
    limpiar_indice,
)


_PATRON_TERMINOS = re.compile(r"[^\W_]+", re.UNICODE)
_STOPWORDS = frozenset(
    """
    a al algo algunas algunos ante antes como con contra cual cuando de del desde
    donde durante e el ella ellas ellos en entre era erais eran eras eres es esa
    esas ese eso esos esta estaba estabais estaban estabas estad estamos estan
    estar estara estaran estas este esto estos estoy estuvo ex ha habia habiais
    habian habias han hasta hay haya he hemos hicieron hizo la las le les lo los
    mas me mi mis mucha muchas mucho muchos muy nada ni no nos nosotros nuestra
    nuestras nuestro nuestros o os otra otras otro otros para pero poco por
    porque que quien quienes se sea seais sean seas ser sera seran si sido siendo
    sin sobre sois somos son soy su sus te teneis tenemos tener tengo teneis
    tenemos tiene tienen tienes todo todos tu tus un una unas uno unos vosotras
    vosotros y ya yo
    á él más mí sí tú
    """.split()
)


def leer_archivo(ruta):
    """Lee un archivo UTF-8 y, si no es válido, intenta decodificarlo como latin-1."""
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            return archivo.read()
    except UnicodeDecodeError:
        with open(ruta, "r", encoding="latin-1") as archivo:
            return archivo.read()


def tokenizar(texto):
    """Devuelve palabras y números en minúsculas, sin signos de puntuación."""
    return _PATRON_TERMINOS.findall(texto.lower())


def quitar_stopwords(tokens):
    """Filtra las palabras vacías comunes del español."""
    return [token for token in tokens if token not in _STOPWORDS]


def contar_frecuencias(tokens):
    """Devuelve un diccionario con la frecuencia de cada término."""
    return dict(Counter(tokens))


def extraer_fragmento(texto, termino):
    """Extrae hasta 50 caracteres alrededor de la primera aparición del término."""
    limite = min(LONGITUD_FRAGMENTO, 50)
    if limite <= 0:
        return ""

    posicion = texto.lower().find(termino.lower()) if termino else -1
    if posicion < 0:
        return texto[:limite]

    inicio = max(0, posicion - max((limite - len(termino)) // 2, 0))
    fin = min(len(texto), inicio + limite)
    inicio = max(0, fin - limite)
    return texto[inicio:fin]


def indexar_coleccion(carpeta):
    """Reconstruye el índice invertido con los archivos .txt de una carpeta."""
    nombres = sorted(os.listdir(carpeta), key=str.casefold)
    documentos = []
    estadisticas = {}

    for nombre in nombres:
        ruta = os.path.join(carpeta, nombre)
        if not nombre.lower().endswith(".txt") or not os.path.isfile(ruta):
            continue

        texto = leer_archivo(ruta)
        frecuencias = contar_frecuencias(
            quitar_stopwords(tokenizar(texto))
        )
        documentos.append((nombre, texto, frecuencias))

        for termino, frecuencia in frecuencias.items():
            datos = estadisticas.setdefault(termino, [0, 0])
            datos[0] += 1
            datos[1] += frecuencia

    limpiar_indice()

    documentos_indexados = []
    for nombre, texto, frecuencias in documentos:
        doc_id = insertar_documento(nombre)
        documentos_indexados.append((doc_id, nombre, texto, frecuencias))

    for termino in sorted(estadisticas):
        num_docs, total_frecuencias = estadisticas[termino]
        insertar_diccionario(termino, num_docs, total_frecuencias)

    for doc_id, nombre, texto, frecuencias in documentos_indexados:
        for termino, frecuencia in frecuencias.items():
            insertar_posting(
                termino,
                doc_id,
                frecuencia,
                nombre,
                extraer_fragmento(texto, termino),
            )
