CREATE TABLE salas (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(50),
    capacidad INT
);

INSERT INTO salas(nombre, capacidad)
VALUES
('Sala A',40),
('Sala B',40),
('Sala C',40);

CREATE TABLE eventos (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    responsable VARCHAR(100),
    nombre_evento VARCHAR(150),
    asistentes INT,
    fecha DATE,
    hora_inicio TIME,
    hora_fin TIME,
    tipo_acomodo VARCHAR(50),
    estado VARCHAR(20) DEFAULT 'Activo',

    extension BOOLEAN DEFAULT FALSE,
    cafeteria BOOLEAN DEFAULT FALSE,
    sonido BOOLEAN DEFAULT FALSE,
    videoconferencia BOOLEAN DEFAULT FALSE,

    sala_id INT,

    FOREIGN KEY(sala_id) REFERENCES salas(id)
);

CREATE TABLE historial (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    evento_id INT,
    accion VARCHAR(20),
    descripcion VARCHAR(255),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(evento_id) REFERENCES eventos(id)
);

CREATE TABLE evento_salas (
    evento_id INT,
    sala_id INT,

    PRIMARY KEY(evento_id, sala_id),

    FOREIGN KEY(evento_id)
        REFERENCES eventos(id),

    FOREIGN KEY(sala_id)
        REFERENCES salas(id)
);

CREATE TABLE servicios (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(100)
);

INSERT INTO servicios(nombre)
VALUES
('Cafetería'),
('Sonido'),
('Videoconferencia'),
('Extensiones');
