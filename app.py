# Persona 4: implementar aqui la aplicacion Flask y su integracion.
# Rutas acordadas: / para cargar, /buscar para consultar y
# /descargar/<nombre> para descargar un archivo.
# La carga acepta solo .txt, usa secure_filename y llama a
# indexar_coleccion(CARPETA_ARCHIVOS) despues de guardar la coleccion.
# La busqueda llama a buscar(consulta) y envia nombre, fragmento y coseno
# a la plantilla de resultados. La descarga usa send_from_directory.
