CREATE TABLE IF NOT EXISTS orders (
    id             SERIAL PRIMARY KEY,
    customer_email TEXT          NOT NULL,
    total          NUMERIC(12,2) NOT NULL CHECK (total >= 0),
    created_at     TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- Denormalizamos product_name y unit_price a proposito: el pedido es un
-- documento historico — si manana el producto cambia de nombre o de
-- precio, el pedido debe seguir mostrando lo que se cobro en su momento.
CREATE TABLE IF NOT EXISTS order_items (
    id           SERIAL PRIMARY KEY,
    order_id     INTEGER       NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id   INTEGER       NOT NULL,
    product_name TEXT          NOT NULL,
    unit_price   NUMERIC(10,2) NOT NULL,
    qty          INTEGER       NOT NULL CHECK (qty > 0)
);

CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
