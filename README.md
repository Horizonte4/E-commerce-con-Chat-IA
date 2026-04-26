# E-commerce Chat IA API

API REST construida con FastAPI para un e-commerce de calzado con asistente conversacional basado en Gemini. El proyecto expone endpoints para consultar productos, gestionar historial de conversación y responder preguntas del usuario con contexto.

## Características principales

- API REST con FastAPI
- Arquitectura por capas: `domain`, `application`, `infrastructure`
- Gestión de productos con servicios y repositorios
- Chat con historial de sesión
- Integración con Gemini para respuestas conversacionales
- Persistencia con SQLite y SQLAlchemy
- Ejecución local y con Docker
- Tests unitarios con `pytest`

### Capas

- `domain`: entidades, excepciones y contratos de repositorio
- `application`: casos de uso, servicios y DTOs
- `infrastructure`: API, base de datos, repositorios concretos e integración con Gemini

## Instalación

### Requisitos

- Python `3.12`
- `pip`
- Docker Desktop opcional

### Instalación local

```powershell
py -3.12 -m venv .venv312
.\.venv312\Scripts\python.exe -m pip install --upgrade pip
.\.venv312\Scripts\python.exe -m pip install -r requirements.txt
```

## Configuración

Crea un archivo `.env` en la raíz del proyecto con variables como estas:

```env
GEMINI_API_KEY=tu_api_key
DATABASE_URL=sqlite:///./data/ecommerce_chat.db
ENVIRONMENT=development
```

### Variables importantes

- `GEMINI_API_KEY`: clave para usar Gemini
- `DATABASE_URL`: cadena de conexión de la base de datos
- `ENVIRONMENT`: ambiente de ejecución

## Uso

### Ejecutar localmente

```powershell
.\.venv312\Scripts\python.exe populate_db.py
.\.venv312\Scripts\python.exe run.py
```

### Docker

### Construcción y arranque

```powershell
docker compose up --build -d
```

### Ver estado

```powershell
docker compose ps
```

### Detener servicios

```powershell
docker compose down
```

La imagen usa `python:3.11-slim` y el contenedor publica la API en el puerto `8000`.

La API quedará disponible en:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/health`

### Ejemplos de endpoints

#### `GET /`

```bash
curl http://127.0.0.1:8000/
```

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

#### `GET /health`

```bash
curl http://127.0.0.1:8000/health
```

## Testing

### Ejecutar tests

```powershell
.\.venv312\Scripts\python.exe -m pytest -q
```

### Ejecutar cobertura

```powershell
.\.venv312\Scripts\python.exe -m pytest --cov=src.application --cov=src.domain.entities --cov-report=term-missing -q
```

Cobertura validada en el proyecto: `97%` sobre los módulos cubiertos en la fase de tests.


## Tecnologías utilizadas

- Python 3.12 para desarrollo local
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Google Gemini API
- Pytest
- Docker y Docker Compose

## Estructura del proyecto

```text
e-commerce-chat-ai/
├── src/
│   ├── application/
│   │   ├── chat_service.py
│   │   ├── dtos.py
│   │   └── product_service.py
│   ├── domain/
│   │   ├── entities.py
│   │   ├── exceptions.py
│   │   └── repositories.py
│   ├── infrastructure/
│   │   ├── api/
│   │   │   └── main.py
│   │   ├── db/
│   │   │   ├── database.py
│   │   │   └── models.py
│   │   ├── llm_providers/
│   │   │   └── gemini_service.py
│   │   └── repositories/
│   │       ├── chat_repository.py
│   │       └── product_repository.py
│   └── python_compat.py
├── tests/
│   ├── test.py
│   ├── test_entities.py
│   └── test_services.py
├── data/
├── Dockerfile
├── docker-compose.yml
├── populate_db.py
├── pyproject.toml
├── requirements.txt
└── run.py
```
