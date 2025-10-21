import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getEvaluationById, type EvaluationResult } from '../services/apiService';
import LoadingSpinner from '../components/LoadingSpinner';

const API_BASE_URL = 'http://localhost:8000'; 

const EvaluationDetailPage = () => {
  const { evaluationId } = useParams<{ evaluationId: string }>();
  const [evaluation, setEvaluation] = useState<EvaluationResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showResume, setShowResume] = useState(false);

  useEffect(() => {
    const fetchEvaluation = async () => {
      if (!evaluationId) return;
      try {
        const data = await getEvaluationById(Number(evaluationId));
        setEvaluation(data);
      } catch (err) {
        setError('Failed to fetch evaluation details.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchEvaluation();
  }, [evaluationId]);

  if (isLoading) return <LoadingSpinner message="Loading details..." />;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;
  if (!evaluation) return <p>Evaluation not found.</p>;

  const resumeUrl = `${API_BASE_URL}/resumes/${evaluation.resume_id}/file`;

  return (
    <div style={{ maxWidth: '800px', margin: '2rem auto', padding: '2rem', backgroundColor: '#fff', color: '#333' }}>
      <h2>Evaluation for {evaluation.candidate_name}</h2>
      <button onClick={() => setShowResume(true)} style={{ marginBottom: '1rem' }}>View Original Resume</button>

      {showResume && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: 'rgba(0,0,0,0.7)', zIndex: 1000, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <div style={{ width: '80%', height: '90%', backgroundColor: 'white', padding: '1rem' }}>
            <button onClick={() => setShowResume(false)} style={{ float: 'right' }}>Close</button>
            <iframe src={resumeUrl} width="100%" height="95%" title="Resume Viewer"></iframe>
          </div>
        </div>
      )}

      <p><strong>Overall Score:</strong> {evaluation.overall_score}/100</p>
      <h4>Summary</h4><p>{evaluation.summary}</p>
      <h4>Strengths</h4>
      <ul>{evaluation.strengths.map((s, i) => <li key={`s-${i}`}>{s}</li>)}</ul>
      <h4>Weaknesses</h4>
      <ul>{evaluation.weaknesses.map((w, i) => <li key={`w-${i}`}>{w}</li>)}</ul>
    </div>
  );
};

export default EvaluationDetailPage;