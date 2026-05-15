"""
MiniMarket — Notifier worker.

Consume eventos 'order.created' de RabbitMQ y simula el envio de un email
de confirmacion. No expone HTTP. Si lo escalas a N replicas, RabbitMQ
reparte los mensajes en round-robin entre ellas.

Logica clave:
  * basic_qos(prefetch_count=1): cada worker procesa UN mensaje a la vez,
    lo que da un balanceo justo entre N workers cuando los pedidos tardan
    diferente.
  * Reintento de conexion al broker: la primera vez que el contenedor
    arranca RabbitMQ puede no estar listo (healthcheck no es perfecto).
"""
import json
import os
import time

import pika

MQ_URL = os.environ["MQ_URL"]
EXCHANGE = "orders"
QUEUE = "notifier.order.created"


def connect_with_retry(url: str, max_attempts: int = 20) -> pika.BlockingConnection:
    delay = 1
    for attempt in range(1, max_attempts + 1):
        try:
            return pika.BlockingConnection(pika.URLParameters(url))
        except pika.exceptions.AMQPConnectionError as e:
            print(f"[notifier] broker no responde (intento {attempt}): {e}")
            time.sleep(delay)
            delay = min(delay * 2, 10)  # backoff exponencial con tope
    raise RuntimeError("No se pudo conectar al broker tras varios intentos")


def on_message(ch, method, properties, body) -> None:
    try:
        event = json.loads(body)
    except json.JSONDecodeError:
        print(f"[notifier] mensaje invalido, descartando: {body!r}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    order_id = event.get("order_id")
    email = event.get("customer_email")
    total = event.get("total")

    # Simulamos un envio de email — en la vida real aqui iria SendGrid,
    # SES, Mailgun, etc. Imprimimos para que se vea en `docker logs`.
    print(
        f"[notifier] Enviando email a {email}: "
        f"pedido #{order_id} confirmado, total ${total:.2f}",
        flush=True,
    )
    time.sleep(0.5)  # simulamos latencia del proveedor de email

    # ACK explicito: solo despues de procesar exitosamente. Si el worker
    # muere antes del ACK, RabbitMQ reentrega el mensaje a otro consumidor.
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main() -> None:
    print(f"[notifier] conectando a {MQ_URL} ...", flush=True)
    connection = connect_with_retry(MQ_URL)
    channel = connection.channel()

    # Declaramos exchange y cola — son idempotentes.
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="fanout", durable=True)
    channel.queue_declare(queue=QUEUE, durable=True)
    channel.queue_bind(queue=QUEUE, exchange=EXCHANGE)

    # Un mensaje a la vez por consumidor: clave para que `--scale` funcione
    # bien (sin esto un solo worker se llevaria todos los mensajes en bloque).
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(queue=QUEUE, on_message_callback=on_message)

    print(f"[notifier] esperando mensajes en cola '{QUEUE}'. Ctrl+C para salir.", flush=True)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
