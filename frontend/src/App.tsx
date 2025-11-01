import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import UploadPage from './pages/UploadPage';
import DashboardPage from './pages/DashboardPage';
import LoginPage from './pages/LoginPage'; 
import ProtectedRoute from './components/ProtectedRoute'; 
import { useAuth } from './context/AuthContext'; 
import './App.css';

function App() {
  const auth = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    auth.logout();
    navigate('/login');
  };

  return (
    <div className="app-container">
      <header>
        <h1>Semantic Profiler</h1>
        <nav style={{ marginTop: '1rem', display: 'flex', gap: '1rem', justifyContent: 'center' }}>
          {auth.isAuthenticated && ( 
            <>
              <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>Evaluate</Link>
              <Link to="/dashboard" style={{ color: 'white', textDecoration: 'none' }}>Dashboard</Link>
              <button onClick={handleLogout} className="logout-button">Logout</button>
            </>
          )}
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route 
            path="/" 
            element={
              <ProtectedRoute>
                <UploadPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </main>
      <footer>
        <p>&copy; 2025 Your Name</p>
      </footer>
    </div>
  );
}

export default App;