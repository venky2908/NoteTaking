import React, { useState } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import Cookies from 'js-cookie';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import Dashboard from './components/Dashboard';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [accessToken, setAccessToken] = useState(Cookies.get('accessToken') || '');

  const register = async (userData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });
      if (!response.ok) {
        throw new Error('Registration failed');
      }
      const data = await response.json();
      setAccessToken(data.access_token);
      Cookies.set('accessToken', data.access_token, { expires: 7 }); // Set cookie for 7 days
    } catch (error) {
      console.error('Registration error:', error);
      alert('Registration failed.');
    }
  };

  const login = async (userData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });
      if (!response.ok) {
        throw new Error('Login failed');
      }
      const data = await response.json();
      setAccessToken(data.access_token);
      Cookies.set('accessToken', data.access_token, { expires: 7 }); // Set cookie for 7 days
    } catch (error) {
      console.error('Login error:', error);
      alert('Login failed.');
    }
  };

  const logout = async () => {
    try {
      await fetch(`${API_BASE_URL}/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });
      setAccessToken('');
      Cookies.remove('accessToken'); // Remove the access token cookie
    } catch (error) {
      console.error('Logout error:', error);
      alert('Logout failed.');
    }
  };

  return (
    <Router>
      <div>
        <Routes>
          <Route
            path="/register"
            element={<RegisterForm register={register} />}
          />
          <Route path="/login" element={<LoginForm login={login} />} />
          <Route
            path="/dashboard"
            element={<Dashboard accessToken={accessToken} logout={logout} />}
          />
          <Route path="/" element={<Navigate to="/login" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;