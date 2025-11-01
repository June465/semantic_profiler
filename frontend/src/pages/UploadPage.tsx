import { useState } from 'react';
import { createEvaluation, type EvaluationResult } from '../services/apiService';
import { uploadResume } from '../services/apiService';
import styles from './UploadPage.module.css'; 

import UploadForm from '../components/UploadForm';
import ResultsDisplay from '../components/ResultsDisplay';
import LoadingSpinner from '../components/LoadingSpinner';

const UploadPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [evaluationResults, setEvaluationResults] = useState<EvaluationResult[]>([]);
  const [skippedIds, setSkippedIds] = useState<number[]>([]);

  const handleFormSubmit = async (files: FileList, title: string, description: string) => {
    setIsLoading(true);
    setError(null);
    setEvaluationResults([]);
    setSkippedIds([]);
    
    try {
      const uploadPromises = Array.from(files).map(file => uploadResume(file));
      const uploadResponses = await Promise.all(uploadPromises);
      const resumeIds = uploadResponses.map(response => response.id);
      
      if (resumeIds.length === 0) throw new Error("File uploads failed.");

      const evalResponse = await createEvaluation(resumeIds, title, description);
      setEvaluationResults(evalResponse.successful_evaluations);
      setSkippedIds(evalResponse.skipped_resume_ids);
    } catch (err: any) {
      setError('An error occurred during evaluation. Please check the console.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <h2>Upload and Evaluate</h2>
      <p>Submit resumes and a job description to get a detailed AI-powered analysis.</p>

      <UploadForm isLoading={isLoading} onSubmit={handleFormSubmit} />
      
      {isLoading && <LoadingSpinner message="Evaluating, please wait..." />}
      {error && <p style={{ color: 'red', marginTop: '1rem' }}>Error: {error}</p>}
      
      {!isLoading && <ResultsDisplay results={evaluationResults} skippedIds={skippedIds} />}
    </div>
  );
};

export default UploadPage;