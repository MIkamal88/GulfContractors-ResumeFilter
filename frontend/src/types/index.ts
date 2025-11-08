export interface ResumeAnalysis {
  filename: string;
  text_content: string;
  keywords_found: string[];
  keywords_missing: string[];
  score: number;
  ai_summary?: string;
  parsed_at: string;
}

export interface FilterResponse {
  total_resumes: number;
  valid_candidates: number;
  rejected_candidates: number;
  csv_file_path: string;
  candidates: ResumeAnalysis[];
}

export interface SingleAnalysisResponse {
  filename: string;
  score: number;
  matched_keywords: string[];
  ai_summary?: string;
}

export interface JobProfile {
  id: string;
  name: string;
  description: string;
  keywords: string[];
  category: string;
}

export interface JobProfilesResponse {
  profiles: JobProfile[];
  categories: string[];
}
