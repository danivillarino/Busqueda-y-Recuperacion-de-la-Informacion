#Configuración de MySQL y rutas compartidas por el proyecto.

import os
from pathlib import Path


def _cargar_env():
    #Carga variables de un archivo .env local sin sobrescribir las ya definidas.
    ruta = Path(__file__).with_name(".env")
    if not ruta.is_file():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


_cargar_env()


CARPETA_ARCHIVOS = "archivos_subidos"
LONGITUD_FRAGMENTO = 50

MYSQL_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "port": int(os.environ.get("MYSQL_PORT", "3306")),
    "user": os.environ.get("MYSQL_USER", "indice_app"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DATABASE", "indice_busqueda"),
    "charset": "utf8mb4",
}
