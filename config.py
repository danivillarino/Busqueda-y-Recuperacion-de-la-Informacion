#Configuración de MySQL y rutas compartidas por el proyecto.

import os


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
