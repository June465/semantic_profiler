
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export interface ResumeResponse {
  id: number;
  filename: string;
  parsed_text: string;
  upload_date: string;
}

export interface EvaluationResult {
  id: number;
  resume_id: number;
  job_description_id: number;
  overall_score: number;
  strengths: string[];
  weaknesses: string[];
  summary: string;
  evaluation_date: string;
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
  resumeId: number,
  jobTitle: string,
  jobDescription: string
): Promise<EvaluationResult[]> => {
  const payload = {
    job_title: jobTitle,
    job_description: jobDescription,
    resume_ids: [resumeId],
  };

  const response = await axios.post<EvaluationResult[]>(`${API_BASE_URL}/evaluations/`, payload);
  return response.data;
};