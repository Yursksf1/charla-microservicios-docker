# Ejemplo 1 — Cafetería *El Buen Café*

**Objetivo pedagógico:** levantar tu primer microservicio dentro de Docker,
con su propia base de datos PostgreSQL, sin instalar Python ni Postgres en
tu máquina.

## La empresa

*El Buen Café* es una cafetería de la zona universitaria que necesita un
catálogo digital de productos (cafés, panadería, comidas) para mostrar en
una pantalla y para alimentar a una app móvil que vendrá después.

## Arquitectura

```
   cliente (curl / navegador)
            │
            ▼
   ┌────────────────┐         ┌────────────────┐
   │  menu  (8001)  │ ──SQL──▶│  postgres (db) │
   │   FastAPI      │         │    cafeteria   │
   └────────────────┘         └────────────────┘
```

Un solo servicio (`menu`) habla con una sola BD (`db`). Más simple
imposible — pero te enseña todas las piezas que vamos a reutilizar.

## Qué vas a aprender aquí

- Cómo se escribe un `Dockerfile` para una API en Python.
- Cómo `docker-compose.yml` une dos contenedores en una red privada.
- Cómo el servicio `menu` encuentra a la BD por **nombre DNS** (`db`), no
  por IP.
- Cómo Postgres ejecuta automáticamente un `init.sql` la primera vez.
- Para qué sirve `/healthz` y por qué Compose tiene un `healthcheck`.

## Pasos

```bash
# 1. Levantar el stack
docker compose up --build

# 2. (en otra terminal) probar la API
curl http://localhost:8001/healthz
curl http://localhost:8001/products | jq

# 3. Crear un producto nuevo
curl -X POST http://localhost:8001/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Brownie","price":4500,"category":"postres"}'

# 4. Ver Swagger/OpenAPI gratis (cortesía de FastAPI)
#    abre en el navegador: http://localhost:8001/docs

# 5. Apagar y limpiar
docker compose down -v
```

## Cosas para experimentar

- **Reinicia solo la API**, sin tocar la BD:
  ```bash
  docker compose restart menu
  ```
  Verifica que tus productos siguen en la BD. Esto es porque están en un
  **volumen** (`pgdata`), no dentro del contenedor.

- **Borra el contenedor de la BD pero deja el volumen**:
  ```bash
  docker compose stop db && docker compose rm -f db
  docker compose up -d db
  ```
  Los datos persisten.

- **Borra el volumen** y observa que tus productos se fueron y volvió la
  semilla de `init.sql`:
  ```bash
  docker compose down -v && docker compose up
  ```

- **Entra al contenedor de la BD** y mira las tablas con `psql`:
  ```bash
  docker compose exec db psql -U cafe -d cafeteria -c '\dt'
  docker compose exec db psql -U cafe -d cafeteria -c 'SELECT * FROM products;'
  ```

## Ejercicios sugeridos

1. Añade un campo `available BOOLEAN` a `products` (modifica `init.sql`
   *y* el `app.py`). ¿Qué pasa si solo modificas uno?
2. Añade un endpoint `PATCH /products/{id}/price` que cambie solo el precio.
3. Añade validación: el precio no puede ser negativo (Pydantic lo permite
   con `Field(ge=0)`).
