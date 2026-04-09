# VULNERABILIDAD INTRODUCIDA: Imagen base 'latest' sin versión fija
# Tipo: Unpinned base image tag
# Severidad esperada: MEDIUM
FROM python:latest

# VULNERABILIDAD INTRODUCIDA: Ejecutar como root
# Tipo: Container running as root user
# Severidad esperada: HIGH
USER root

WORKDIR /app

# VULNERABILIDAD INTRODUCIDA: Contraseña hardcodeada
# Tipo: Sensitive data exposed in environment variable
# Severidad esperada: HIGH
ENV DB_PASSWORD="supersecreta123"
ENV SECRET_KEY="clave-super-secreta-hardcodeada"

# VULNERABILIDAD INTRODUCIDA: Puerto SSH expuesto
# Tipo: Sensitive port exposed
# Severidad esperada: MEDIUM
EXPOSE 22
EXPOSE 5000

RUN apt-get update && apt-get install -y curl wget

COPY . .

CMD ["python", "app.py"]
