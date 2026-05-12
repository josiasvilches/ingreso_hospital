# 1. Usamos una imagen oficial de Python ligera
FROM python:3.10-slim

# 2. Definimos el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiamos el archivo de requerimientos y los instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiamos todo el código fuente de tu proyecto al contenedor
COPY . .

# 5. Exponemos el puerto de tu servidor (8888)
EXPOSE 8888

# Nota: No ponemos un CMD o ENTRYPOINT fijo acá, porque se lo  
# pasamos dinámicamente desde el docker-compose (uno para main, otro para celery).