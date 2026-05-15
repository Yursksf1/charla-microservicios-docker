"""
MiniMarket — Orders service.

Crea pedidos:
  1. Valida cada producto contra el servicio 'products' (sincrono, HTTP).
  2. Guarda el pedido y sus items en su propia BD.
  3. Publica el evento 'order.created' en RabbitMQ (asincrono).

El cliente recibe 201 en cuanto el pedido esta guardado y el evento
publicado — no espera al worker.
"""
import json
import os
from contextlib import contextmanager
from datetime import datetime

import httpx
import pika
import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field

DB_URL = os.environ["DB_URL"]
PRODUCTS_URL = os.environ["PRODUCTS_URL"]
MQ_URL = os.environ["MQ_URL"]

EXCHANGE = "orders"
ROUTING_KEY = "order.created"
HTTP_TIMEOUT = 3.0

app = FastAPI(title="MiniMarket — Orders", version="1.0.0")


# --------------------------------------------------------------------------
#   Modelos
# --------------------------------------------------------------------------
class ItemIn(BaseModel):
    product_id: int = Field(gt=0)
    qty: int = Field(gt=0)


class OrderIn(BaseModel):
    customer_email: EmailStr
    items: list[ItemIn] = Field(min_length=1)


class OrderOut(BaseModel):
    id: int
    customer_email: str
    total: float
    created_at: datetime
    items: list[dict]


# --------------------------------------------------------------------------
#   Helpers
# --------------------------------------------------------------------------
@contextmanager
def db():
    conn = psycopg.connect(DB_URL)
    try:
        yield conn
    finally:
        conn.close()


def publish_event(payload: dict) -> None:
    """
    Publica un evento JSON en el exchange 'orders'. Abrimos y cerramos la
    conexion en cada llamada — sencillo y suficiente para una clase. En
    produccion usarias una conexion persistente o un pool.
    """
    params = pika.URLParameters(MQ_URL)
    connection = pika.BlockingConnection(params)
    try:
        channel = connection.channel()
        # Idempotente: si el exchange ya existe con esos params, no pasa nada.
        channel.exchange_declare(exchange=EXCHANGE, exchange_type="fanout", durable=True)
        channel.basic_publish(
            exchange=EXCHANGE,
            routing_key=ROUTING_KEY,
            body=json.dumps(payload, default=str).encode(),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,  # persistente: sobrevive al reinicio del broker
            ),
        )
    finally:
        connection.close()


# --------------------------------------------------------------------------
#   Endpoints
# --------------------------------------------------------------------------
@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/orders", response_model=OrderOut, status_code=201)
def create_order(req: OrderIn):
    # --- 1. Validar productos y calcular total contra el servicio products
    enriched_items = []
    total = 0.0
    for item in req.items:
        try:
            r = httpx.get(
                f"{PRODUCTS_URL}/products/{item.product_id}",
                timeout=HTTP_TIMEOUT,
            )
        except httpx.RequestError as e:
            raise HTTPException(503, f"Servicio de productos no disponible: {e!s}")
        if r.status_code == 404:
            raise HTTPException(404, f"Producto {item.product_id} no existe")
        if r.status_code >= 400:
            raise HTTPException(502, f"products respondio {r.status_code}")
        p = r.json()
        subtotal = float(p["price"]) * item.qty
        total += subtotal
        enriched_items.append({
            "product_id": p["id"],
            "name": p["name"],
            "unit_price": float(p["price"]),
            "qty": item.qty,
            "subtotal": subtotal,
        })

    # --- 2. Guardar el pedido en la BD
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO orders (customer_email, total) VALUES (%s, %s) "
            "RETURNING id, created_at",
            (req.customer_email, total),
        )
        order_id, created_at = cur.fetchone()
        for it in enriched_items:
            cur.execute(
                "INSERT INTO order_items "
                "(order_id, product_id, product_name, unit_price, qty) "
                "VALUES (%s, %s, %s, %s, %s)",
                (order_id, it["product_id"], it["name"], it["unit_price"], it["qty"]),
            )
        conn.commit()

    # --- 3. Publicar el evento. Si esto falla DESPUES del commit, el
    # pedido queda sin notificacion — el outbox pattern resolveria esto.
    payload = {
        "event": "order.created",
        "order_id": order_id,
        "customer_email": req.customer_email,
        "total": total,
        "items": enriched_items,
        "created_at": created_at.isoformat(),
    }
    try:
        publish_event(payload)
    except Exception as e:
        # En produccion: log + alerta + reintento. No abortamos al cliente.
        print(f"[orders] WARN: no se pudo publicar el evento: {e}")

    return OrderOut(
        id=order_id,
        customer_email=req.customer_email,
        total=total,
        created_at=created_at,
        items=enriched_items,
    )


@app.get("/orders", response_model=list[OrderOut])
def list_orders():
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, customer_email, total, created_at "
            "FROM orders ORDER BY id DESC"
        )
        orders = cur.fetchall()

        results = []
        for o in orders:
            cur.execute(
                "SELECT product_id, product_name, unit_price, qty "
                "FROM order_items WHERE order_id = %s",
                (o[0],),
            )
            items = [
                {
                    "product_id": r[0],
                    "name": r[1],
                    "unit_price": float(r[2]),
                    "qty": r[3],
                    "subtotal": float(r[2]) * r[3],
                }
                for r in cur.fetchall()
            ]
            results.append(OrderOut(
                id=o[0], customer_email=o[1], total=float(o[2]),
                created_at=o[3], items=items,
            ))
    return results
