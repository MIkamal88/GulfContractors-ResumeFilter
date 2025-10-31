"""
Example client script to test the Resume Filter API
"""

import requests
import json


def test_health_check():
    """Test the health check endpoint"""
    response = requests.get("http://localhost:8000/")
    print("Health Check:", response.json())


def analyze_single_resume(resume_path, keywords):
    """
    Test analyzing a single resume

    Args:
        resume_path: Path to the resume file
        keywords: List of keywords to search for
    """
    url = "http://localhost:8000/analyze-single"

    files = {'file': open(resume_path, 'rb')}
    data = {
        'keywords': json.dumps(keywords),
        'generate_ai_summary': True
    }

    response = requests.post(url, files=files, data=data)

    if response.status_code == 200:
        result = response.json()
        print("\n=== Resume Analysis ===")
        print(f"Filename: {result['filename']}")
        print(f"Score: {result['score']}%")
        print(f"Keywords Found: {', '.join(result['keywords_found'])}")
        print(f"Keywords Missing: {', '.join(result['keywords_missing'])}")
        print(f"\nAI Summary:\n{result['ai_summary']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())


def filter_multiple_resumes(resume_paths, keywords, min_score=50):
    """
    Test filtering multiple resumes

    Args:
        resume_paths: List of paths to resume files
        keywords: List of keywords to search for
        min_score: Minimum score threshold
    """
    url = "http://localhost:8000/filter-resumes"

    files = [('files', open(path, 'rb')) for path in resume_paths]
    data = {
        'keywords': json.dumps(keywords),
        'min_score': min_score,
        'generate_ai_summary': True
    }

    response = requests.post(url, files=files, data=data)

    if response.status_code == 200:
        result = response.json()
        print("\n=== Batch Filtering Results ===")
        print(f"Total Resumes: {result['total_resumes']}")
        print(f"Valid Candidates: {result['valid_candidates']}")
        print(f"Rejected: {result['rejected_candidates']}")
        print(f"CSV File: {result['csv_file_path']}")

        print("\n=== Valid Candidates ===")
        for candidate in result['candidates']:
            print(f"\n- {candidate['filename']} (Score: {candidate['score']}%)")
            print(f"  Keywords: {', '.join(candidate['keywords_found'])}")
            print(f"  Summary: {candidate['ai_summary'][:100]}...")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

    # Close all file handles
    for _, file_handle in files:
        file_handle.close()


if __name__ == "__main__":
    # Example usage
    print("Resume Filter API - Example Client\n")

    # Test health check
    test_health_check()

    # Example keywords for a software engineering position
    keywords = [
        "Python",
        "FastAPI",
        "Docker",
        "AWS",
        "Machine Learning",
        "REST API",
        "Git"
    ]

    # Example 1: Analyze a single resume
    # analyze_single_resume("path/to/resume.pdf", keywords)

    # Example 2: Filter multiple resumes
    # resume_files = [
    #     "path/to/resume1.pdf",
    #     "path/to/resume2.docx",
    #     "path/to/resume3.pdf"
    # ]
    # filter_multiple_resumes(resume_files, keywords, min_score=60)

    print("\n\nTo use this script:")
    print("1. Uncomment the example calls above")
    print("2. Replace the file paths with actual resume files")
    print("3. Adjust keywords as needed")
    print("4. Run: python example_client.py")
