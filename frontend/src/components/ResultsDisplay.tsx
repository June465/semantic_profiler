import React from 'react';
import { type EvaluationResult } from '../services/apiService';

interface ResultsDisplayProps {
  results: EvaluationResult[];
  skippedIds: number[];
}

const styles: { [key: string]: React.CSSProperties } = {
  resultsContainer: {
    marginTop: '2rem',
    padding: '1.5rem',
    border: '1px solid #ddd',
    borderRadius: '8px',
    backgroundColor: '#fff',
  },
  resultsHeader: {
    borderBottom: '2px solid #eee',
    paddingBottom: '0.5rem',
    marginBottom: '1rem',
  }
};

const ResultsDisplay = ({ results, skippedIds }: ResultsDisplayProps) => {
  const showResults = results.length > 0;
  const showSkipped = skippedIds.length > 0;

  if (!showResults && !showSkipped) {
    return null; 
  }

  return (
    <>
      {showSkipped && (
        <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#fffbe6', border: '1px solid #ffe58f', borderRadius: '4px' }}>
          <p>
            <strong>Notice:</strong> {skippedIds.length} resume(s) were skipped (IDs: {skippedIds.join(', ')}) because no relevant information was found for this job description.
          </p>
        </div>
      )}

      {showResults && (
        <div style={styles.resultsContainer}>
          <h3 style={styles.resultsHeader}>Comparison Results</h3>
          {results
            .sort((a, b) => b.overall_score - a.overall_score)
            .map((result) => (
              <details key={result.id} style={{ marginBottom: '1rem', borderBottom: '1px solid #eee', paddingBottom: '1rem' }}>
                <summary style={{ fontWeight: 'bold', cursor: 'pointer', fontSize: '1.2rem' }}>
                  {`${result.candidate_name} - Score: ${result.overall_score}/100`}
                </summary>
                <div style={{ paddingLeft: '20px', marginTop: '1rem' }}>
                  <h4>Summary</h4><p>{result.summary}</p>
                  <h4>Strengths</h4><ul>{result.strengths.map((s, i) => <li key={`s-${i}`}>{s}</li>)}</ul>
                  <h4>Weaknesses</h4><ul>{result.weaknesses.map((w, i) => <li key={`w-${i}`}>{w}</li>)}</ul>
                </div>
              </details>
            ))}
        </div>
      )}
    </>
  );
};

export default ResultsDisplay;