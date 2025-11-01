# Gulf Contractors Resume Filter

A dockerized application for parsing, analyzing, and filtering resumes based on keywords with optional AI-powered summaries.

## Project Structure

```
GC_resumefilter/
├── backend/                 # FastAPI backend service
│   ├── config.py           # Configuration management
│   ├── main.py             # FastAPI application
│   ├── models.py           # Pydantic models
│   ├── resume_parser.py    # PDF/DOCX parsing
│   ├── keyword_matcher.py  # Keyword matching logic
│   ├── openai_service.py   # OpenAI integration
│   ├── csv_exporter.py     # CSV export functionality
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Backend container config
│   └── .dockerignore       # Docker ignore patterns
├── docker-compose.yml       # Multi-service orchestration
└── .env.example            # Environment variables template
```

## Prerequisites

- Docker
- Docker Compose
- OpenAI API Key (optional, for AI summaries)

## Quick Start

### 1. Clone and Setup Environment

```bash
# Copy the environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env
```

### 2. Configure Environment Variables

Edit `.env` file:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
USE_OPENAI=True

# Resume Filter Settings
MIN_KEYWORD_SCORE=50
```

### 3. Choose Your Environment

#### Development (Recommended for Testing)
Uses bind mounts for easy file access from host machine:

```bash
# Build and start development services
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down
```

**Benefits:**
- Direct access to `./output` and `./resumes` directories on host
- Easy debugging and testing
- Simple curl commands work with local files

#### Production
Uses named volumes for better isolation and portability:

```bash
# Build and start production services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services (keeps volumes)
docker-compose -f docker-compose.prod.yml down

# Stop and remove volumes
docker-compose -f docker-compose.prod.yml down -v
```

**Benefits:**
- Better security and isolation
- Works with orchestration platforms
- Portable across different servers
- Built-in health checks

### 4. Access the API

- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Health Check
```bash
GET /
```

### Filter Resumes
```bash
POST /filter-resumes
Content-Type: multipart/form-data

Parameters:
- files: List of resume files (PDF or DOCX)
- keywords: JSON array of keywords ["Python", "FastAPI", ...]
- min_score: Minimum score threshold (optional)
- generate_ai_summary: Enable AI summaries (default: true)
```

### Analyze Single Resume
```bash
POST /analyze-single
Content-Type: multipart/form-data

Parameters:
- file: Resume file (PDF or DOCX)
- keywords: JSON array of keywords
- generate_ai_summary: Enable AI summaries (default: true)
```

### Download CSV
```bash
GET /download-csv?file_path=/app/output/filtered_resumes_20250101_120000.csv
```

## Volume Management

### Development Mode (Bind Mounts)
Files are directly accessible on your host machine:

```bash
# Resumes are in ./resumes directory
ls ./resumes

# Output CSV files are in ./output directory
ls ./output

# Test with curl using local files
curl -X POST "http://localhost:8000/filter-resumes" \
  -F "files=@resumes/resume1.pdf" \
  -F "files=@resumes/resume2.pdf" \
  -F 'keywords=["Python", "FastAPI"]' \
  -F "min_score=50"
```

### Production Mode (Named Volumes)
Files are stored in Docker-managed volumes. Access them using docker commands:

```bash
# Copy resumes to the production volume
docker cp /path/to/local/resumes/. gc-resume-filter-backend:/app/resumes/

# Copy output files from the production volume
docker cp gc-resume-filter-backend:/app/output/. /path/to/local/output/

# Inspect volume contents
docker-compose -f docker-compose.prod.yml exec backend ls -la /app/output
docker-compose -f docker-compose.prod.yml exec backend ls -la /app/resumes

# Backup production volumes
docker run --rm -v resume-data-output:/data -v $(pwd):/backup alpine tar czf /backup/output-backup.tar.gz -C /data .
docker run --rm -v resume-data-storage:/data -v $(pwd):/backup alpine tar czf /backup/resumes-backup.tar.gz -C /data .
```

Both backend and frontend services have access to these volumes, allowing:
- Frontend to upload resumes to shared storage
- Backend to process and generate CSV reports
- Frontend to access and download generated CSV files

## Development

### Running Backend Locally (without Docker)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp ../.env.example .env

# Run the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Rebuilding Containers

```bash
# Rebuild and restart services
docker-compose up -d --build

# Rebuild specific service
docker-compose build backend
```

## Excel Hyperlinks in CSV Output (Windows Users)

The generated CSV files include Excel HYPERLINK formulas for easy access to resume files. For these hyperlinks to work correctly on Windows:

### Configure RESUME_FOLDER_PATH

In your `.env` file, set `RESUME_FOLDER_PATH` to your **Windows host path**:

```env
# Example for Windows (use your actual path)
RESUME_FOLDER_PATH=D:\Work\GulfContractors\GC_resumefilter\resumes

# Example for Linux/Mac
RESUME_FOLDER_PATH=/home/user/GC_resumefilter/resumes
```

**Important Notes:**
- Use backslashes (`\`) for Windows paths or forward slashes (`/`) - both work
- Use the **absolute path** on your host machine (not container path)
- The path should point to where your resume files are stored on your computer
- After changing this variable, restart the container: `docker-compose -f docker-compose.dev.yml restart`

### Testing Hyperlinks

1. Generate a CSV file using the API
2. Open the CSV in Excel (CSV files opened in text editors show the raw formula)
3. Click on any filename hyperlink - it should open the PDF in your default viewer

### Example

If your project is at `D:\Work\GulfContractors\GC_resumefilter\`:

```env
RESUME_FOLDER_PATH=D:\Work\GulfContractors\GC_resumefilter\resumes
```

The CSV will contain:
```
=HYPERLINK("file:///D:/Work/GulfContractors/GC_resumefilter/resumes/Resume.pdf","Resume.pdf")
```

When clicked in Excel, this opens `D:\Work\GulfContractors\GC_resumefilter\resumes\Resume.pdf`

### Disable Hyperlinks

If you don't need hyperlinks, leave the default:
```env
RESUME_FOLDER_PATH=/app/resumes
```

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI summaries | None (required if USE_OPENAI=True) |
| `USE_OPENAI` | Enable/disable OpenAI integration | True |
| `MIN_KEYWORD_SCORE` | Minimum keyword match score (0-100) | 50 |
| `CSV_OUTPUT_PATH` | Container path for CSV exports (don't change) | /app/output/filtered_resumes.csv |
| `RESUME_FOLDER_PATH` | Path for Excel hyperlinks - use Windows host path for working links | /app/resumes |

## Troubleshooting

### Check Container Logs
```bash
docker-compose logs backend
```

### Access Container Shell
```bash
docker-compose exec backend /bin/bash
```

### Reset Everything
```bash
docker-compose down -v
docker-compose up -d --build
```

## Future Additions

- React + Vite + TypeScript frontend (commented in docker-compose.yml)
- Database integration for resume storage
- User authentication
- Advanced filtering options

## License

Proprietary - Gulf Contractors



