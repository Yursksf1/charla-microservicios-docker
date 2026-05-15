CREATE TABLE IF NOT EXISTS books (
    id     SERIAL PRIMARY KEY,
    title  TEXT NOT NULL,
    author TEXT NOT NULL,
    copies INTEGER NOT NULL CHECK (copies >= 0)
);

INSERT INTO books (title, author, copies) VALUES
    ('Cien anos de soledad',            'Gabriel Garcia Marquez', 3),
    ('Rayuela',                         'Julio Cortazar',         2),
    ('Pedro Paramo',                    'Juan Rulfo',             1),
    ('La ciudad y los perros',          'Mario Vargas Llosa',     2),
    ('Building Microservices',          'Sam Newman',             4),
    ('Designing Data-Intensive Apps',   'Martin Kleppmann',       2);
