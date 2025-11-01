# Windows Setup Guide

Quick setup guide for Windows users.

## Prerequisites

- Docker Desktop for Windows
- Git for Windows (optional)

## Installation Steps

### 1. Install Docker Desktop

Download and install from: https://www.docker.com/products/docker-desktop/

### 2. Clone or Download the Project

```powershell
# Using Git
git clone <repository-url>
cd GC_resumefilter

# Or download and extract ZIP file
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env`:

```powershell
copy .env.example .env
```

Edit `.env` in Notepad or your preferred editor:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_actual_api_key_here
USE_OPENAI=True

# Resume Filter Settings
MIN_KEYWORD_SCORE=50

# File Paths
CSV_OUTPUT_PATH=/app/output/filtered_resumes.csv

# IMPORTANT: Set this to your Windows path for working Excel hyperlinks
# Example: RESUME_FOLDER_PATH=C:\Users\YourName\Projects\GC_resumefilter\resumes
RESUME_FOLDER_PATH=D:\Work\GulfContractors\GC_resumefilter\resumes
```

**Finding Your Path:**
1. Open File Explorer
2. Navigate to your project's `resumes` folder
3. Click on the address bar - it will show the full path
4. Copy and paste into `.env` file

### 4. Start the Application

Using PowerShell or Command Prompt:

```powershell
# Development mode (recommended for testing)
docker-compose -f docker-compose.dev.yml up -d

# Check if it's running
docker ps

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```

### 5. Test the API

Open browser and navigate to:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/

Or test with PowerShell:

```powershell
# Health check
curl http://localhost:8000/

# Upload and filter resumes (from project root directory)
curl -X POST "http://localhost:8000/filter-resumes" `
  -F "files=@resumes/Resume1.pdf" `
  -F "files=@resumes/Resume2.pdf" `
  -F 'keywords=["Python","Java","Manager"]' `
  -F "min_score=50" `
  -F "generate_ai_summary=false"
```

**Note:** In PowerShell, use backtick `` ` `` for line continuation, not backslash `\`

### 6. Access Generated CSV Files

CSV files are generated in the `output` folder:

```
GC_resumefilter\
  └── output\
      └── filtered_resumes_20251101_150441.csv
```

Open in Excel to test hyperlinks!

## Common Issues

### Issue: Docker daemon not running
**Solution:** Start Docker Desktop application

### Issue: Port 8000 already in use
**Solution:** Stop other services using port 8000 or change the port in docker-compose file:
```yaml
ports:
  - "8001:8000"  # Use 8001 on host instead
```

### Issue: Excel hyperlinks not working
**Solution:** Check your `RESUME_FOLDER_PATH` in `.env`:
1. Must be your Windows path (e.g., `D:\Work\...`)
2. Must be absolute path (not relative)
3. Restart container after changing: `docker-compose -f docker-compose.dev.yml restart`

### Issue: "File not found" when using curl
**Solution:** Make sure you're in the project root directory and the resume files exist:
```powershell
# Check current directory
pwd

# List resume files
dir resumes
```

## Stopping the Application

```powershell
# Stop containers (keeps data)
docker-compose -f docker-compose.dev.yml down

# Stop and remove all data
docker-compose -f docker-compose.dev.yml down -v
```

## Directory Structure

```
GC_resumefilter\
├── backend\              # Backend code
├── resumes\             # Put your resume PDFs here
├── output\              # Generated CSV files appear here
├── .env                 # Your configuration (create from .env.example)
├── .env.example         # Template
├── docker-compose.dev.yml   # Development config
└── docker-compose.prod.yml  # Production config
```

## Next Steps

- Add more resumes to the `resumes\` folder
- Adjust `MIN_KEYWORD_SCORE` in `.env` to change filtering threshold
- Enable OpenAI summaries by setting your API key
- Check the main README.md for advanced features

## Support

For issues or questions, refer to the main README.md or contact your system administrator.
