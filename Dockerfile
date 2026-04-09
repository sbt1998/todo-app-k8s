# CORRECCIÓN 1: Imagen base con versión fija en lugar de 'latest'
# Vulnerabilidad original: Image Version Using 'latest' (MEDIUM)
# Estado: CORREGIDA
FROM python:3.11-slim

# CORRECCIÓN 2: Usuario no root
# Vulnerabilidad original: Last User Is 'root' (HIGH)
# Estado: CORREGIDA
RUN useradd -m appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# CORRECCIÓN 3: Contraseña eliminada del Dockerfile
# Vulnerabilidad original: Passwords And Secrets - Generic Secret (HIGH)
# Estado: CORREGIDA - las credenciales se inyectan en tiempo de ejecución
# ENV DB_PASSWORD ya no está aquí

# CORRECCIÓN 4: Puerto SSH eliminado
# Vulnerabilidad original: Exposing Port 22 SSH (LOW)
# Estado: CORREGIDA
EXPOSE 5000

# CORRECCIÓN 5: Healthcheck añadido
# Vulnerabilidad original: Healthcheck Instruction Missing (LOW)
# Estado: CORREGIDA
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

USER appuser

CMD ["python", "app.py"]
