import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";

// Layout Components
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";

// Page Components
import Home from "./pages/Home";
import DiseaseDetection from "./pages/DiseaseDetection";
import WeatherForecast from "./pages/WeatherForecast";
import CropMarket from "./pages/CropMarket";
import AIAdvisor from "./pages/AIAdvisor";

// Auth Pages
import Login from "./pages/Login";
import Register from "./pages/Register";
import Profile from "./pages/Profile";

// Chat Widget Component
import ChatWidget from "./components/ChatWidget";

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const isAuthenticated = localStorage.getItem("token"); // Simple check
  return isAuthenticated ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <div className="app">
      <Navbar />
      
      <main className="main-content">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Home />} />
          <Route path="/disease-detection" element={<DiseaseDetection />} />
          <Route path="/weather" element={<WeatherForecast />} />
          <Route path="/market" element={<CropMarket />} />
          <Route path="/advisor" element={<AIAdvisor />} />
          
          {/* Auth Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected Routes */}
          <Route 
            path="/profile" 
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } 
          />
          
          {/* 404 Route */}
          <Route 
            path="*" 
            element={
              <div className="not-found">
                <h1>404</h1>
                <h2>Page Not Found</h2>
                <p>The page you're looking for doesn't exist.</p>
                <a href="/" className="btn btn-primary">Go Home</a>
              </div>
            } 
          />
        </Routes>
      </main>
      
      {/* Chat Widget - appears on all pages */}
      <ChatWidget />
      
      <Footer />
    </div>
  );
}

export default App;