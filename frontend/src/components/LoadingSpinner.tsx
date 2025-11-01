import styles from './LoadingSpinner.module.css'; 

const LoadingSpinner = ({ message = 'Loading...' }: { message?: string }) => {
  return (
    <div className={styles.container}>
      <div className={styles.spinner}></div>
      <p>{message}</p>
    </div>
  );
};

export default LoadingSpinner;