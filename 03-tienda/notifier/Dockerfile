FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY worker.py .
# OJO: NO hay EXPOSE — este servicio no escucha HTTP.
# Y no usamos uvicorn — corremos el script directamente.
CMD ["python", "-u", "worker.py"]
