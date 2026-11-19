# Trabajo Práctico - Programación 2 - API RESTful  

## Correr la API con Docker

Requiere tener [Docker](https://www.docker.com/products/docker-desktop/) instalado y abierto.

```bash
docker build -t paseos-api .
docker run -p 8000:8000 -e SECRET_KEY=poner-una-clave-larga paseos-api
```

La documentación interactiva queda en http://localhost:8000/docs.

- `SECRET_KEY` es obligatoria en producción: es la clave con la que se firman los tokens JWT.
- La base de datos es SQLite dentro del contenedor: los datos se pierden al borrar el contenedor.
- Las plataformas de deploy indican el puerto con la variable `PORT`; el contenedor la usa automáticamente (si no existe, usa el 8000).
