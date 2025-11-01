// In frontend/src/pages/DashboardPage.tsx
import { useState, useEffect } from 'react';
import { getAllEvaluations } from '../services/apiService';
import type { EvaluationResult } from '../services/apiService';
import EvaluationModal from '../components/EvaluationModal';
import styles from './DashboardPage.module.css';

const DashboardPage = () => {
  const [evaluations, setEvaluations] = useState<EvaluationResult[]>([]);
  const [selectedEvaluation, setSelectedEvaluation] = useState<EvaluationResult | null>(null);
  // _FIXED_: These are now used
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEvaluations = async () => {
      try {
        const data = await getAllEvaluations();
        setEvaluations(data.sort((a, b) => new Date(b.evaluation_date).getTime() - new Date(a.evaluation_date).getTime()));
      } catch (err) {
        setError('Failed to fetch evaluation history.');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchEvaluations();
  }, []);

  // _FIXED_: Add UI for loading and error states
  if (isLoading) {
    return <div className={styles.centered}>Loading evaluation history...</div>;
  }

  if (error) {
    return <div className={`${styles.centered} ${styles.error}`}>{error}</div>;
  }

  return (
    <div className={styles.dashboardContainer}>
      <h2>Evaluation History</h2>
      {evaluations.length === 0 ? (
        <p>No evaluations have been performed yet.</p>
      ) : (
      <table className={styles.evalTable}>
        <thead>
          <tr>
            <th>Candidate Name</th>
            <th>Overall Score</th>
            <th>Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {evaluations.map((evaluation) => (
            <tr key={evaluation.id}>
              <td>{evaluation.candidate_name}</td>
              <td>{evaluation.overall_score}</td>
              <td>{new Date(evaluation.evaluation_date).toLocaleString()}</td>
              <td>
                <button onClick={() => setSelectedEvaluation(evaluation)}>View Details</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      )}

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