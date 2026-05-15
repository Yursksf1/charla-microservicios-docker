"""
Cafeteria 'El Buen Cafe' — Menu API.

Un solo servicio FastAPI con CRUD sobre productos. La conexion a Postgres
se hace con psycopg (v3), abriendo una conexion por request — sencillo y
suficiente para una clase. En produccion usarias un pool (psycopg_pool o
SQLAlchemy).
"""
import os
from contextlib import contextmanager

import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DB_URL = os.environ["DB_URL"]

app = FastAPI(
    title="Cafeteria — Menu API",
    description="Catalogo de productos de la cafeteria El Buen Cafe.",
    version="1.0.0",
)


# --------------------------------------------------------------------------
#   Modelos Pydantic — definen el contrato JSON de entrada y salida.
# --------------------------------------------------------------------------
class ProductIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    price: float = Field(ge=0)
    category: str = Field(min_length=1, max_length=40)


class Product(ProductIn):
    id: int


# --------------------------------------------------------------------------
#   Helper de conexion a Postgres.
# --------------------------------------------------------------------------
@contextmanager
def db():
    conn = psycopg.connect(DB_URL)
    try:
        yield conn
    finally:
        conn.close()


# --------------------------------------------------------------------------
#   Endpoints de salud — los usa Docker / Compose / Kubernetes.
# --------------------------------------------------------------------------
@app.get("/healthz", tags=["health"])
def healthz():
    """Liveness: estoy vivo? (no toca la BD)."""
    return {"status": "ok"}


@app.get("/readyz", tags=["health"])
def readyz():
    """Readiness: estoy listo para servir trafico? (BD respondiendo)."""
    try:
        with db() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"db unavailable: {e}")


# --------------------------------------------------------------------------
#   CRUD de productos.
# --------------------------------------------------------------------------
@app.get("/products", response_model=list[Product], tags=["products"])
def list_products(category: str | None = None):
    sql = "SELECT id, name, price, category FROM products"
    params: tuple = ()
    if category:
        sql += " WHERE category = %s"
        params = (category,)
    sql += " ORDER BY id"
    with db() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    return [
        {"id": r[0], "name": r[1], "price": float(r[2]), "category": r[3]}
        for r in rows
    ]


@app.get("/products/{pid}", response_model=Product, tags=["products"])
def get_product(pid: int):
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, name, price, category FROM products WHERE id = %s",
            (pid,),
        )
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"id": row[0], "name": row[1], "price": float(row[2]), "category": row[3]}


@app.post("/products", response_model=Product, status_code=201, tags=["products"])
def create_product(p: ProductIn):
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO products (name, price, category) "
            "VALUES (%s, %s, %s) RETURNING id",
            (p.name, p.price, p.category),
        )
        new_id = cur.fetchone()[0]
        conn.commit()
    return {"id": new_id, **p.model_dump()}


@app.delete("/products/{pid}", status_code=204, tags=["products"])
def delete_product(pid: int):
    with db() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM products WHERE id = %s", (pid,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        conn.commit()
