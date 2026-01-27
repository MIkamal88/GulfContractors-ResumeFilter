import axios from "axios";
import type {
  FilterResponse,
  SingleAnalysisResponse,
  JobProfilesResponse,
  JobProfile,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_URL || "/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "multipart/form-data",
  },
});

export const filterResumes = async (
  files: File[],
  keywords: string[],
  minScore: number = 0,
  generateAiSummary: boolean = true,
  doubleWeightKeywords: string[] = [],
): Promise<FilterResponse> => {
  const formData = new FormData();

  files.forEach((file) => {
    formData.append("files", file);
  });

  formData.append("keywords", JSON.stringify(keywords));
  formData.append("double_weight_keywords", JSON.stringify(doubleWeightKeywords));
  formData.append("min_score", minScore.toString());
  formData.append("generate_ai_summary", generateAiSummary.toString());

  const response = await api.post<FilterResponse>("/filter-resumes", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
};

export const analyzeSingleResume = async (
  file: File,
  keywords: string[],
  generateAiSummary: boolean = true,
  doubleWeightKeywords: string[] = [],
): Promise<SingleAnalysisResponse> => {
  const formData = new FormData();

  formData.append("file", file);
  formData.append("keywords", JSON.stringify(keywords));
  formData.append("double_weight_keywords", JSON.stringify(doubleWeightKeywords));
  formData.append("generate_ai_summary", generateAiSummary.toString());

  const response = await api.post<SingleAnalysisResponse>(
    "/analyze-single",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    },
  );

  return response.data;
};

export const downloadCSV = async (
  candidates: FilterResponse["candidates"],
): Promise<Blob> => {
  const response = await api.post("/download-csv", candidates, {
    headers: {
      "Content-Type": "application/json",
    },
    responseType: "blob",
  });

  return response.data;
};

export const openResume = (filename: string): void => {
  const url = `${API_BASE_URL}/view-resume/${encodeURIComponent(filename)}`;
  window.open(url, "_blank");
};

// Job Profiles API
export const getJobProfiles = async (): Promise<JobProfilesResponse> => {
  const response = await api.get<JobProfilesResponse>("/job-profiles", {
    headers: {
      "Content-Type": "application/json",
    },
  });
  return response.data;
};

export const getJobProfile = async (profileId: string): Promise<JobProfile> => {
  const response = await api.get<JobProfile>(`/job-profiles/${profileId}`, {
    headers: {
      "Content-Type": "application/json",
    },
  });
  return response.data;
};

export const createCustomProfile = async (
  profile: JobProfile,
): Promise<JobProfile> => {
  const response = await api.post<JobProfile>("/job-profiles", profile, {
    headers: {
      "Content-Type": "application/json",
    },
  });
  return response.data;
};

export const updateCustomProfile = async (
  profileId: string,
  profile: JobProfile,
): Promise<JobProfile> => {
  const response = await api.put<JobProfile>(
    `/job-profiles/${profileId}`,
    profile,
    {
      headers: {
        "Content-Type": "application/json",
      },
    },
  );
  return response.data;
};

export const deleteCustomProfile = async (profileId: string): Promise<void> => {
  await api.delete(`/job-profiles/${profileId}`, {
    headers: {
      "Content-Type": "application/json",
    },
  });
};

export default api;
