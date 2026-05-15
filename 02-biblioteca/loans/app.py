"""
Biblioteca San Carlos — Loans service.

Gestiona prestamos. NO lee la tabla de libros directamente: para cualquier
informacion sobre stock o existencia llama por HTTP al servicio 'books'.
"""
import os
from contextlib import contextmanager
from datetime import datetime

import httpx
import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DB_URL = os.environ["DB_URL"]
BOOKS_URL = os.environ["BOOKS_URL"]

# Timeout corto. La clase enfatiza: la red va a fallar — no esperes
# eternamente. 3 segundos es generoso para una llamada entre contenedores
# en la misma red, pero suficientemente corto para no colgar al usuario.
HTTP_TIMEOUT = 3.0

app = FastAPI(title="Biblioteca — Loans", version="1.0.0")


class LoanIn(BaseModel):
    book_id: int = Field(gt=0)
    borrower: str = Field(min_length=1, max_length=120)


class Loan(BaseModel):
    id: int
    book_id: int
    borrower: str
    borrowed_at: datetime
    returned_at: datetime | None


@contextmanager
def db():
    conn = psycopg.connect(DB_URL)
    try:
        yield conn
    finally:
        conn.close()


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/loans", response_model=list[Loan])
def list_loans(active: bool | None = None):
    sql = "SELECT id, book_id, borrower, borrowed_at, returned_at FROM loans"
    if active is True:
        sql += " WHERE returned_at IS NULL"
    elif active is False:
        sql += " WHERE returned_at IS NOT NULL"
    sql += " ORDER BY id DESC"
    with db() as conn, conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return [
        Loan(id=r[0], book_id=r[1], borrower=r[2], borrowed_at=r[3], returned_at=r[4])
        for r in rows
    ]


@app.post("/loans", response_model=Loan, status_code=201)
def create_loan(req: LoanIn):
    """
    Crea un prestamo. Antes de insertar localmente, le pedimos al servicio
    'books' que reserve un ejemplar. Si books no responde o no hay stock,
    abortamos sin escribir en nuestra BD.
    """
    try:
        r = httpx.post(
            f"{BOOKS_URL}/books/{req.book_id}/reserve", timeout=HTTP_TIMEOUT
        )
    except httpx.RequestError as e:
        # books esta caido / no responde. En produccion: aqui dispararia
        # el circuit breaker (bloque 5 de la clase).
        raise HTTPException(
            status_code=503,
            detail=f"Servicio de libros no disponible: {e!s}",
        )

    if r.status_code == 404:
        raise HTTPException(404, "Libro no existe en el catalogo")
    if r.status_code == 409:
        raise HTTPException(409, "No hay ejemplares disponibles")
    if r.status_code >= 400:
        raise HTTPException(502, f"books respondio {r.status_code}: {r.text}")

    # books decremento el stock. Ahora registramos el prestamo.
    # OJO: si esta INSERT falla, el stock queda inconsistente — esto es
    # exactamente el problema que motiva el patron Saga.
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO loans (book_id, borrower) VALUES (%s, %s) "
            "RETURNING id, book_id, borrower, borrowed_at, returned_at",
            (req.book_id, req.borrower),
        )
        row = cur.fetchone()
        conn.commit()
    return Loan(
        id=row[0], book_id=row[1], borrower=row[2],
        borrowed_at=row[3], returned_at=row[4],
    )


@app.post("/loans/{lid}/return", response_model=Loan)
def return_loan(lid: int):
    """Marca el prestamo como devuelto y libera el ejemplar en books."""
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE loans SET returned_at = NOW() "
            "WHERE id = %s AND returned_at IS NULL "
            "RETURNING id, book_id, borrower, borrowed_at, returned_at",
            (lid,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(404, "Prestamo no encontrado o ya devuelto")
        conn.commit()

    # Liberar el ejemplar en books. Si falla, lo logueamos pero no echamos
    # atras el return — preferimos eventual consistency aqui.
    try:
        httpx.post(f"{BOOKS_URL}/books/{row[1]}/release", timeout=HTTP_TIMEOUT)
    except httpx.RequestError:
        # En produccion: enviar a una dead-letter queue para reintentar.
        pass

    return Loan(
        id=row[0], book_id=row[1], borrower=row[2],
        borrowed_at=row[3], returned_at=row[4],
    )
