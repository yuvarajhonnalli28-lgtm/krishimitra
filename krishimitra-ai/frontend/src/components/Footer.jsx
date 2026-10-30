import React from "react";
import { Link } from "react-router-dom";
import "./Footer.css";

function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-container">
        
        {/* About Section */}
        <div className="footer-section">
          <h3>🌾 KrishiMitra AI</h3>
          <p>
            Empowering farmers with AI-driven insights for smarter farming. 
            Disease detection, weather forecasts, market prices, and expert advice.
          </p>
        </div>

        {/* Quick Links */}
        <div className="footer-section">
          <h4>Quick Links</h4>
          <ul>
            <li><Link to="/">Home</Link></li>
            <li><Link to="/disease-detection">Disease Detection</Link></li>
            <li><Link to="/weather">Weather Forecast</Link></li>
            <li><Link to="/market">Market Prices</Link></li>
            <li><Link to="/advisor">AI Advisor</Link></li>
          </ul>
        </div>

        {/* Resources */}
        <div className="footer-section">
          <h4>Resources</h4>
          <ul>
            <li><a href="#">Farming Tips</a></li>
            <li><a href="#">Crop Calendar</a></li>
            <li><a href="#">Government Schemes</a></li>
            <li><a href="#">Training Videos</a></li>
          </ul>
        </div>

        {/* Contact */}
        <div className="footer-section">
          <h4>Contact Us</h4>
          <ul>
            <li>📞 +91 12345 67890</li>
            <li>📧 help@krishimitra.ai</li>
            <li>🌐 www.krishimitra.ai</li>
          </ul>
          <div className="social-links">
            <a href="#" title="Facebook">📘</a>
            <a href="#" title="Twitter">🐦</a>
            <a href="#" title="Instagram">📷</a>
            <a href="#" title="YouTube">▶️</a>
          </div>
        </div>
      </div>

      {/* Copyright */}
      <div className="footer-bottom">
        <p>&copy; {currentYear} KrishiMitra AI. All rights reserved.</p>
        <p>
          <Link to="/privacy">Privacy Policy</Link> | 
          <Link to="/terms">Terms of Use</Link>
        </p>
      </div>
    </footer>
  );
}

export default Footer;