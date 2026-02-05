export interface EmploymentEntry {
  company: string;
  location: string;
  role: string;
  start_date: string;
  end_date: string;
  duration_years: number;
}

export interface ResumeAnalysis {
  filename: string;
  text_content: string;
  keywords_found: string[];
  keywords_missing: string[];
  score: number;
  ai_summary?: string;
  uae_presence?: boolean;
  employment_history?: EmploymentEntry[];
  total_experience_years?: number;
  is_image_based: boolean;
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
  double_weight_keywords?: string[];  // Keywords that count as 2x weight
  category: string;
}

export interface JobProfilesResponse {
  profiles: JobProfile[];
  categories: string[];
}
