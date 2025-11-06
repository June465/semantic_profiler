import { type EvaluationResult } from '../services/apiService';
import styles from './ResultsDisplay.module.css';

interface ResultsDisplayProps {
  results: EvaluationResult[];
  skippedIds: number[];
}

const BiasWarningIcon = () => (
  <span className={styles.warningIcon} title="Potential bias detected: Score changed significantly after anonymizing resume details.">
    ⚠️
  </span>
);

const ResultsDisplay = ({ results, skippedIds }: ResultsDisplayProps) => {
  const showResults = results.length > 0;
  const showSkipped = skippedIds.length > 0;

  if (!showResults && !showSkipped) {
    return null;
  }

  return (
    <>
      {showSkipped && (
        <div className={styles.notice}>
          <p>
            <strong>Notice:</strong> {skippedIds.length} resume(s) were skipped (IDs: {skippedIds.join(', ')}) because no relevant information was found.
          </p>
        </div>
      )}

      {showResults && (
        <div className={styles.resultsContainer}>
          <h3 className={styles.resultsHeader}>Comparison Results</h3>
          {results
            .sort((a, b) => b.overall_score - a.overall_score)
            .map((result) => (
              <details key={result.id} className={styles.details}>
                <summary className={styles.summary}>
                  <span>
                    {result.bias_flag && <BiasWarningIcon />}
                    {`${result.candidate_name} - Score: ${result.overall_score}/100`}
                    {result.percentile_rank !== null && (
                      <strong className={styles.percentile}>
                        {` (${result.percentile_rank.toFixed(0)}th Percentile)`}
                      </strong>
                    )}
                  </span>
                </summary>
              </details>
            ))}
        </div>
      )}
    </>
  );
};

export default ResultsDisplay;