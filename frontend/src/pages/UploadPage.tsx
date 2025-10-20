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
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [evaluationResult, setEvaluationResult] = useState<EvaluationResult | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => { if (event.target.files && event.target.files.length > 0) { setResumeFile(event.target.files[0]); } };

  // --- NEW INSTRUMENTED handleSubmit FUNCTION ---
  const handleSubmit = async (event: React.FormEvent) => {
    console.log("--- 1. handleSubmit START ---");
    event.preventDefault();
    console.log("--- 2. preventDefault called ---");

    if (!resumeFile || !jobTitle.trim() || !jobDescription.trim()) {
      console.error("--- VALIDATION FAILED ---");
      setError('Please fill out all fields and select a resume file.');
      return;
    }
    console.log("--- 3. Validation PASSED ---");
    
    setIsLoading(true);
    setError(null);
    setEvaluationResult(null);
    console.log("--- 4. UI state reset, isLoading is TRUE ---");

    try {
      console.log("--- 5. ENTERING try block ---");
      
      console.log("--- 6. Calling uploadResume... ---");
      const uploadResponse = await uploadResume(resumeFile);
      console.log("--- 7. uploadResume FINISHED. Response:", uploadResponse);

      if (!uploadResponse || typeof uploadResponse.id === 'undefined') {
        throw new Error("Server response did not contain a valid resume object.");
      }
      const resumeId = Number(uploadResponse.id);
      console.log("--- 8. Got resumeId:", resumeId);

      if (isNaN(resumeId) || resumeId <= 0) {
          throw new Error(`Invalid resume ID received: ${uploadResponse.id}`);
      }
      
      console.log("--- 9. Calling createEvaluation... ---");
      const evaluationResponse = await createEvaluation(resumeId, jobTitle, jobDescription);
      console.log("--- 10. createEvaluation FINISHED. Response:", evaluationResponse);
      
      if (evaluationResponse && evaluationResponse.length > 0) {
        console.log("--- 11. Setting evaluation result state ---");
        setEvaluationResult(evaluationResponse[0]);
      } else {
        throw new Error("Evaluation completed, but no result was returned.");
      }
      console.log("--- 12. LEAVING try block successfully ---");

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
      <p>Submit a resume and job description to get a detailed AI-powered analysis.</p>
      <form onSubmit={handleSubmit}>
        <div style={styles.formGroup}><label htmlFor="resume-file" style={styles.label}>1. Upload Resume (PDF or DOCX)</label><input type="file" id="resume-file" style={styles.input} accept=".pdf,.docx" onChange={handleFileChange} /></div>
        <div style={styles.formGroup}><label htmlFor="job-title" style={styles.label}>2. Enter Job Title</label><input type="text" id="job-title" style={styles.input} placeholder="e.g., Senior Python Developer" value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} /></div>
        <div style={styles.formGroup}><label htmlFor="job-description" style={styles.label}>3. Paste Job Description</label><textarea id="job-description" style={styles.textarea} placeholder="Paste the full job description here..." value={jobDescription} onChange={(e) => setJobDescription(e.target.value)} /></div>
        <button type="submit" style={styles.button} disabled={isLoading}>{isLoading ? 'Evaluating...' : 'Evaluate Candidate'}</button>
      </form>
      {isLoading && <p style={{ textAlign: 'center', marginTop: '1rem' }}>Loading... Evaluating candidate...</p>}
      {error && <p style={{ color: 'red', marginTop: '1rem' }}>Error: {error}</p>}
      {evaluationResult && (
        <div style={styles.resultsContainer}>
          <h3 style={styles.resultsHeader}>Evaluation Result</h3>
          <p><strong>Overall Score:</strong> {evaluationResult.overall_score}/100</p>
          <h4>Summary</h4><p>{evaluationResult.summary}</p>
          <h4>Strengths</h4><ul>{evaluationResult.strengths.map((strength: string, index: number) => (<li key={`strength-${index}`}>{strength}</li>))}</ul>
          <h4>Weaknesses</h4><ul>{evaluationResult.weaknesses.map((weakness: string, index: number) => (<li key={`weakness-${index}`}>{weakness}</li>))}</ul>
        </div>
      )}
    </div>
  );
};

export default UploadPage;