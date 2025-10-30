import React from 'react';
import type { EvaluationResult } from '../services/apiService';

interface EvaluationModalProps {
  evaluation: EvaluationResult;
  onClose: () => void;
}

const API_BASE_URL = 'http://localhost:8000';

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
        <h4>Summary</h4>
        <p>{evaluation.summary}</p>
        <h4>Strengths</h4>
        <ul>{evaluation.strengths.map((s, i) => <li key={`s-${i}`}>{s}</li>)}</ul>
        <h4>Weaknesses</h4>
        <ul>{evaluation.weaknesses.map((w, i) => <li key={`w-${i}`}>{w}</li>)}</ul>
        <hr />
        <a href={resumeDownloadUrl} target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none', padding: '10px 15px', backgroundColor: '#007bff', color: 'white', borderRadius: '4px' }}>
          Download Resume
        </a>
      </div>
    </div>
  );
};

export default EvaluationModal;