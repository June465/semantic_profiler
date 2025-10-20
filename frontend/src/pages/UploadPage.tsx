import React, { useState } from 'react'; 

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    width: '100%',
    maxWidth: '800px',
    padding: '2rem',
    backgroundColor: '#f9f9f9',
    borderRadius: '8px',
    boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
  },
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
    boxSizing: 'border-box',
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

const UploadPage = () => {
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {

    if (event.target.files && event.target.files.length > 0) {
      setResumeFile(event.target.files[0]);
    }
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault(); 
    
    if (!resumeFile) {
      alert('Please select a resume file.');
      return;
    }
    
    console.log('Submitting the following data:');
    console.log('Resume File:', resumeFile);
    console.log('Job Title:', jobTitle);
    console.log('Job Description:', jobDescription);
  };


  return (
    <div style={styles.container}>
      <h2>Upload and Evaluate</h2>
      <p>Submit a resume and job description to get a detailed AI-powered analysis.</p>

      {/* --- 4. CONNECT FORM TO HANDLERS --- */}
      <form onSubmit={handleSubmit}>
        <div style={styles.formGroup}>
          <label htmlFor="resume-file" style={styles.label}>
            1. Upload Resume (PDF or DOCX)
          </label>
          <input
            type="file"
            id="resume-file"
            style={styles.input}
            accept=".pdf,.docx"
            onChange={handleFileChange} 
          />
        </div>

        <div style={styles.formGroup}>
          <label htmlFor="job-title" style={styles.label}>
            2. Enter Job Title
          </label>
          <input
            type="text"
            id="job-title"
            style={styles.input}
            placeholder="e.g., Senior Python Developer"
            value={jobTitle} 
            onChange={(e) => setJobTitle(e.target.value)} 
          />
        </div>

        <div style={styles.formGroup}>
          <label htmlFor="job-description" style={styles.label}>
            3. Paste Job Description
          </label>
          <textarea
            id="job-description"
            style={styles.textarea}
            placeholder="Paste the full job description here..."
            value={jobDescription} 
            onChange={(e) => setJobDescription(e.target.value)} 
          />
        </div>

        <button type="submit" style={styles.button}>
          Evaluate Candidate
        </button>
      </form>
    </div>
  );
};

export default UploadPage;