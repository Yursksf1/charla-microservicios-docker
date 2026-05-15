"""
Biblioteca San Carlos — Books service.

Catalogo de libros. Es la 'fuente de verdad' del stock: el servicio de
prestamos NUNCA toca esta BD directamente, solo consume estos endpoints.
"""
import os
from contextlib import contextmanager

import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DB_URL = os.environ["DB_URL"]

app = FastAPI(title="Biblioteca — Books", version="1.0.0")


class BookIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=120)
    copies: int = Field(ge=0)


class Book(BookIn):
    id: int


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


@app.get("/books", response_model=list[Book])
def list_books():
    with db() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, title, author, copies FROM books ORDER BY id")
        rows = cur.fetchall()
    return [{"id": r[0], "title": r[1], "author": r[2], "copies": r[3]} for r in rows]


@app.get("/books/{bid}", response_model=Book)
def get_book(bid: int):
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, title, author, copies FROM books WHERE id = %s", (bid,)
        )
        row = cur.fetchone()
    if not row:
        raise HTTPException(404, "Libro no encontrado")
    return {"id": row[0], "title": row[1], "author": row[2], "copies": row[3]}


@app.post("/books", response_model=Book, status_code=201)
def create_book(b: BookIn):
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO books (title, author, copies) VALUES (%s, %s, %s) "
            "RETURNING id",
            (b.title, b.author, b.copies),
        )
        new_id = cur.fetchone()[0]
        conn.commit()
    return {"id": new_id, **b.model_dump()}


@app.post("/books/{bid}/reserve", response_model=Book)
def reserve_copy(bid: int):
    """
    Decrementa el stock en 1. Atomico: usamos UPDATE ... WHERE copies > 0
    para evitar carreras (dos prestamos simultaneos sobre el ultimo
    ejemplar). Si la condicion no se cumple, devolvemos 409 Conflict.
    """
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE books SET copies = copies - 1 "
            "WHERE id = %s AND copies > 0 "
            "RETURNING id, title, author, copies",
            (bid,),
        )
        row = cur.fetchone()
        if not row:
            # Distinguimos 'no existe' de 'sin stock'.
            cur.execute("SELECT 1 FROM books WHERE id = %s", (bid,))
            if not cur.fetchone():
                raise HTTPException(404, "Libro no encontrado")
            raise HTTPException(409, "Sin ejemplares disponibles")
        conn.commit()
    return {"id": row[0], "title": row[1], "author": row[2], "copies": row[3]}


@app.post("/books/{bid}/release", response_model=Book)
def release_copy(bid: int):
    """Incrementa el stock en 1 — se llama al devolver un prestamo."""
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE books SET copies = copies + 1 WHERE id = %s "
            "RETURNING id, title, author, copies",
            (bid,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(404, "Libro no encontrado")
        conn.commit()
    return {"id": row[0], "title": row[1], "author": row[2], "copies": row[3]}
