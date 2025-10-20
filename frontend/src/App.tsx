import React from 'react';
import UploadPage from './pages/UploadPage.tsx';
import './App.css';

function App() {
  return (
    <div className="app-container">
      <header>
        <h1>Semantic Profiler</h1>
      </header>
      <main>
        <UploadPage />
      </main>
      <footer>
        <p>&copy; 2025 Gowri Ajith<br></br>- 23BCE1417, SCOPE, Computer Science and Engineering, VIT Chennai </p>
      </footer>
    </div>
  );
}

export default App;