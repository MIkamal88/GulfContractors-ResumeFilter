# Resume Filter Backend

A FastAPI-based backend system that parses resumes, rates them based on keyword matching, generates AI summaries using OpenAI API, and exports qualified candidates to CSV.

## Features

- Parse resumes in PDF and DOCX formats
- Keyword-based scoring and filtering
- AI-powered resume summaries using OpenAI GPT-4o-mini
- Export valid candidates to CSV
- RESTful API endpoints
- Batch processing support

## Tech Stack

- **Framework**: FastAPI
- **Resume Parsing**: PyPDF2, python-docx
- **AI Integration**: OpenAI API
- **Data Export**: Pandas
- **Runtime**: Python 3.8+

## Installation

### 1. Clone or navigate to the repository

```bash
cd /mnt/D/Work/GulfContractors/GC_resumefilter
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
MIN_KEYWORD_SCORE=50
CSV_OUTPUT_PATH=./output/filtered_resumes.csv
```

## Usage

### Start the server

```bash
python main.py
```

Or using uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### 1. Health Check

```
GET /
```

Check if the API is running.

### 2. Filter Multiple Resumes

```
POST /filter-resumes
```

Upload multiple resumes, filter by keywords, and export valid candidates.

**Parameters:**
- `files`: Multiple resume files (PDF or DOCX)
- `keywords`: JSON array of keywords (e.g., `["Python", "FastAPI", "Docker"]`)
- `min_score`: Minimum score threshold (0-100, optional)
- `generate_ai_summary`: Generate AI summaries (true/false, default: true)

**Example using curl:**

```bash
curl -X POST "http://localhost:8000/filter-resumes" \
  -F "files=@resume1.pdf" \
  -F "files=@resume2.pdf" \
  -F "files=@resume3.docx" \
  -F 'keywords=["Python", "FastAPI", "Machine Learning", "Docker", "AWS"]' \
  -F "min_score=60" \
  -F "generate_ai_summary=true"
```

**Response:**

```json
{
  "total_resumes": 3,
  "valid_candidates": 2,
  "rejected_candidates": 1,
  "csv_file_path": "./output/filtered_resumes_20250130_143022.csv",
  "candidates": [
    {
      "filename": "resume1.pdf",
      "text_content": "...",
      "keywords_found": ["Python", "FastAPI", "Docker"],
      "keywords_missing": ["Machine Learning", "AWS"],
      "score": 60,
      "ai_summary": "Experienced Python developer with 5 years...",
      "parsed_at": "2025-01-30T14:30:22"
    }
  ]
}
```

### 3. Analyze Single Resume

```
POST /analyze-single
```

Analyze a single resume without filtering or CSV export.

**Parameters:**
- `file`: Single resume file (PDF or DOCX)
- `keywords`: JSON array of keywords
- `generate_ai_summary`: Generate AI summary (true/false, default: true)

**Example:**

```bash
curl -X POST "http://localhost:8000/analyze-single" \
  -F "file=@resume.pdf" \
  -F 'keywords=["Python", "FastAPI", "Docker"]' \
  -F "generate_ai_summary=true"
```

### 4. Download CSV

```
GET /download-csv?file_path=./output/filtered_resumes_20250130_143022.csv
```

Download a generated CSV file.

## Project Structure

```
GC_resumefilter/
├── main.py                 # FastAPI application and endpoints
├── models.py               # Pydantic models for request/response
├── config.py               # Configuration and settings
├── resume_parser.py        # Resume parsing (PDF, DOCX)
├── keyword_matcher.py      # Keyword matching and scoring
├── openai_service.py       # OpenAI API integration
├── csv_exporter.py         # CSV export functionality
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Configuration

Edit `.env` to customize:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `MIN_KEYWORD_SCORE`: Default minimum score threshold (default: 50)
- `CSV_OUTPUT_PATH`: Output path for CSV files (default: ./output/filtered_resumes.csv)

## CSV Output Format

The generated CSV includes:

| Column | Description |
|--------|-------------|
| Filename | Original resume filename |
| Score | Keyword match percentage (0-100) |
| Keywords Found | Comma-separated matched keywords |
| Keywords Missing | Comma-separated missing keywords |
| AI Summary | AI-generated candidate summary |
| Parsed At | Timestamp of analysis |

## How It Works

1. **Upload**: Resumes are uploaded via the API
2. **Parse**: Text is extracted from PDF/DOCX files
3. **Analyze**: Keywords are matched using regex patterns
4. **Score**: Percentage score is calculated based on matches
5. **Filter**: Candidates meeting the minimum score threshold are selected
6. **Summarize**: OpenAI generates professional summaries for valid candidates
7. **Export**: Results are exported to a timestamped CSV file

## Error Handling

- Invalid file formats return 400 Bad Request
- Missing OpenAI API key returns 500 Internal Server Error
- File parsing errors are logged and processing continues for other files
- AI summary failures don't block the filtering process

## Development

Run with auto-reload for development:

```bash
uvicorn main:app --reload
```

## License

Proprietary - Gulf Contractors

## Support

For issues or questions, contact the development team.
