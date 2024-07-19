import React from "react";
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css'; // Global styles
import './App.css'; // Include app-specific styles
import './Dashboard.css'; // Dashboard-specific styles
import './LoginForm.css'; // Login form-specific styles
import './RegisterForm.css'; // Register form-specific styles

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);
