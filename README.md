# E-commerce Chat IA API

API REST construida con FastAPI para un e-commerce de calzado con asistente conversacional basado en Google Gemini. El proyecto permite consultar productos, conversar con una IA con memoria de sesion y persistir historial en SQLite siguiendo una arquitectura en capas.

## Caracteristicas principales

- API REST con FastAPI
- Clean Architecture con capas `domain`, `application` e `infrastructure`
- Catalogo de productos persistido con SQLite y SQLAlchemy
- Chat con IA usando Google Gemini
- Historial conversacional por `session_id`
- Carga automatica de 10 productos iniciales al arrancar
- Ejecucion local y con Docker
- Tests unitarios con `pytest`
- Documentacion automatica en `/docs`


### Responsabilidades por capa

- `domain`: entidades, validaciones, excepciones e interfaces de repositorio
- `application`: DTOs y casos de uso
- `infrastructure`: FastAPI, SQLAlchemy, SQLite y Gemini

## Instalacion

### Requisitos previos

- Python `3.12` para ejecucion local
- `pip`
- Docker Desktop opcional
- API key de Google Gemini

### Instalacion local

```powershell
py -3.12 -m venv .venv312
.\.venv312\Scripts\python.exe -m pip install --upgrade pip
.\.venv312\Scripts\python.exe -m pip install -r requirements.txt
```

## Configuracion

Crea un archivo `.env` en la raiz del proyecto usando `.env.example` como base.

```env
GEMINI_API_KEY=tu_api_key_aqui
DATABASE_URL=sqlite:///./data/ecommerce_chat.db
ENVIRONMENT=development
HOST=127.0.0.1
PORT=8000
```

### Variables importantes

- `GEMINI_API_KEY`: clave para consumir Gemini
- `DATABASE_URL`: cadena de conexion de base de datos
- `ENVIRONMENT`: ambiente de ejecucion
- `HOST`: host local de Uvicorn
- `PORT`: puerto local de Uvicorn

## Uso

### Ejecutar localmente

La aplicacion crea tablas y carga automaticamente los 10 productos iniciales cuando la base esta vacia.

```powershell
.\.venv312\Scripts\python.exe run.py
```

### URLs utiles

- API: `http://127.0.0.1:8000/`
- Swagger UI: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

### Endpoints principales

- `GET /`
- `GET /products`
- `GET /products/{product_id}`
- `POST /chat`
- `GET /chat/history/{session_id}`
- `DELETE /chat/history/{session_id}`
- `GET /health`

### Ejemplos de uso

#### `GET /products`

```bash
curl http://127.0.0.1:8000/products
```

#### `GET /products/{product_id}`

```bash
curl http://127.0.0.1:8000/products/1
```

#### `POST /chat`

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"demo-session\",\"message\":\"Busco unos tenis negros para correr\"}"
```

#### `GET /chat/history/{session_id}`

```bash
curl "http://127.0.0.1:8000/chat/history/demo-session?limit=10"
```

#### `DELETE /chat/history/{session_id}`

```bash
curl -X DELETE http://127.0.0.1:8000/chat/history/demo-session
```

## Testing

### Ejecutar tests

```powershell
.\.venv312\Scripts\python.exe -m pytest -q
```

### Ejecutar cobertura

Si quieres medir cobertura, instala primero `pytest-cov` en el entorno virtual:

```powershell
.\.venv312\Scripts\python.exe -m pip install pytest-cov
.\.venv312\Scripts\python.exe -m pytest --cov=src.application --cov=src.domain.entities --cov-report=term-missing -q
```

## Docker

La imagen de contenedor usa `python:3.11-slim`. El desarrollo local usa Python `3.12`, que es la version fijada para el entorno del proyecto.

### Levantar servicios

```powershell
docker compose up --build -d
```

### Ver estado

```powershell
docker compose ps
```

### Ver logs

```powershell
docker compose logs -f
```

### Detener servicios

```powershell
docker compose down
```

## Tecnologias utilizadas

- Python 3.12 en local
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Google Gemini API
- Pytest
- Docker y Docker Compose

## Estructura del proyecto

```text
.
|-- src/
|   |-- application/
|   |   |-- chat_service.py
|   |   |-- dtos.py
|   |   `-- product_service.py
|   |-- domain/
|   |   |-- entities.py
|   |   |-- exceptions.py
|   |   `-- repositories.py
|   `-- infrastructure/
|       |-- api/
|       |   `-- main.py
|       |-- db/
|       |   |-- __init__.py
|       |   |-- database.py
|       |   `-- models.py
|       |-- llm_providers/
|       |   `-- gemini_service.py
|       `-- repositories/
|           |-- chat_repository.py
|           `-- product_repository.py
|-- tests/
|   |-- test.py
|   |-- test_entities.py
|   `-- test_services.py
|-- data/
|-- evidencias/
|-- .env.example
|-- .gitignore
|-- .python-version
|-- docker-compose.yml
|-- Dockerfile
|-- populate_db.py
|-- pyproject.toml
|-- README.md
|-- requirements.txt
`-- run.py
```
