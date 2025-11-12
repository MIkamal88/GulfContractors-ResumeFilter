# Gulf Contractors Resume Filter

A web application for parsing, analyzing, and filtering resumes based on keywords with optional AI-powered summaries. Deployed on Apache server with FastAPI backend and React frontend.

## Project Structure

```
GC_resumefilter/
├── backend/                     # FastAPI backend service
│   ├── config.py               # Configuration management
│   ├── main.py                 # FastAPI application
│   ├── models.py               # Pydantic models
│   ├── resume_parser.py        # PDF/DOCX parsing
│   ├── keyword_matcher.py      # Keyword matching logic
│   ├── openai_service.py       # OpenAI integration
│   ├── csv_exporter.py         # CSV export functionality
│   ├── requirements.txt        # Python dependencies
│   └── venv/                   # Python virtual environment
├── frontend/                    # React + Vite + TypeScript frontend
│   ├── src/                    # React source code
│   ├── dist/                   # Production build (served by Apache)
│   ├── package.json            # Node dependencies
│   └── vite.config.ts          # Vite configuration
├── apache-config.conf          # Apache virtual host configuration
├── deploy.sh                   # Automated deployment script
├── .env.example                # Environment variables template
├── output/                     # Generated CSV reports
└── resumes/                    # Uploaded resume files
```

## Prerequisites

- Apache2 web server
- Python 3.8+
- Node.js 16+ and npm
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

# File Paths (adjust to your local paths)
CSV_OUTPUT_PATH=/mnt/D/Work/GulfContractors/GC_resumefilter/output/filtered_resumes.csv
RESUME_FOLDER_PATH=/mnt/D/Work/GulfContractors/GC_resumefilter/resumes
```

### 3. Run Automated Deployment

The easiest way to deploy is using the automated script:

```bash
# Make the script executable (if not already)
chmod +x deploy.sh

# Run the deployment script
./deploy.sh
```

This script will:
1. Install backend Python dependencies
2. Install frontend Node dependencies
3. Build the frontend for production
4. Create necessary directories
5. Configure Apache with the correct settings
6. Set up the backend as a systemd service
7. Start all services

### 4. Manual Deployment (Alternative)

If you prefer manual deployment, see [APACHE_SETUP.md](APACHE_SETUP.md) for detailed step-by-step instructions.

### 5. Access the Application

- Frontend: http://localhost
- Backend API: http://localhost/api
- API Documentation: http://localhost/api/docs
- ReDoc: http://localhost/api/redoc

## Service Management

### Backend Service

The FastAPI backend runs as a systemd service:

```bash
# Check status
sudo systemctl status gc-resumefilter-backend

# Start service
sudo systemctl start gc-resumefilter-backend

# Stop service
sudo systemctl stop gc-resumefilter-backend

# Restart service
sudo systemctl restart gc-resumefilter-backend

# View logs
sudo journalctl -u gc-resumefilter-backend -f
```

### Apache Service

```bash
# Restart Apache
sudo systemctl restart apache2

# Reload Apache (without dropping connections)
sudo systemctl reload apache2

# Check Apache status
sudo systemctl status apache2

# View error logs
sudo tail -f /var/log/apache2/gc_resumefilter_error.log

# View access logs
sudo tail -f /var/log/apache2/gc_resumefilter_access.log
```

## API Endpoints

### Health Check
```bash
GET /api/
```

### Filter Resumes
```bash
POST /api/filter-resumes
Content-Type: multipart/form-data

Parameters:
- files: List of resume files (PDF or DOCX)
- keywords: JSON array of keywords ["Python", "FastAPI", ...]
- min_score: Minimum score threshold (optional)
- generate_ai_summary: Enable AI summaries (default: true)
```

### Analyze Single Resume
```bash
POST /api/analyze-single
Content-Type: multipart/form-data

Parameters:
- file: Resume file (PDF or DOCX)
- keywords: JSON array of keywords
- generate_ai_summary: Enable AI summaries (default: true)
```

### Download CSV
```bash
GET /api/download-csv?file_path=/path/to/filtered_resumes.csv
```

### Job Profiles
```bash
GET /api/job-profiles              # Get all job profiles
GET /api/job-profiles/{id}         # Get specific profile
POST /api/job-profiles             # Create custom profile
PUT /api/job-profiles/{id}         # Update custom profile
DELETE /api/job-profiles/{id}      # Delete custom profile
```

## Development

### Running Backend Locally (Development Mode)

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Run with auto-reload
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Running Frontend Locally (Development Mode)

```bash
cd frontend

# Start development server
npm run dev

# Build for production
npm run build
```

The Vite dev server proxies API requests to `http://localhost:8000` automatically.

### Rebuilding Frontend

After making changes to the frontend:

```bash
cd frontend
npm run build

# Restart Apache to clear any caches
sudo systemctl reload apache2
```

## File Storage

### Resumes
Uploaded resume files are stored in `./resumes/` directory. Ensure this directory has proper permissions:

```bash
chmod 755 resumes/
```

### Output CSV Files
Generated CSV reports are saved in `./output/` directory:

```bash
ls -lh output/
```

### Job Profiles Data
Custom job profiles are persisted in `./backend/data/custom_profiles.json`

## Excel Hyperlinks in CSV Output

The generated CSV files include Excel HYPERLINK formulas for easy access to resume files.

### Configure RESUME_FOLDER_PATH

In your `.env` file, set `RESUME_FOLDER_PATH` to your **local path**:

```env
# Example for Windows
RESUME_FOLDER_PATH=D:\Work\GulfContractors\GC_resumefilter\resumes

# Example for Linux
RESUME_FOLDER_PATH=/mnt/D/Work/GulfContractors/GC_resumefilter/resumes
```

**Important Notes:**
- Use the **absolute path** on your local machine
- For Windows: Use backslashes (`\`) or forward slashes (`/`)
- For Linux/WSL: Use forward slashes (`/`)
- After changing, restart the backend service

### Testing Hyperlinks

1. Generate a CSV file using the API
2. Open the CSV in Excel
3. Click on any filename hyperlink - it should open the PDF

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI summaries | None (required if USE_OPENAI=True) |
| `USE_OPENAI` | Enable/disable OpenAI integration | True |
| `MIN_KEYWORD_SCORE` | Minimum keyword match score (0-100) | 50 |
| `CSV_OUTPUT_PATH` | Path for CSV exports | ./output/filtered_resumes.csv |
| `RESUME_FOLDER_PATH` | Path for Excel hyperlinks | ./resumes |

## Troubleshooting

### Backend Issues

```bash
# Check if backend is running
curl http://localhost:8000

# Check service status
sudo systemctl status gc-resumefilter-backend

# View detailed logs
sudo journalctl -u gc-resumefilter-backend -n 100 --no-pager

# Restart backend
sudo systemctl restart gc-resumefilter-backend
```

### Frontend Issues

```bash
# Verify frontend build exists
ls -la frontend/dist/

# Rebuild frontend
cd frontend && npm run build

# Check Apache configuration
sudo apache2ctl configtest

# Restart Apache
sudo systemctl restart apache2
```

### Apache Proxy Issues

```bash
# Verify required modules are enabled
sudo apache2ctl -M | grep proxy

# Enable proxy modules if missing
sudo a2enmod proxy proxy_http rewrite headers
sudo systemctl restart apache2
```

### Permission Issues

```bash
# Fix directory permissions
chmod 755 resumes/ output/ backend/data/
chmod 644 .env
```

## Updating the Application

### Update Backend Code

```bash
# Pull latest changes
git pull

# Install any new dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Restart backend service
sudo systemctl restart gc-resumefilter-backend
```

### Update Frontend Code

```bash
# Pull latest changes
git pull

# Install dependencies and rebuild
cd frontend
npm install
npm run build

# Reload Apache
sudo systemctl reload apache2
```

## Architecture

### Request Flow

1. User accesses http://localhost → Apache serves React frontend from `frontend/dist/`
2. Frontend makes API calls to `/api/*` → Apache proxies to FastAPI on port 8000
3. FastAPI processes requests, parses resumes, matches keywords
4. Results returned to frontend or exported as CSV

### Technology Stack

- **Frontend**: React 19 + TypeScript + Vite
- **Backend**: FastAPI (Python) + Uvicorn
- **Web Server**: Apache2 with mod_proxy
- **Process Manager**: systemd
- **AI Integration**: OpenAI API
- **File Parsing**: PyPDF2, python-docx

## Security Considerations

- Backend runs on localhost:8000 (not exposed externally)
- Apache acts as reverse proxy
- CORS configured in FastAPI
- Security headers set in Apache config
- File upload validation in backend
- Environment variables for sensitive data

## License

Proprietary - Gulf Contractors
