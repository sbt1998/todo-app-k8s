# Imagen base oficial de Python
FROM python:3.11-slim

# Usuario no root por seguridad
RUN useradd -m appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Cambiamos a usuario no root
USER appuser

EXPOSE 5000

CMD ["python", "app.py"]
