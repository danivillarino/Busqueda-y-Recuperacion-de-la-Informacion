# Persona 3: implementar aqui la ponderacion tf-idf y la busqueda.
# Funciones requeridas: calcular_idf(N, df), calcular_tf(frecuencia),
# construir_vector_consulta(tokens), construir_vector_documento(doc_id),
# norma(vector), similitud_coseno(vec_a, vec_b) y buscar(consulta).
# Usar idf = log10(N / df), peso = tf * idf y calcular coseno manualmente.
# Reutilizar tokenizar y quitar_stopwords de indexador.py.
# Definir y mantener un unico criterio para tf. Contemplar consulta vacia,
# termino inexistente y vectores con norma cero. Ordenar resultados de mayor
# a menor y devolver (nombre_archivo, fragmento, coseno).
# Usar unicamente las bibliotecas permitidas por el documento del equipo.
