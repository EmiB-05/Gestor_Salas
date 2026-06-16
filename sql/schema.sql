CREATE DATABASE gestor_salas;

CREATE TABLE salas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50),
    capacidad INT
);

INSERT INTO salas(nombre, capacidad)
VALUES
('Sala A',40),
('Sala B',40),
('Sala C',40);

CREATE TABLE eventos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    responsable VARCHAR(100),
    nombre_evento VARCHAR(150),
    asistentes INT,
    fecha DATE,
    hora_inicio TIME,
    hora_fin TIME,
    tipo_acomodo VARCHAR(50),
    estado VARCHAR(20) DEFAULT 'Activo'
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
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100)
);

INSERT INTO servicios(nombre)
VALUES
('Cafetería'),
('Sonido'),
('Videoconferencia'),
('Extensiones');