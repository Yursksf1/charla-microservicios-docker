# Imagen base "slim": Python 3.12 sin paquetes extra (~50 MB en lugar de ~900).
FROM python:3.12-slim

# Carpeta de trabajo dentro del contenedor.
WORKDIR /app

# Truco de cache: copiamos requirements.txt antes que el codigo.
# Asi, si solo cambia el codigo (no las dependencias), Docker reutiliza la
# capa con pip install — y el build pasa de 60 s a 1 s.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ahora si, el codigo de la app.
COPY app.py .

# Documenta el puerto. No publica nada — eso lo hace docker-compose.
EXPOSE 8000

# Uvicorn sirviendo FastAPI. --host 0.0.0.0 para que sea accesible desde
# fuera del contenedor (de lo contrario solo escucharia en 127.0.0.1).
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
