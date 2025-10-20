import React, { useState } from 'react';
import { createEvaluation, type EvaluationResult, type MassEvaluationResponse, uploadResume } from '../services/apiService';

import UploadForm from '../components/UploadForm';
import ResultsDisplay from '../components/ResultsDisplay';
import LoadingSpinner from '../components/LoadingSpinner';

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    width: '100%',
    maxWidth: '800px',
    padding: '2rem',
    backgroundColor: '#f9f9f9',
    borderRadius: '8px',
    boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
    color: '#333',
  },
};

const UploadPage = () => {
  // The parent page now only holds the important state
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [evaluationResults, setEvaluationResults] = useState<EvaluationResult[]>([]);
  const [skippedIds, setSkippedIds] = useState<number[]>([]);

  // The main submission logic stays here
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
      // ... (your existing robust error handling) ...
      setError('An error occurred during evaluation. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={styles.container}>
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