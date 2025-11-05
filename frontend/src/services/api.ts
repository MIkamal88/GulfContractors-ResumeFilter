import axios from "axios";
import type { FilterResponse, SingleAnalysisResponse } from "../types";

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
): Promise<FilterResponse> => {
  const formData = new FormData();

  files.forEach((file) => {
    formData.append("files", file);
  });

  formData.append("keywords", JSON.stringify(keywords));
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
): Promise<SingleAnalysisResponse> => {
  const formData = new FormData();

  formData.append("file", file);
  formData.append("keywords", JSON.stringify(keywords));
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

export const downloadCSV = async (filePath: string): Promise<Blob> => {
  const response = await api.get("/download-csv", {
    params: { file_path: filePath },
    responseType: "blob",
  });

  return response.data;
};

export default api;
