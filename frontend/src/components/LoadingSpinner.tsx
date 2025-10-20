import React from 'react';

interface SpinnerStyles {
  spinner: React.CSSProperties;
  container: React.CSSProperties;
}

const styles: SpinnerStyles = {
  spinner: {
    border: '4px solid rgba(0, 0, 0, 0.1)',
    width: '36px',
    height: '36px',
    borderRadius: '50%',
    borderLeftColor: '#09f',
    animation: 'spin 1s ease infinite',
  },
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    gap: '1rem',
    marginTop: '2rem',
    color: '#333',
  },
};

const keyframes = `
  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
`;

const LoadingSpinner = ({ message = 'Loading...' }: { message?: string }) => {
  return (
    <>
      <style>{keyframes}</style>
      <div style={styles.container}>
        <div style={styles.spinner}></div>
        <p>{message}</p>
      </div>
    </>
  );
};

export default LoadingSpinner;