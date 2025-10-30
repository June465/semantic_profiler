import React from 'react';
import type { EvaluationResult, ScoreBreakdown } from '../services/apiService';

interface EvaluationModalProps {
  evaluation: EvaluationResult;
  onClose: () => void;
}

const API_BASE_URL = 'http://localhost:8000';

const ScoreBreakdownChart = ({ scores }: { scores: ScoreBreakdown }) => {
  return (
    <div style={{ marginTop: '1.5rem', marginBottom: '1rem' }}>
      <h4>Score Breakdown</h4>
      {Object.entries(scores).map(([category, score]) => (
        <div key={category} style={{ marginBottom: '10px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
            <span>{category}</span>
            <strong>{score}</strong>
          </div>
          <div style={{ backgroundColor: '#e9ecef', borderRadius: '4px', height: '20px' }}>
            <div style={{
              width: `${score}%`,
              height: '100%',
              backgroundColor: score > 75 ? '#28a745' : score > 50 ? '#ffc107' : '#dc3545',
              borderRadius: '4px',
              transition: 'width 0.5s ease-in-out',
            }}></div>
          </div>
        </div>
      ))}
    </div>
  );
};

const modalOverlayStyle: React.CSSProperties = {
  position: 'fixed',
  top: 0,
  left: 0,
  width: '100%',
  height: '100%',
  backgroundColor: 'rgba(0,0,0,0.7)',
  zIndex: 1000,
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
};

const modalContentStyle: React.CSSProperties = {
  width: '80%',
  maxWidth: '800px',
  height: '90%',
  backgroundColor: 'white',
  padding: '2rem',
  borderRadius: '8px',
  overflowY: 'auto', 
  color: '#333', 
};

const closeButtonStyle: React.CSSProperties = {
  position: 'sticky', 
  top: '10px',        
  right: '10px',      
  float: 'right',     
  padding: '8px 12px',
  fontSize: '1rem',
  fontWeight: 'bold',
  cursor: 'pointer',
  border: 'none',
  borderRadius: '4px',
  backgroundColor: '#333',
  zIndex: 10,         
};

const BiasCheckDisplay = ({ evaluation }: { evaluation: EvaluationResult }) => {
  if (evaluation.anonymized_score === null) {
    return null; 
  }

  const discrepancyStyle: React.CSSProperties = {
    color: evaluation.bias_flag ? '#dc3545' : '#28a745',
    fontWeight: 'bold',
  };

  return (
    <div style={{ border: '1px solid #ddd', borderRadius: '4px', padding: '1rem', marginTop: '1.5rem', backgroundColor: '#f9f9f9' }}>
      <h4>Bias Check Analysis</h4>
      {evaluation.bias_flag && (
         <p style={{ color: '#dc3545', fontWeight: 'bold' }}>
           ⚠️ Warning: A significant score discrepancy was detected after removing personal information. This may indicate potential bias in the evaluation.
         </p>
      )}
      <p><strong>Original Score:</strong> {evaluation.overall_score}</p>
      <p><strong>Anonymized Score:</strong> {evaluation.anonymized_score}</p>
      <p><strong>Score Discrepancy:</strong> <span style={discrepancyStyle}>{evaluation.score_discrepancy?.toFixed(2)}</span> points</p>
    </div>
  );
};

const EvaluationModal = ({ evaluation, onClose }: EvaluationModalProps) => {
  const resumeDownloadUrl = `${API_BASE_URL}/resumes/${evaluation.resume_id}/file`;

  const handleOverlayClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (event.target === event.currentTarget) {
      onClose();
    }
  };

  return (
    <div style={modalOverlayStyle} onClick={handleOverlayClick}>
      <div style={modalContentStyle}>
        <button onClick={onClose} style={closeButtonStyle}>
          Close
        </button>
        <div style={{ clear: 'both' }}></div>
        
        <h2>Evaluation for {evaluation.candidate_name}</h2>
        <hr />
        <p><strong>Overall Score:</strong> {evaluation.overall_score}/100</p>
        
        <BiasCheckDisplay evaluation={evaluation} />
        
        {evaluation.score_breakdown && Object.keys(evaluation.score_breakdown).length > 0 && (
          <ScoreBreakdownChart scores={evaluation.score_breakdown} />
        )}
        
        <h4>Summary</h4>
        <p>{evaluation.summary}</p>
        <h4>Strengths</h4>
        <ul>{evaluation.strengths.map((s, i) => <li key={`s-${i}`}>{s}</li>)}</ul>
        <h4>Weaknesses</h4>
        <ul>{evaluation.weaknesses.map((w, i) => <li key={`w-${i}`}>{w}</li>)}</ul>
        <hr />
        <a href={resumeDownloadUrl} target="_blank" rel="noopener noreferrer" style={{ 
          textDecoration: 'none', 
          padding: '10px 15px', 
          backgroundColor: '#007bff', 
          color: 'white', 
          borderRadius: '4px' 
          }}>
          Download Resume
        </a>
      </div>
    </div>
  );
};

export default EvaluationModal;