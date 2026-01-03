# Interior Design AI - Backend

FastAPI backend for the AI-powered interior design application.

## Features

- **Chat-based design**: Upload a room photo and chat to make changes
- **AI-powered generation**: Uses Claude for understanding + Stable Diffusion for images
- **Version history**: Track all design iterations
- **Export specifications**: Generate PDF reports for contractors
- **Real-time updates**: WebSocket support for live chat

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy (async)
- **AI**: Anthropic Claude, Replicate (Stable Diffusion)
- **Storage**: S3-compatible (AWS S3, Cloudflare R2, MinIO)
- **Cache**: Redis

## Quick Start

### 1. Clone and setup

```bash
cd backend
cp .env.example .env
# Edit .env with your API keys
```

### 2. Run with Docker (Recommended)

```bash
docker-compose up -d
```

This starts:
- API server at http://localhost:8000
- PostgreSQL at localhost:5432
- Redis at localhost:6379
- MinIO (S3) at http://localhost:9000

### 3. Run locally (Alternative)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL and Redis (via Docker or locally)
docker-compose up -d db redis minio

# Run the app
uvicorn app.main:app --reload
```

## API Endpoints

### Projects
```
POST   /api/projects              # Create new project
GET    /api/projects              # List projects
GET    /api/projects/{id}         # Get project details
PATCH  /api/projects/{id}         # Update project
DELETE /api/projects/{id}         # Delete project
```

### Images
```
POST   /api/projects/{id}/upload  # Upload room photo
GET    /api/projects/{id}/image   # Get current design
GET    /api/projects/{id}/original # Get original photo
```

### Chat
```
POST   /api/projects/{id}/chat    # Send message, get design
GET    /api/projects/{id}/chat/history  # Get chat history
WS     /api/projects/{id}/ws      # WebSocket for real-time
```

### Versions
```
GET    /api/projects/{id}/versions     # Get all versions
POST   /api/projects/{id}/versions/{n}/favorite  # Toggle favorite
POST   /api/projects/{id}/versions/{n}/finalize  # Mark as final
```

### Export
```
POST   /api/projects/{id}/export  # Export specification
GET    /api/projects/{id}/specification  # Get spec as JSON
GET    /api/projects/{id}/export/pdf     # Download PDF
```

## API Usage Example

```python
import httpx

# 1. Create a project
response = httpx.post("http://localhost:8000/api/projects", json={
    "name": "Living Room Redesign"
})
project_id = response.json()["id"]

# 2. Upload room photo
with open("living_room.jpg", "rb") as f:
    response = httpx.post(
        f"http://localhost:8000/api/projects/{project_id}/upload",
        files={"file": f}
    )
print(response.json()["message"])  # AI's analysis

# 3. Chat to make changes
response = httpx.post(
    f"http://localhost:8000/api/projects/{project_id}/chat",
    json={"content": "Make the walls sage green"}
)
print(response.json()["image_url"])  # New design!

# 4. Export specification
response = httpx.post(
    f"http://localhost:8000/api/projects/{project_id}/export",
    json={"format": "pdf"}
)
with open("specification.pdf", "wb") as f:
    f.write(response.content)
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Claude API key | Yes |
| `REPLICATE_API_TOKEN` | Replicate API token | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `AWS_ACCESS_KEY_ID` | S3 access key | Yes |
| `AWS_SECRET_ACCESS_KEY` | S3 secret key | Yes |
| `S3_BUCKET_NAME` | S3 bucket name | Yes |
| `S3_ENDPOINT_URL` | S3 endpoint (for R2/MinIO) | No |
| `REDIS_URL` | Redis connection string | No |
| `DEBUG` | Enable debug mode | No |

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   │
│   ├── api/
│   │   ├── __init__.py      # API router
│   │   └── routes/
│   │       ├── projects.py  # Project CRUD
│   │       ├── chat.py      # Chat endpoints
│   │       ├── images.py    # Image upload
│   │       └── export.py    # Export specs
│   │
│   ├── models/
│   │   ├── database.py      # SQLAlchemy models
│   │   └── schemas.py       # Pydantic schemas
│   │
│   └── services/
│       ├── orchestrator.py  # Main AI logic
│       ├── room_analyzer.py # Claude Vision
│       ├── image_generator.py # Stable Diffusion
│       ├── spec_generator.py  # PDF export
│       └── storage.py       # S3 storage
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Development

### Run tests
```bash
pytest
```

### Format code
```bash
black app/
isort app/
```

### Type checking
```bash
mypy app/
```

## License

MIT
