import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom'; // Import Link from react-router-dom
import '../LoginForm.css'; // Import your CSS file for styling

const LoginForm = ({ login }) => {
    const navigate = useNavigate()
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (event) => {
    event.preventDefault(); // Prevent default form submission

    try {
      await login({ email, password });
      alert('Login successful!');
      navigate('/dashboard'); // Redirect to dashboard after loginvi
    } catch (error) {
      console.error('Login error:', error);
      alert('Login failed.');
    }
  };

  return (
    <div className="login-form-container">
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <div className="form-group">
          <label>Email:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="form-control"
            required
          />
        </div>
        <div className="form-group">
          <label>Password:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="form-control"
            required
          />
        </div>
        <button type="submit" className="btn btn-primary">
          Login
        </button>
      </form>
      <p>
        Don't have an account yet? <Link to="/register">Register here</Link>
      </p>
    </div>
  );
};

export default LoginForm;