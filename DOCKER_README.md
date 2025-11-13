# Docker Development Setup

This guide explains how to run the GulfContractors Resume Filter application using Docker for development.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

## Quick Start

### 1. Configure Environment Variables

Copy the example environment file and configure it:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and set your configuration:

```env
USE_OPENAI=False
OPENAI_API_KEY=your_openai_api_key_here
MIN_KEYWORD_SCORE=50
```

### 2. Build and Start Services

```bash
docker-compose up --build
```

This will:
- Build the backend (Python/FastAPI) container
- Build the frontend (React/Vite) container
- Start both services with hot-reload enabled
- Create a network for inter-service communication

### 3. Access the Application

- Frontend: http://localhost:5173/resumefilter/
- Backend API: http://localhost:8000/api/
- API Documentation: http://localhost:8000/docs

## Development Workflow

### Running in Background

```bash
docker-compose up -d
```

### View Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### Stopping Services

```bash
docker-compose down
```

### Rebuilding After Dependency Changes

If you modify `requirements.txt` or `package.json`:

```bash
docker-compose down
docker-compose up --build
```

### Accessing Service Shells

```bash
# Backend shell
docker-compose exec backend bash

# Frontend shell
docker-compose exec frontend sh
```

## Hot Reload

Both services are configured for hot-reload:

- **Backend**: Changes to Python files will automatically restart the FastAPI server
- **Frontend**: Changes to React/TypeScript files will trigger Vite's hot module replacement (HMR)

## Data Persistence

The following directories are mounted as volumes for persistence:

- `./backend/data` - Job profiles storage
- `./backend` - Backend source code (for hot-reload)
- `./frontend` - Frontend source code (for hot-reload)

## Troubleshooting

### Port Already in Use

If ports 5173 or 8000 are already in use, modify the port mappings in `docker-compose.yml`:

```yaml
ports:
  - "3000:5173"  # Map host port 3000 to container port 5173
```

### File Changes Not Detected (Windows/Mac)

If hot-reload isn't working, the Vite config already includes polling. Verify it's enabled in `frontend/vite.config.ts`:

```typescript
watch: {
  usePolling: true,
}
```

### Backend Health Check Failing

Check if the backend is running properly:

```bash
docker-compose exec backend curl http://localhost:8000/api/
```

### Permission Issues

If you encounter permission issues with mounted volumes:

```bash
# Linux: Fix ownership
sudo chown -R $USER:$USER backend/data
```

## Production Deployment

This Docker setup is for **development only**. For Apache production deployment, refer to `apache-config.conf`.

Key differences for production:
- Frontend should be built (`npm run build`) and served as static files
- Backend should run with production WSGI server settings
- Use proper environment variables and secrets management
- Enable security headers and HTTPS

## Architecture

```
┌─────────────────┐         ┌─────────────────┐
│   Frontend      │         │    Backend      │
│   (React/Vite)  │────────>│   (FastAPI)     │
│   Port: 5173    │         │   Port: 8000    │
└─────────────────┘         └─────────────────┘
        │                           │
        └───────────┬───────────────┘
                    │
            resumefilter-network
                (Docker Bridge)
```

## Environment Variables

### Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_OPENAI` | `False` | Enable/disable OpenAI integration |
| `OPENAI_API_KEY` | - | OpenAI API key for AI summaries |
| `MIN_KEYWORD_SCORE` | `50` | Minimum score threshold (0-100) |

### Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `/api` | Backend API URL |
| `DOCKER_ENV` | `true` | Enables Docker-specific proxy settings |

## Next Steps

1. Review client feedback points
2. Implement required changes
3. Test changes using Docker dev environment
4. Deploy to Apache production server

For client feedback implementation, refer to the main project documentation.
