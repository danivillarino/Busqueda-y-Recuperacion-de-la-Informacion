CREATE TABLE IF NOT EXISTS documentos (
    doc_id INT NOT NULL AUTO_INCREMENT,
    nombre_archivo VARCHAR(255) NOT NULL,
    contenido MEDIUMTEXT NOT NULL,
    PRIMARY KEY (doc_id),
    UNIQUE KEY uq_documentos_nombre_archivo (nombre_archivo),
    FULLTEXT KEY ft_documentos_contenido (contenido)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS diccionario (
    termino VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
    num_docs INT NOT NULL,
    total_frecuencias INT NOT NULL,
    PRIMARY KEY (termino)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS posting (
    termino VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
    doc_id INT NOT NULL,
    frecuencia INT NOT NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    fragmento VARCHAR(50) NOT NULL,
    PRIMARY KEY (termino, doc_id),
    CONSTRAINT fk_posting_termino
        FOREIGN KEY (termino) REFERENCES diccionario (termino)
        ON DELETE CASCADE,
    CONSTRAINT fk_posting_documento
        FOREIGN KEY (doc_id) REFERENCES documentos (doc_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
