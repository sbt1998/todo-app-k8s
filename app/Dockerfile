# VULNERABILIDAD INTRODUCIDA 1: Imagen base con tag 'latest' en lugar de versión fija
# Tipo: Unpinned base image
# Severidad esperada: MEDIUM
FROM python:latest

# VULNERABILIDAD INTRODUCIDA 2: Ejecutar como root (no se crea usuario sin privilegios)
# Tipo: Container running as root
# Severidad esperada: HIGH
USER root

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# VULNERABILIDAD INTRODUCIDA 3: Contraseña hardcodeada en variable de entorno
# Tipo: Sensitive Information Exposure
# Severidad esperada: HIGH
ENV DB_PASS="todopass"

EXPOSE 5000

CMD ["python", "app.py"]
