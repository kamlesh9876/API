# Myth Buster API

A FastAPI-based REST API for debunking and verifying common myths and misconceptions.

## Features

- **CRUD Operations**: Create, read, update, and delete myths
- **Search**: Search myths by title, description, or category
- **Filtering**: Filter myths by category or truth status
- **Statistics**: Get statistics about the myth database
- **Categories**: View all available categories

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python app.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Myths
- `GET /myths` - Get all myths (with optional filtering)
- `GET /myths/{id}` - Get a specific myth
- `POST /myths` - Create a new myth
- `PUT /myths/{id}` - Update a myth
- `DELETE /myths/{id}` - Delete a myth

### Search & Filter
- `GET /myths/search?q=query` - Search myths
- `GET /categories` - Get all categories
- `GET /stats` - Get database statistics

## Data Model

Each myth contains:
- `id`: Unique identifier
- `title`: Myth title
- `description`: Detailed description
- `is_true`: Whether the statement is true or false
- `category`: Category (Nature, Biology, Animals, etc.)
- `evidence`: List of evidence points
- `sources`: List of credible sources

## Example Usage

### Get all myths
```bash
curl http://localhost:8000/myths
```

### Get only false myths
```bash
curl http://localhost:8000/myths?is_true=false
```

### Search for myths about brain
```bash
curl http://localhost:8000/myths/search?q=brain
```

### Create a new myth
```bash
curl -X POST http://localhost:8000/myths \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Myth",
    "description": "Description of the myth",
    "is_true": false,
    "category": "Science",
    "evidence": ["Evidence 1"],
    "sources": ["Source 1"]
  }'
```
