// In frontend/src/components/UploadForm.tsx

import React, { useState } from 'react';
import styles from './UploadForm.module.css';

// _MODIFIED_: The interface is updated to define the new props we are receiving.
// TypeScript will now know that this component expects to receive these two test IDs.
interface UploadFormProps {
  isLoading: boolean;
  onSubmit: (files: FileList, title: string, description: string) => void;
  'data-testid-upload-input': string;
  'data-testid-evaluate-button': string;
}

// _MODIFIED_: We now destructure the new props from the props object.
const UploadForm = ({ isLoading, onSubmit, ...props }: UploadFormProps) => { 
  const [resumeFiles, setResumeFiles] = useState<FileList | null>(null);
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [error, setError] = useState<string | null>(null); 

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setResumeFiles(event.target.files);
    }
  };

  const handleLocalSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    setError(null); 

    if (!resumeFiles || resumeFiles.length === 0) {
      setError('Please select at least one resume file.');
      return;
    }
    if (!jobTitle.trim()) {
      setError('Please enter a job title.');
      return;
    }
    if (!jobDescription.trim()) {
      setError('Please enter a job description.');
      return;
    }
    
    onSubmit(resumeFiles, jobTitle, jobDescription);
  };

  return (
    <form onSubmit={handleLocalSubmit}>
      {error && <p style={{ color: 'red', marginBottom: '1rem' }}>{error}</p>}
      
      <div className={styles.formGroup}>
        <label htmlFor="resume-file" className={styles.label}>1. Upload Resumes (PDF or DOCX)</label>
        <input 
          type="file" 
          id="resume-file" 
          className={styles.input} 
          accept=".pdf,.docx" 
          onChange={handleFileChange} 
          multiple
          // _NEW_: We apply the test ID received from the parent to the file input.
          data-testid={props['data-testid-upload-input']}
        />
      </div>
      <div className={styles.formGroup}>
        <label htmlFor="job-title" className={styles.label}>2. Enter Job Title</label>
        <input 
          type="text" 
          id="job-title" 
          className={styles.input} 
          placeholder="e.g., Senior Python Developer" 
          value={jobTitle} 
          onChange={(e) => setJobTitle(e.target.value)} 
        />
      </div>
      <div className={styles.formGroup}>
        <label htmlFor="job-description" className={styles.label}>3. Paste Job Description</label>
        <textarea 
          id="job-description" 
          className={styles.textarea} 
          placeholder="Paste the full job description here..." 
          value={jobDescription} 
          onChange={(e) => setJobDescription(e.target.value)} 
        />
      </div>
      <button 
        type="submit" 
        className={styles.button} 
        disabled={isLoading}
        // _NEW_: We apply the test ID received from the parent to the submit button.
        data-testid={props['data-testid-evaluate-button']}
      >
        {isLoading ? 'Evaluating...' : 'Evaluate Candidates'}
      </button>
    </form>
  );
};

export default UploadForm;