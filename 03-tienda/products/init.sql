CREATE TABLE IF NOT EXISTS products (
    id    SERIAL PRIMARY KEY,
    sku   TEXT          NOT NULL UNIQUE,
    name  TEXT          NOT NULL,
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    stock INTEGER       NOT NULL CHECK (stock >= 0)
);

INSERT INTO products (sku, name, price, stock) VALUES
    ('SKU-001', 'Arroz 1 kg',          4200, 80),
    ('SKU-002', 'Aceite girasol 1 L',  9800, 40),
    ('SKU-003', 'Leche entera 1 L',    4500, 60),
    ('SKU-004', 'Pan tajado',          5500, 25),
    ('SKU-005', 'Cafe molido 250 g',  12500, 30),
    ('SKU-006', 'Huevos x 12',        13000, 50);
