-- BD propia del servicio de prestamos.
-- OJO: NO existe aqui ninguna tabla 'books'. La unica forma de saber
-- de un libro es preguntandole al servicio books por HTTP.

CREATE TABLE IF NOT EXISTS loans (
    id          SERIAL PRIMARY KEY,
    book_id     INTEGER     NOT NULL,
    borrower    TEXT        NOT NULL,
    borrowed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    returned_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_loans_active
    ON loans (book_id) WHERE returned_at IS NULL;
