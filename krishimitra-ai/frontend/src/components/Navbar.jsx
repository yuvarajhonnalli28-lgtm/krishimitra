import React, { useContext, useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import "./Navbar.css";

function Navbar() {
  const { user, logout } = useContext(AuthContext);
  const { isDarkMode, toggleTheme } = useTheme();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
    // Close mobile menu if open
    setIsMenuOpen(false);
  };

  const navLinks = [
    { path: "/", label: "Home" },
    { path: "/disease-detection", label: "Disease Detection" },
    { path: "/weather", label: "Weather" },
    { path: "/market", label: "Market" },
    { path: "/advisor", label: "AI Advisor" },
  ];

  // Close menu when clicking outside (optional - you can add this with useEffect)

  return (
    <nav className="navbar">
      <div className="nav-container">
        
        {/* Logo */}
        <Link to="/" className="nav-logo" onClick={() => setIsMenuOpen(false)}>
          <span className="logo-icon">🌾</span>
          <span className="logo-text">KrishiMitra AI</span>
        </Link>

        {/* Mobile Menu Button */}
        <button 
          className="mobile-menu-btn"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          aria-label="Toggle menu"
        >
          {isMenuOpen ? "✕" : "☰"}
        </button>

        {/* Navigation Links */}
        <div className={`nav-links ${isMenuOpen ? "active" : ""}`}>
          {navLinks.map((link) => (
            <NavLink
              key={link.path}
              to={link.path}
              className={({ isActive }) => 
                isActive ? "nav-link active" : "nav-link"
              }
              onClick={() => setIsMenuOpen(false)}
            >
              {link.label}
            </NavLink>
          ))}
        </div>

        {/* Right Side Actions */}
        <div className="nav-actions">
          
          {/* Theme Toggle */}
          <button 
            onClick={toggleTheme} 
            className="theme-toggle" 
            title={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
            aria-label="Toggle theme"
          >
            {isDarkMode ? "☀️" : "🌙"}
          </button>

          {/* User Menu */}
          {user ? (
            <div className="user-menu">
              <span className="user-name" title={user.name || "Farmer"}>
                {user.name || "Farmer"}
              </span>
              <button 
                onClick={handleLogout} 
                className="btn btn-outline btn-small"
                aria-label="Logout"
              >
                Logout
              </button>
            </div>
          ) : (
            <div className="auth-buttons">
              <Link 
                to="/login" 
                className="btn btn-outline btn-small"
                onClick={() => setIsMenuOpen(false)}
              >
                Login
              </Link>
              <Link 
                to="/register" 
                className="btn btn-primary btn-small"
                onClick={() => setIsMenuOpen(false)}
              >
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;