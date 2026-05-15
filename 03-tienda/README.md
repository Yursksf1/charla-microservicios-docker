# Ejemplo 3 — Tienda online *MiniMarket*

**Objetivo pedagógico:** practicar **mensajería asíncrona** con un broker
(RabbitMQ), worker independiente, escalado horizontal del worker, y la
diferencia entre comunicación síncrona y asíncrona.

## La empresa

*MiniMarket* vende productos en línea. El equipo se dio cuenta de que cada
vez que alguien hace un pedido, hay que enviar email de confirmación,
notificación push, registro a analítica, etc. — y todas esas tareas
volvían lentísima la API.

Decisión: el pedido se guarda y se confirma de inmediato, y las
notificaciones se procesan **en segundo plano** por un worker.

## Arquitectura

```
   cliente
      │
      ▼
   ┌──────────────┐         ┌─────────────────┐
   │ orders (8005)│ ──SQL─► │ orders_db (pg)  │
   │   FastAPI    │         └─────────────────┘
   └──────┬───────┘
          │ publica
          │ "order.created"
          ▼
   ┌─────────────────┐
   │  RabbitMQ (mq)  │ ────► ┌────────────────────────┐
   └─────────────────┘       │ notifier (worker x N)  │
                             │   pika, sin HTTP       │
   ┌──────────────┐          └────────────────────────┘
   │products(8004)│──SQL─►┌─────────────────┐
   │   FastAPI    │       │ products_db (pg)│
   └──────────────┘       └─────────────────┘
```

- **products** — catálogo independiente. CRUD simple. Lo usa `orders`
  para validar que el producto existe y obtener el precio.
- **orders** — API que crea pedidos. Llama a `products` (síncrono) para
  validar y luego **publica** un evento `order.created` (asíncrono).
  Devuelve `201` al cliente sin esperar a que se procese la notificación.
- **notifier** — worker que **no expone HTTP**. Solo se conecta a
  RabbitMQ y procesa eventos. Simula enviar un email imprimiendo en log.

## Qué vas a aprender aquí

- Por qué `orders` no llama a `notifier` directamente: si el envío de
  email tarda 5 s, el cliente esperaría 5 s.
- Cómo el **broker** absorbe picos de carga: aunque el worker esté lento
  o caído, los mensajes esperan en la cola.
- Cómo **escalar** un worker para procesar más rápido.
- La diferencia entre un servicio que expone API y un worker que no.

## Pasos

```bash
# 1. Levantar todo (RabbitMQ tarda ~10 s en estar healthy la primera vez)
docker compose up --build

# 2. Listar productos (semilla incluida)
curl http://localhost:8004/products | jq

# 3. Crear un pedido. orders -> products (sync) -> rabbitmq -> notifier
curl -X POST http://localhost:8005/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_email":"ana@example.com","items":[{"product_id":1,"qty":2},{"product_id":3,"qty":1}]}'

# 4. Mira los logs del worker — veras la 'notificacion enviada'
docker compose logs -f notifier

# 5. La UI de RabbitMQ (admin/admin)
#    http://localhost:15672/

# 6. Apagar
docker compose down -v
```

## Cosas para experimentar

- **Apaga el worker** y crea pedidos. Los mensajes se acumularán en
  RabbitMQ (puedes verlo en la UI). Cuando levantes el worker de nuevo,
  los procesará todos:
  ```bash
  docker compose stop notifier
  for i in 1 2 3 4 5; do
    curl -X POST http://localhost:8005/orders -H "Content-Type: application/json" \
      -d '{"customer_email":"test@x.com","items":[{"product_id":1,"qty":1}]}'
  done
  docker compose start notifier
  docker compose logs -f notifier
  ```

- **Escala el worker** para procesar más rápido:
  ```bash
  docker compose up -d --scale notifier=4
  docker compose ps notifier   # veras 4 contenedores
  ```
  RabbitMQ reparte los mensajes entre los 4 consumidores en round-robin.

- **Apaga RabbitMQ** y crea un pedido:
  ```bash
  docker compose stop mq
  curl -X POST http://localhost:8005/orders ...
  ```
  La API de pedidos fallará al publicar. En producción usarías el
  **outbox pattern** (clase, bloque 5): guardar el evento en la misma
  transacción que el pedido y publicarlo desde un proceso separado.

## Ejercicios sugeridos

1. Añade un cuarto servicio: `inventory` (otro worker) que consuma el
   mismo evento `order.created` y descuente stock en su propia BD.
   Tendrás que cambiar el `exchange` de RabbitMQ de `direct` a `fanout`
   o usar dos `queues` separadas. Esto es **coreografía de eventos**.
2. Añade idempotencia: el worker debería poder reprocesar el mismo
   `order.created` sin enviar dos emails (pista: tabla de eventos
   procesados con el `order_id`).
3. Implementa un endpoint `GET /orders/{id}` que devuelva el estado y
   los items.
