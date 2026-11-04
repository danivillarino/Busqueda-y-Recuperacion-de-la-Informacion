"""Módulo buscador.

Calcula pesos tf-idf, normas y similitud coseno, y ordena los documentos
por relevancia para una consulta de texto.

Reutiliza la tokenización y las stopwords de `indexador.py` (Persona 2)
y las funciones de lectura de `db.py` (Persona 1).
"""

import math
from collections import Counter

from db import (
    obtener_diccionario_termino,
    obtener_posting_termino,
    obtener_postings_documento,
    obtener_total_documentos,
)
from indexador import quitar_stopwords, tokenizar


def calcular_idf(n_total, num_docs):
    """Devuelve idf = log10(N / df).

    Si los valores no permiten calcularlo (N o df no positivos), devuelve 0.0.
    """
    if n_total <= 0 or num_docs <= 0:
        return 0.0
    return math.log10(n_total / num_docs)


def calcular_tf(frecuencia):
    """Devuelve tf = 1 + log10(frecuencia).

    Se usa la misma definición para la consulta y para los documentos.
    Una frecuencia no positiva no aporta peso.
    """
    if frecuencia <= 0:
        return 0.0
    return 1.0 + math.log10(frecuencia)


def construir_vector_consulta(tokens):
    """Devuelve {termino: peso tf-idf} para los tokens de la consulta.

    Se espera que los tokens ya vengan normalizados y sin stopwords.
    Los términos que no existen en el diccionario (df = 0) se omiten.
    """
    if not tokens:
        return {}

    n_total = obtener_total_documentos()
    if n_total <= 0:
        return {}

    vector = {}
    for termino, frecuencia in Counter(tokens).items():
        datos = obtener_diccionario_termino(termino)
        if datos is None:
            continue

        num_docs, _total_frecuencias = datos
        idf = calcular_idf(n_total, num_docs)
        vector[termino] = calcular_tf(frecuencia) * idf

    return vector


def construir_vector_documento(doc_id):
    """Devuelve {termino: peso tf-idf} con todos los términos del documento.

    Se usan todos los términos (no solo los de la consulta) porque la norma
    del documento debe cubrir su vector completo.
    """
    postings = obtener_postings_documento(doc_id)
    if not postings:
        return {}

    n_total = obtener_total_documentos()
    if n_total <= 0:
        return {}

    vector = {}
    for termino, frecuencia in postings:
        datos = obtener_diccionario_termino(termino)
        if datos is None:
            continue

        num_docs, _total_frecuencias = datos
        idf = calcular_idf(n_total, num_docs)
        vector[termino] = calcular_tf(frecuencia) * idf

    return vector


def norma(vector):
    """Devuelve la norma euclidiana: raíz de la suma de los pesos al cuadrado."""
    return math.sqrt(sum(peso * peso for peso in vector.values()))


def similitud_coseno(vec_a, vec_b):
    """Devuelve el coseno entre dos vectores dispersos.

    Si alguna de las normas es 0, el coseno no está definido y se devuelve 0.0.
    """
    norma_a = norma(vec_a)
    norma_b = norma(vec_b)
    if norma_a == 0.0 or norma_b == 0.0:
        return 0.0

    # Producto punto recorriendo el vector más corto.
    if len(vec_a) > len(vec_b):
        vec_a, vec_b = vec_b, vec_a
    producto_punto = sum(
        peso * vec_b.get(termino, 0.0) for termino, peso in vec_a.items()
    )

    return producto_punto / (norma_a * norma_b)


def buscar(consulta):
    """Busca una consulta de texto y devuelve [(nombre_archivo, fragmento, coseno)].

    Los resultados se ordenan de mayor a menor coseno; los empates se resuelven
    por nombre de archivo ascendente para que el orden sea estable.
    """
    if not consulta or not consulta.strip():
        return []

    tokens = quitar_stopwords(tokenizar(consulta))
    vector_consulta = construir_vector_consulta(tokens)
    if not vector_consulta:
        return []

    # Documentos candidatos: los que contienen al menos un término de la
    # consulta. Se agrupan por doc_id para no repetir documentos y se guarda
    # el fragmento que aporta cada término.
    postings_por_doc = {}
    for termino in vector_consulta:
        for doc_id, _frecuencia, nombre_archivo, fragmento in obtener_posting_termino(termino):
            entrada = postings_por_doc.setdefault(
                doc_id,
                {"nombre_archivo": nombre_archivo, "fragmentos": {}},
            )
            entrada["fragmentos"][termino] = fragmento

    resultados = []
    for doc_id, datos in postings_por_doc.items():
        vector_documento = construir_vector_documento(doc_id)
        coseno = similitud_coseno(vector_consulta, vector_documento)

        # Fragmento del término de la consulta con mayor peso en el documento.
        termino_elegido = max(
            datos["fragmentos"],
            key=lambda termino: vector_documento.get(termino, 0.0),
        )
        resultados.append(
            (datos["nombre_archivo"], datos["fragmentos"][termino_elegido], coseno)
        )

    resultados.sort(key=lambda resultado: (-resultado[2], resultado[0]))
    return resultados
