import React from 'react';
import UploadPage from './pages/UploadPage.tsx';
import './App.css'; // We'll use this for some basic styling

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
        <p>&copy; 2024 Your Name</p>
      </footer>
    </div>
  );
}

export default App;