import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

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

export const uploadResume = async (file: File): Promise<ResumeResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await axios.post<ResumeResponse>(`${API_BASE_URL}/resumes/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const createEvaluation = async (
  resumeIds: number[],
  jobTitle: string,
  jobDescription: string
): Promise<MassEvaluationResponse> => {
  const payload = {
    job_title: jobTitle,
    job_description: jobDescription,
    resume_ids: resumeIds,
  };

  const response = await axios.post<MassEvaluationResponse>(`${API_BASE_URL}/evaluations/`, payload);
  return response.data;
};

export const getAllEvaluations = async (): Promise<EvaluationResult[]> => {
  const response = await axios.get<EvaluationResult[]>(`${API_BASE_URL}/evaluations/`);
  return response.data;
};

export const getEvaluationById = async (id: number): Promise<EvaluationResult> => {
  const response = await axios.get<EvaluationResult>(`${API_BASE_URL}/evaluations/${id}`);
  return response.data;
};