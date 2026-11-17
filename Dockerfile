# Imagen de la API de Gestión de Paseos Caninos.
#
# Construir:  docker build -t paseos-api .
# Correr:     docker run -p 8000:8000 -e SECRET_KEY=una-clave-larga paseos-api
# Docs:       http://localhost:8000/docs

FROM python:3.14-slim

# No generar archivos .pyc y mostrar los logs al instante.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Instalar las dependencias en el Python del contenedor, sin virtualenv:
    # el contenedor ya es un entorno aislado.
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN pip install --no-cache-dir poetry

# Primero solo los archivos de dependencias: si el código cambia pero las
# dependencias no, Docker reutiliza esta capa y el build es mucho más rápido.
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root --no-interaction --no-ansi

# Después, el código.
COPY . .

EXPOSE 8000

# Las plataformas de deploy indican el puerto en la variable PORT;
# si no existe, se usa el 8000.
CMD ["sh", "-c", "fastapi run paseos/app.py --host 0.0.0.0 --port ${PORT:-8000}"]
