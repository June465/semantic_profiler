import React, { useState, useEffect } from 'react';
import { type EvaluationResult, getAllEvaluations } from '../services/apiService';
import LoadingSpinner from '../components/LoadingSpinner';
import EvaluationModal from '../components/EvaluationModal'; 

const API_BASE_URL = 'http://localhost:8000'; 

const styles: { [key: string]: React.CSSProperties } = {
    container: { width: '100%', maxWidth: '1000px', margin: '0 auto', padding: '2rem', color: '#333' },
    table: { width: '100%', borderCollapse: 'collapse', marginTop: '2rem', backgroundColor: 'white' },
    th: { border: '1px solid #ddd', padding: '12px', textAlign: 'left', backgroundColor: '#f2f2f2' },
    td: { border: '1px solid #ddd', padding: '12px' },
};

const DashboardPage = () => {
  const [evaluations, setEvaluations] = useState<EvaluationResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEvaluation, setSelectedEvaluation] = useState<EvaluationResult | null>(null);

  useEffect(() => {
    const fetchEvaluations = async () => {
      try {
        setIsLoading(true);
        const data = await getAllEvaluations();
        setEvaluations(data.sort((a, b) => new Date(b.evaluation_date).getTime() - new Date(a.evaluation_date).getTime()));
      } catch (err) {
        setError('Failed to fetch evaluation history.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchEvaluations();
  }, []); 

  return (
    <div style={styles.container}>
      <h2>Evaluation Dashboard</h2>
      
      <table style={styles.table}>
        <thead>
          <tr>
            <th style={styles.th}>Candidate Name</th>
            <th style={styles.th}>Score</th>
            <th style={styles.th}>Date</th>
            <th style={styles.th}>Actions</th> 
          </tr>
        </thead>
        <tbody>
          {evaluations.map(e => {
            const resumeDownloadUrl = `${API_BASE_URL}/resumes/${e.resume_id}/file`;
            return (
              <tr key={e.id}>
                <td style={styles.td}>
                  <a href={resumeDownloadUrl} target="_blank" rel="noopener noreferrer">{e.candidate_name}</a>
                </td>
                <td style={styles.td}>{e.overall_score}/100</td>
                <td style={styles.td}>{new Date(e.evaluation_date).toLocaleDateString()}</td>
                <td style={styles.td}>
                  <button onClick={() => setSelectedEvaluation(e)}>View Details</button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {selectedEvaluation && (
        <EvaluationModal 
          evaluation={selectedEvaluation}
          onClose={() => setSelectedEvaluation(null)}
        />
      )}
    </div>
  );
};

export default DashboardPage;