"""
MiniMarket — Products service.

Catalogo de productos. Independiente del servicio de pedidos: si pedidos
quiere saber un precio, pregunta aqui (no espia la BD).
"""
import os
from contextlib import contextmanager

import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DB_URL = os.environ["DB_URL"]

app = FastAPI(title="MiniMarket — Products", version="1.0.0")


class ProductIn(BaseModel):
    sku: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=1, max_length=120)
    price: float = Field(ge=0)
    stock: int = Field(ge=0)


class Product(ProductIn):
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


@app.get("/products", response_model=list[Product])
def list_products():
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, sku, name, price, stock FROM products ORDER BY id"
        )
        rows = cur.fetchall()
    return [
        {"id": r[0], "sku": r[1], "name": r[2], "price": float(r[3]), "stock": r[4]}
        for r in rows
    ]


@app.get("/products/{pid}", response_model=Product)
def get_product(pid: int):
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, sku, name, price, stock FROM products WHERE id = %s",
            (pid,),
        )
        row = cur.fetchone()
    if not row:
        raise HTTPException(404, "Producto no encontrado")
    return {
        "id": row[0], "sku": row[1], "name": row[2],
        "price": float(row[3]), "stock": row[4],
    }


@app.post("/products", response_model=Product, status_code=201)
def create_product(p: ProductIn):
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO products (sku, name, price, stock) "
            "VALUES (%s, %s, %s, %s) RETURNING id",
            (p.sku, p.name, p.price, p.stock),
        )
        new_id = cur.fetchone()[0]
        conn.commit()
    return {"id": new_id, **p.model_dump()}
