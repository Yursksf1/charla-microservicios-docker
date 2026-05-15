# Ejercicios prácticos — Microservicios en Docker

Tres ejemplos progresivos pensados para acompañar la clase **Arquitectura de
Microservicios en Docker** (Javier Chacon — CUSOL UIS).

Cada ejemplo está pensado como una **empresa diferente** con su propia lógica
de negocio. La complejidad sube en cada paso, pero la base tecnológica es la
misma: **FastAPI + PostgreSQL + Docker Compose**.

| # | Carpeta | Empresa | Concepto que se practica |
|---|---------|---------|--------------------------|
| 1 | `01-cafeteria/` | Cafetería *El Buen Café* | 1 servicio + 1 BD. Dockerfile, Compose, `/healthz`, CRUD básico. |
| 2 | `02-biblioteca/` | Biblioteca *San Carlos* | 2 servicios + **2 BDs** (database-per-service). Llamada **REST entre servicios** vía DNS interno de Docker. |
| 3 | `03-tienda/` | Tienda online *MiniMarket* | 3 servicios + Postgres + **RabbitMQ**. Mensajería **asíncrona** con un worker que se puede **escalar**. |

## Antes de empezar

Necesitas tener instalado:

```bash
docker --version          # >= 20
docker compose version    # plugin v2
```

> Si tu Docker es antiguo (`docker-compose` con guión), los comandos que
> aparecen como `docker compose up` también funcionan como `docker-compose up`.

## Cómo trabajar con cada ejemplo

```bash
cd 01-cafeteria          # entra al ejemplo
docker compose up --build
# ... probar con curl, navegador o /docs ...
docker compose down -v   # apaga TODO y borra volúmenes (BD limpia)
```

El flag `-v` borra los volúmenes — útil mientras aprendes para volver a un
estado limpio. En producción, **NO** uses `-v` salvo que sepas qué borras.

## Filosofía de los ejemplos

Estos ejercicios privilegian **claridad pedagógica** sobre código de
producción. Verás cosas como contraseñas en texto plano en el `compose.yml`
o `SELECT *` que jamás aceptarías en un sistema real — son intencionales
para que el código sea lo más legible posible.

Cuando termines los tres, intenta:

1. Añadir un cuarto servicio a `03-tienda/` que también consuma el evento
   `order.created` (por ejemplo, *facturación*). Eso es **coreografía de
   eventos**.
2. Romper un servicio a propósito (`docker compose stop db`) y observar
   cómo se comporta el resto del sistema.
3. Escalar el worker: `docker compose up -d --scale notifier=4` y mandar
   muchos pedidos seguidos.
