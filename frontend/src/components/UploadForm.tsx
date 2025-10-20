import React, { useState } from 'react';

interface UploadFormProps {
  isLoading: boolean;
  onSubmit: (files: FileList, title: string, description: string) => void;
}

const styles: { [key: string]: React.CSSProperties } = {
  formGroup: {
    marginBottom: '1.5rem',
  },
  label: {
    display: 'block',
    marginBottom: '0.5rem',
    fontWeight: 'bold',
    color: '#333',
  },
  input: {
    width: '100%',
    padding: '0.75rem',
    border: '1px solid #ccc',
    borderRadius: '4px',
    boxSizing: 'border-box', // TypeScript is happy with this specific value
  },
  textarea: {
    width: '100%',
    padding: '0.75rem',
    border: '1px solid #ccc',
    borderRadius: '4px',
    minHeight: '200px',
    fontFamily: 'inherit',
    fontSize: 'inherit',
    boxSizing: 'border-box',
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
    cursor: 'pointer',
  },
};

const UploadForm = ({ isLoading, onSubmit }: UploadFormProps) => {
  const [resumeFiles, setResumeFiles] = useState<FileList | null>(null);
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setResumeFiles(event.target.files);
    }
  };

  const handleLocalSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (resumeFiles && jobTitle.trim() && jobDescription.trim()) {
      onSubmit(resumeFiles, jobTitle, jobDescription);
    } else {
      alert('Please fill out all fields and select at least one resume.');
    }
  };

  return (
    <form onSubmit={handleLocalSubmit}>
      <div style={styles.formGroup}>
        <label htmlFor="resume-file" style={styles.label}>1. Upload Resumes (PDF or DOCX)</label>
        <input type="file" id="resume-file" style={styles.input} accept=".pdf,.docx" onChange={handleFileChange} multiple />
      </div>
      <div style={styles.formGroup}>
        <label htmlFor="job-title" style={styles.label}>2. Enter Job Title</label>
        <input type="text" id="job-title" style={styles.input} placeholder="e.g., Senior Python Developer" value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} />
      </div>
      <div style={styles.formGroup}>
        <label htmlFor="job-description" style={styles.label}>3. Paste Job Description</label>
        <textarea id="job-description" style={styles.textarea} placeholder="Paste the full job description here..." value={jobDescription} onChange={(e) => setJobDescription(e.target.value)} />
      </div>
      <button type="submit" style={styles.button} disabled={isLoading}>
        {isLoading ? 'Evaluating...' : 'Evaluate Candidates'}
      </button>
    </form>
  );
};

export default UploadForm;