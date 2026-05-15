-- Cafeteria El Buen Cafe — esquema y semilla.
-- Postgres ejecuta este archivo automaticamente la primera vez que se
-- inicializa el volumen, gracias a que lo montamos en
-- /docker-entrypoint-initdb.d/init.sql desde docker-compose.yml.

CREATE TABLE IF NOT EXISTS products (
    id       SERIAL PRIMARY KEY,
    name     TEXT          NOT NULL,
    price    NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    category TEXT          NOT NULL
);

INSERT INTO products (name, price, category) VALUES
    ('Espresso',                  3500, 'cafe'),
    ('Capuccino',                 5500, 'cafe'),
    ('Americano',                 4000, 'cafe'),
    ('Latte vainilla',            6000, 'cafe'),
    ('Croissant',                 4500, 'panaderia'),
    ('Pan de queso',              3000, 'panaderia'),
    ('Sandwich jamon y queso',    8500, 'comida'),
    ('Brownie con helado',        7000, 'postres');
