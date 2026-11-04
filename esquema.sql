CREATE TABLE IF NOT EXISTS documentos (
    doc_id INT NOT NULL AUTO_INCREMENT,
    nombre_archivo VARCHAR(255) NOT NULL,
    PRIMARY KEY (doc_id),
    UNIQUE KEY uq_documentos_nombre_archivo (nombre_archivo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS diccionario (
    termino VARCHAR(100) NOT NULL,
    num_docs INT NOT NULL,
    total_frecuencias INT NOT NULL,
    PRIMARY KEY (termino)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS posting (
    termino VARCHAR(100) NOT NULL,
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
