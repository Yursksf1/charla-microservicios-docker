# Ejemplo 2 — Biblioteca *San Carlos*

**Objetivo pedagógico:** practicar el patrón **database-per-service** y la
**comunicación REST entre microservicios** usando el DNS interno de Docker.

## La empresa

La *Biblioteca San Carlos* presta libros. Quiere dividir su sistema en dos
servicios separados para que dos equipos diferentes los mantengan:

- **books** — el catálogo (qué libros existen, cuántos ejemplares hay).
- **loans** — los préstamos (quién tiene qué libro y desde cuándo).

Cada equipo es dueño de su propio servicio y, **muy importante**, de su
propia base de datos. No pueden meter mano en la BD del otro.

## Arquitectura

```
       cliente
          │
          ├─────────────────────┐
          ▼                     ▼
   ┌──────────────┐      ┌──────────────┐
   │ books (8002) │      │ loans (8003) │
   │   FastAPI    │◄─────│   FastAPI    │   (loans llama a books por HTTP)
   └──────┬───────┘      └──────┬───────┘
          │                     │
          ▼                     ▼
   ┌──────────────┐      ┌──────────────┐
   │ books_db     │      │ loans_db     │   (BDs independientes!)
   │  postgres    │      │  postgres    │
   └──────────────┘      └──────────────┘
```

Cuando alguien crea un préstamo en **loans**, este llama por HTTP a
**books** para:
1. Confirmar que el libro existe.
2. Bajar el contador de ejemplares disponibles.

Esa es la única forma de saber de los libros: **prohibido leer
directamente** la tabla `books` desde el servicio `loans`.

## Qué vas a aprender aquí

- Por qué cada servicio tiene su propia BD (acoplamiento, escalado,
  evolución de esquema independiente).
- Cómo un servicio resuelve la dirección del otro: en Docker Compose,
  simplemente `http://books:8000`.
- Qué pasa cuando un servicio del que dependes está caído (la red **va a**
  fallar — bloque 3 de la clase).
- El concepto de **contrato HTTP** entre servicios: si `books` cambia su
  endpoint, `loans` se rompe.

## Pasos

```bash
# 1. Levantar todo
docker compose up --build

# 2. Listar libros (semilla incluida)
curl http://localhost:8002/books | jq

# 3. Crear un prestamo (esto disparara la llamada loans -> books)
curl -X POST http://localhost:8003/loans \
  -H "Content-Type: application/json" \
  -d '{"book_id": 1, "borrower": "Maria Lopez"}'

# 4. Ver el prestamo creado y el contador de ejemplares decrementado
curl http://localhost:8003/loans | jq
curl http://localhost:8002/books/1 | jq

# 5. Devolver el libro
curl -X POST http://localhost:8003/loans/1/return

# 6. Apagar
docker compose down -v
```

## Cosas para experimentar

- **Tira `books` abajo** y trata de crear un préstamo:
  ```bash
  docker compose stop books
  curl -X POST http://localhost:8003/loans \
    -H "Content-Type: application/json" \
    -d '{"book_id": 2, "borrower": "Test"}'
  ```
  Verás el error que devuelve `loans` cuando no puede contactar a `books`.
  Esto es lo que la clase llama **fallo en cascada** y lo que un *circuit
  breaker* mitigaría.

- **Asómate a las BDs por separado** y comprueba que cada una tiene SOLO
  su tabla:
  ```bash
  docker compose exec books_db psql -U app -d books -c '\dt'
  docker compose exec loans_db psql -U app -d loans -c '\dt'
  ```

- **Intenta crear un préstamo de un libro inexistente**:
  ```bash
  curl -X POST http://localhost:8003/loans \
    -H "Content-Type: application/json" \
    -d '{"book_id": 9999, "borrower": "Test"}'
  ```
  Observa cómo `loans` traduce el 404 de `books` a su propia respuesta.

## Ejercicios sugeridos

1. Añade un endpoint `GET /loans/by-borrower/{nombre}` en `loans`.
2. Cuando se devuelve un libro, el contador debería **subir**. Implementa
   esa llamada de regreso a `books`. (Pista: necesitas un endpoint
   nuevo en `books`.)
3. Hoy `loans` confía ciegamente en `books`. Añade un timeout corto al
   `httpx.post` y observa qué pasa si `books` tarda demasiado.
4. **Saga manual:** ¿qué pasa si `books` decrementa pero la inserción en
   `loans_db` falla justo después? El stock queda inconsistente. Diseña
   una compensación.
