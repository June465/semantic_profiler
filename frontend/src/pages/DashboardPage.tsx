import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { type EvaluationResult, getAllEvaluations } from '../services/apiService';
import LoadingSpinner from '../components/LoadingSpinner';

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
      <p>History of all candidate evaluations.</p>

      {isLoading && <LoadingSpinner message="Fetching history..." />}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      
      {!isLoading && !error && (
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Candidate Name</th>
              <th style={styles.th}>Score</th>
              <th style={styles.th}>Date</th>
              <th style={styles.th}>Summary</th>
            </tr>
          </thead>
          <tbody>
            {evaluations.map(e => (
              <tr key={e.id}>
                <td style={styles.td}>
                  <Link to={`/evaluations/${e.id}`}>{e.candidate_name}</Link>
                </td>
                <td style={styles.td}>{e.overall_score}/100</td>
                <td style={styles.td}>{new Date(e.evaluation_date).toLocaleDateString()}</td>
                <td style={styles.td}>{e.summary}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default DashboardPage;