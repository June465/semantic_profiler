import { createContext, useState, useContext, ReactNode, useEffect } from 'react'; // _MODIFIED_: Add useEffect
import { login as apiLogin, setAuthToken } from '../services/apiService';

interface AuthContextType {
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));

  // _NEW_: Add this useEffect hook.
  // This runs once when the app loads. If a token exists in localStorage,
  // it configures the apiClient to use it for all subsequent requests.
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setAuthToken(storedToken);
    }
  }, []); // The empty dependency array ensures this runs only once on mount.


  const login = async (username: string, password: string) => {
    try {
      const response = await apiLogin(username, password);
      const newToken = response.access_token;
      localStorage.setItem('token', newToken);
      setToken(newToken);
      setAuthToken(newToken); // Set token for future Axios requests
    } catch (error) {
      console.error("Login failed:", error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setAuthToken(null);
  };
  
  const isAuthenticated = !!token;

  return (
    <AuthContext.Provider value={{ token, login, logout, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};