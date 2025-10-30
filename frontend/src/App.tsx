import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import UploadPage from './pages/UploadPage';
import DashboardPage from './pages/DashboardPage';
import './App.css';

function App() {
  return (
    <div className="app-container">
      <header>
        <h1>Semantic Profiler</h1>
        <nav style={{ marginTop: '1rem', display: 'flex', gap: '1rem', justifyContent: 'center' }}>
          <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>Evaluate</Link>
          <Link to="/dashboard" style={{ color: 'white', textDecoration: 'none' }}>Dashboard</Link>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
        </Routes>
      </main>
      <footer>
        <p>&copy; 2025 Gowri Ajith<br></br>-23BCE1417, SCOPE, Computer Science and Engineering, VIT Chennai</p>
      </footer>
    </div>
  );
}

export default App;