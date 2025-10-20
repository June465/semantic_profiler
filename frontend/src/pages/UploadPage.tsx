import React, { useState } from 'react';
import { uploadResume, createEvaluation, type EvaluationResult } from '../services/apiService';

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
    formGroup: { 
        marginBottom: '1.5rem' 
    },
    label: { display: 'block', 
        marginBottom: '0.5rem', 
        fontWeight: 'bold', 
        color: '#333' 
    },
    input: { 
        width: '100%', 
        padding: '0.75rem', 
        border: '1px solid #ccc', 
        borderRadius: '4px', 
        boxSizing: 'border-box' 
    },
    textarea: { 
        width: '100%', 
        padding: '0.75rem', 
        border: '1px solid #ccc', 
        borderRadius: '4px', 
        minHeight: '200px', 
        fontFamily: 'inherit', 
        fontSize: 'inherit', 
        boxSizing: 'border-box' 
    },
    button: { 
        display: 'block', 
        width: '100%', 
        padding: '1rem', 
        backgroundColor: '#007bff', 
        color: 'white', 
        border: 'none', 
        borderRadius: '4px', 
        fontSize: '1.1rem', 
        fontWeight: 'bold', 
        cursor: 'pointer' 
    },
    resultsContainer: { 
        marginTop: '2rem', 
        padding: '1.5rem', 
        border: '1px solid #ddd', 
        borderRadius: '8px', 
        backgroundColor: '#fff' 
    },
    resultsHeader: { 
        borderBottom: '2px solid #eee', 
        paddingBottom: '0.5rem', 
        marginBottom: '1rem' 
    }
};

const UploadPage = () => {
  const [resumeFiles, setResumeFiles] = useState<FileList | null>(null);
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [evaluationResults, setEvaluationResults] = useState<EvaluationResult[]>([]);
  const [skippedIds, setSkippedIds] = useState<number[]>([]);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setResumeFiles(event.target.files);
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
  event.preventDefault();
  if (!resumeFiles || resumeFiles.length === 0) {
    setError('Please select one or more resume files.');
    return;
  }
  if (!jobTitle.trim() || !jobDescription.trim()) {
    setError('Please fill out the job title and description.');
    return;
  }
  
  setIsLoading(true);
  setError(null);
  setEvaluationResults([]);
  setSkippedIds([]);

  try {
    console.log(`Step 1: Uploading ${resumeFiles.length} resume(s)...`);
    
    const uploadPromises = Array.from(resumeFiles).map(file => uploadResume(file));
    const uploadResponses = await Promise.all(uploadPromises);
    
    const resumeIds = uploadResponses.map(response => response.id);
    console.log(`Step 2: All resumes uploaded. IDs:`, resumeIds);

    if (resumeIds.length === 0) {
      throw new Error("None of the files could be uploaded successfully.");
    }

    console.log("Step 3: Creating evaluation for all resumes...");
    const evaluationResponse = await createEvaluation(resumeIds, jobTitle, jobDescription);
    console.log("Evaluation response received:", evaluationResponse);
    setEvaluationResults(evaluationResponse.successful_evaluations);
    setSkippedIds(evaluationResponse.skipped_resume_ids);

  } catch (err: any) {
    console.error("--- X. ENTERING CATCH BLOCK ---", err);
    let errorMessage = 'An error occurred. Check the console for details.';
    if (err.message) { errorMessage = err.message; }
    setError(errorMessage);
  } finally {
     console.log("--- Y. ENTERING FINALLY BLOCK ---");
    setIsLoading(false);
    console.log("--- Z. isLoading set to FALSE ---");
  }
};

  return (
    <div style={styles.container}>
      <h2>Upload and Evaluate</h2>
      <p>Submit resume(s) and a job description to get a detailed AI-powered analysis.</p>
      <form onSubmit={handleSubmit}>
        <div style={styles.formGroup}>
            <label htmlFor="resume-file" style={styles.label}>
                1. Upload Resume (PDF or DOCX)
            </label>
            <input type="file" id="resume-file" style={styles.input} accept=".pdf,.docx" onChange={handleFileChange} multiple />
        </div>
        <div style={styles.formGroup}>
            <label htmlFor="job-title" style={styles.label}>
                2. Enter Job Title
            </label>
            <input type="text" id="job-title" style={styles.input} placeholder="e.g., Senior Python Developer" value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} />
        </div>
        <div style={styles.formGroup}>
            <label htmlFor="job-description" style={styles.label}>
                3. Paste Job Description
            </label>
            <textarea id="job-description" style={styles.textarea} placeholder="Paste the full job description here..." value={jobDescription} onChange={(e) => setJobDescription(e.target.value)} />
        </div>
        <button type="submit" style={styles.button} disabled={isLoading}>
            {isLoading ? 'Evaluating...' : 'Evaluate Candidate'}
        </button>
      </form>
      {evaluationResults.length > 0 && (
        <div style={styles.resultsContainer}>
            <h3 style={styles.resultsHeader}>Comparison Results</h3>
            {evaluationResults
            .sort((a, b) => b.overall_score - a.overall_score)
            .map((result) => (
            <details key={result.id} style={{ marginBottom: '1rem', borderBottom: '1px solid #eee', paddingBottom: '1rem' }}>
                <summary style={{ fontWeight: 'bold', cursor: 'pointer', fontSize: '1.2rem' }}>
                  {`${result.candidate_name} - Score: ${result.overall_score}/100`}
                </summary>
                <div style={{ paddingLeft: '20px', marginTop: '1rem' }}>
                    <h4>Summary</h4>
                    <p>{result.summary}</p>
                    <h4>Strengths</h4>
                    <ul>
                        {result.strengths.map((strength, index) => (
                            <li key={`strength-${index}`}>{strength}</li>
                        ))}
                    </ul>
                    <h4>Weaknesses</h4>
                    <ul>
                        {result.weaknesses.map((weakness, index) => (
                            <li key={`weakness-${index}`}>{weakness}</li>
                        ))}
                    </ul>
                </div>
            </details>
          ))}
        </div>
      )}
    </div>
  );
};

export default UploadPage;