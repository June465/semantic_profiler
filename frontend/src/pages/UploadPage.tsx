import React from 'react';

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    width: '100%', // Make it responsive within the grid
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
  return (
    <div style={styles.container}>
      <h2>Upload and Evaluate</h2>
      <p>Submit a resume and job description to get a detailed AI-powered analysis.</p>

      <form>
        <div style={styles.formGroup}>
          <label htmlFor="resume-file" style={styles.label}>
            1. Upload Resume (PDF or DOCX)
          </label>
          <input
            type="file"
            id="resume-file"
            style={styles.input}
            accept=".pdf,.docx"
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