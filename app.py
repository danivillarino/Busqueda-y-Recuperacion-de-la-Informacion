"""Aplicación web para cargar documentos y consultar el índice."""

from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

from config import CARPETA_ARCHIVOS


app = Flask(__name__)
UPLOAD_FOLDER = Path(app.root_path, CARPETA_ARCHIVOS).resolve()
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)


@app.route("/", methods=["GET", "POST"])
def cargar_archivos():
    if request.method == "GET":
        return render_template("cargar.html")

    archivos = request.files.getlist("archivos")
    archivos_validos = []
    nombres = set()

    for archivo in archivos:
        if not archivo.filename:
            continue
        if not archivo.filename.lower().endswith(".txt"):
            return render_template(
                "cargar.html",
                error="Solo se permiten archivos con extensión .txt.",
            ), 400

        nombre = secure_filename(archivo.filename)
        if not nombre or not nombre.lower().endswith(".txt"):
            return render_template(
                "cargar.html",
                error="No se pudo usar uno de los nombres de archivo.",
            ), 400
        if nombre.casefold() in nombres:
            return render_template(
                "cargar.html",
                error="La selección contiene nombres de archivo duplicados.",
            ), 400

        nombres.add(nombre.casefold())
        archivos_validos.append((archivo, nombre))

    if not archivos_validos:
        return render_template(
            "cargar.html",
            error="Selecciona al menos un archivo .txt.",
        ), 400

    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    for archivo, nombre in archivos_validos:
        archivo.save(UPLOAD_FOLDER / nombre)

    from indexador import indexar_coleccion

    indexar_coleccion(str(UPLOAD_FOLDER))
    return render_template(
        "cargar.html",
        mensaje=f"Se cargaron e indexaron {len(archivos_validos)} archivo(s).",
    )


@app.route("/buscar", methods=["GET", "POST"])
def pagina_busqueda():
    if request.method == "GET" and "consulta" not in request.args:
        return render_template("buscar.html")

    consulta = request.values.get("consulta", "").strip()
    if not consulta:
        return render_template(
            "buscar.html",
            error="Escribe un término o una frase para buscar.",
        ), 400

    return resultados(consulta)


def resultados(consulta):
    from buscador import buscar

    encontrados = buscar(consulta)
    return render_template(
        "resultados.html",
        consulta=consulta,
        resultados=encontrados,
    )


@app.route("/descargar/<nombre>")
def descargar(nombre):
    if secure_filename(nombre) != nombre or not nombre.lower().endswith(".txt"):
        abort(404)
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        nombre,
        as_attachment=True,
    )


if __name__ == "__main__":
    app.run()
