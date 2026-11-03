# Persona 1: implementar aqui las funciones de acceso a MySQL.
# obtener_conexion() devuelve una conexion; crear_tablas() ejecuta esquema.sql.
# limpiar_indice() vacia documentos, diccionario y posting antes de indexar.
# insertar_documento(nombre_archivo) devuelve doc_id.
# insertar_diccionario(termino, num_docs, total_frecuencias).
# insertar_posting(termino, doc_id, frecuencia, nombre_archivo, fragmento).
# obtener_total_documentos() devuelve N.
# obtener_diccionario_termino(termino) devuelve (num_docs, total_frecuencias)
# o None; obtener_posting_termino(termino) devuelve las filas del termino.
# obtener_postings_documento(doc_id) devuelve pares (termino, frecuencia).
# Usar consultas parametrizadas y documentar la creacion de la base y el usuario.
