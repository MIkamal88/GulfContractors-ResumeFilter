#!/bin/bash
curl -X POST "http://localhost:8000/filter-resumes" \
  -F "files=@resumes/CM Cv 1.pdf" \
  -F "files=@resumes/CM Cv 2.pdf" \
  -F 'keywords=["Infrastructure", "Roads", "Highways", "Sewer", "pump station", "pipeline", "storm water", "bridge", "Drainage Networks"]' \
  -F "min_score=0" \
  -F "generate_ai_summary=true"
