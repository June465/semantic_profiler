// In frontend/src/services/apiService.ts
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

export const setAuthToken = (token: string | null) => {
  if (token) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete apiClient.defaults.headers.common['Authorization'];
  }
};

// --- Interfaces ---
export interface ResumeResponse {
  id: number;
  filename: string;
  parsed_text: string;
  upload_date: string;
}

export type ScoreBreakdown = { [key: string]: number };

export interface EvaluationResult {
  id: number;
  resume_id: number;
  job_description_id: number;
  candidate_name: string;
  overall_score: number;
  strengths: string[];
  weaknesses: string[];
  summary: string;
  evaluation_date: string;
  score_breakdown: ScoreBreakdown | null;
  anonymized_score: number | null;
  score_discrepancy: number | null;
  bias_flag: boolean;
}

export interface MassEvaluationResponse {
  successful_evaluations: EvaluationResult[];
  skipped_resume_ids: number[];
}

// _NEW & FIXED_: Add the missing TokenResponse interface
interface TokenResponse {
  access_token: string;
  token_type: string;
}

// --- API Functions ---
export const login = async (username: string, password: string): Promise<TokenResponse> => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await axios.post<TokenResponse>(`${API_BASE_URL}/auth/token`, formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
};

export const uploadResume = async (file: File): Promise<ResumeResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await apiClient.post<ResumeResponse>('/resumes/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

// _FIXED_: Removed the unused variables from the function signature
export const createEvaluation = async (
  resumeIds: number[],
  jobTitle: string,
  jobDescription: string
): Promise<MassEvaluationResponse> => {
  // _FIXED_: Re-added the payload that was missing
  const payload = {
    job_title: jobTitle,
    job_description: jobDescription,
    resume_ids: resumeIds,
  };
  const response = await apiClient.post<MassEvaluationResponse>('/evaluations/', payload);
  return response.data;
};

export const getAllEvaluations = async (): Promise<EvaluationResult[]> => {
  const response = await apiClient.get<EvaluationResult[]>('/evaluations/');
  return response.data;
};

export const getEvaluationById = async (id: number): Promise<EvaluationResult> => {
  const response = await apiClient.get<EvaluationResult>(`/evaluations/${id}`);
  return response.data;
};