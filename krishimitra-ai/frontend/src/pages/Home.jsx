import React, { useContext } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import toast from "react-hot-toast";
import "./Home.css";

function Home() {
  const { user } = useContext(AuthContext);

  // Features data
  const features = [
    {
      id: 1,
      title: "🌱 Disease Detection",
      description: "Upload photos of your crops and instantly detect diseases using AI. Get treatment recommendations and prevention tips.",
      icon: "🔍",
      color: "#4caf50",
      link: "/disease-detection",
      stats: "95% accuracy"
    },
    {
      id: 2,
      title: "☀️ Weather Forecast",
      description: "Get accurate 7-day weather forecasts tailored for farming. Plan irrigation, harvesting, and protection measures.",
      icon: "🌤️",
      color: "#2196f3",
      link: "/weather",
      stats: "Real-time data"
    },
    {
      id: 3,
      title: "💰 Market Prices",
      description: "Live market prices for crops across different mandis. Make informed decisions about when and where to sell.",
      icon: "📈",
      color: "#ff9800",
      link: "/market",
      stats: "1000+ mandis"
    },
    {
      id: 4,
      title: "🤖 AI Advisor",
      description: "24/7 farming assistant. Ask questions about crops, fertilizers, pests, and get instant expert advice.",
      icon: "💬",
      color: "#9c27b0",
      link: "/advisor",
      stats: "Instant answers"
    }
  ];

  // Handle AI Advisor click
  const handleAdvisorClick = (e) => {
    if (!user) {
      e.preventDefault();
      toast.error("Please login to access AI Advisor", {
        icon: "🔒",
        duration: 3000,
        position: "top-center"
      });
    } else {
      toast.success("Welcome to KrishiMitra AI 🌾", {
        icon: "👋",
        duration: 2000
      });
    }
  };

  // Handle feature click (for features that might require login)
  const handleFeatureClick = (e, featureName, requiresAuth = false) => {
    if (requiresAuth && !user) {
      e.preventDefault();
      toast.error(`Please login to access ${featureName}`, {
        icon: "🔒",
        duration: 3000
      });
    }
  };

  return (
    <div className="home-page">

      {/* ===== HERO SECTION ===== */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            <span className="hero-title-main">KrishiMitra AI</span>
            <span className="hero-title-sub">Your Intelligent Farming Assistant</span>
          </h1>

          <p className="hero-description">
            Empowering farmers with AI-driven insights for disease detection, 
            weather forecasting, market prices, and expert advice — all in one place.
          </p>

          <div className="hero-buttons">
            <Link
              to="/advisor"
              className="btn btn-primary"
              onClick={handleAdvisorClick}
            >
              🤖 Ask AI Advisor
            </Link>

            <Link
              to="/weather"
              className="btn btn-secondary"
            >
              ☀️ Check Weather
            </Link>
          </div>

          {/* Stats Banner */}
          <div className="stats-banner">
            <div className="stat-item">
              <span className="stat-number">10K+</span>
              <span className="stat-label">Happy Farmers</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">50K+</span>
              <span className="stat-label">Diseases Detected</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">95%</span>
              <span className="stat-label">Accuracy Rate</span>
            </div>
          </div>
        </div>

        <div className="hero-image">
          <div className="farming-illustration">
            <span>🌾</span>
            <span>🌱</span>
            <span>🌽</span>
          </div>
        </div>
      </section>

      {/* ===== FEATURES SECTION ===== */}
      <section className="features-section">
        <div className="section-header">
          <h2>Our Features</h2>
          <p>Everything you need to manage your farm efficiently</p>
        </div>

        <div className="features-grid">
          {features.map((feature) => (
            <Link
              to={feature.link}
              key={feature.id}
              className="feature-card-link"
              onClick={(e) => handleFeatureClick(e, feature.title, feature.link === "/advisor")}
            >
              <div className="feature-card" style={{ borderTop: `4px solid ${feature.color}` }}>
                <div className="feature-icon" style={{ backgroundColor: feature.color + '20' }}>
                  <span>{feature.icon}</span>
                </div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
                <div className="feature-footer">
                  <span className="feature-stats">{feature.stats}</span>
                  <span className="feature-arrow">→</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* ===== HOW IT WORKS SECTION ===== */}
      <section className="how-it-works">
        <div className="section-header">
          <h2>How It Works</h2>
          <p>Three simple steps to smarter farming</p>
        </div>

        <div className="steps-container">
          <div className="step-item">
            <div className="step-number">1</div>
            <h3>Upload or Ask</h3>
            <p>Upload a photo of your crop or type your farming question</p>
          </div>
          <div className="step-item">
            <div className="step-number">2</div>
            <h3>AI Analysis</h3>
            <p>Our advanced AI analyzes your input using the latest models</p>
          </div>
          <div className="step-item">
            <div className="step-number">3</div>
            <h3>Get Results</h3>
            <p>Receive instant recommendations, treatments, and solutions</p>
          </div>
        </div>
      </section>

      {/* ===== TESTIMONIALS SECTION ===== */}
      <section className="testimonials-section">
        <div className="section-header">
          <h2>What Farmers Say</h2>
          <p>Trusted by thousands of farmers across India</p>
        </div>

        <div className="testimonials-grid">
          <div className="testimonial-card">
            <div className="testimonial-rating">⭐⭐⭐⭐⭐</div>
            <p className="testimonial-content">
              "KrishiMitra AI helped me detect wheat rust early. Saved my entire crop from destruction!"
            </p>
            <div className="testimonial-author">
              <strong>Rajesh Kumar</strong>
              <span>Wheat Farmer, Punjab</span>
            </div>
          </div>

          <div className="testimonial-card">
            <div className="testimonial-rating">⭐⭐⭐⭐⭐</div>
            <p className="testimonial-content">
              "The weather forecast feature is very accurate. Helped me plan my irrigation perfectly during dry spell."
            </p>
            <div className="testimonial-author">
              <strong>Lakshmi Devi</strong>
              <span>Vegetable Farmer, Tamil Nadu</span>
            </div>
          </div>

          <div className="testimonial-card">
            <div className="testimonial-rating">⭐⭐⭐⭐</div>
            <p className="testimonial-content">
              "Market prices helped me get 20% more profit by choosing the right mandi to sell my tomatoes."
            </p>
            <div className="testimonial-author">
              <strong>Mohammad Ali</strong>
              <span>Tomato Farmer, Uttar Pradesh</span>
            </div>
          </div>
        </div>
      </section>

      {/* ===== CALL TO ACTION SECTION ===== */}
      <section className="cta-section">
        <div className="cta-content">
          <h2>Ready to transform your farming?</h2>
          <p>Join thousands of farmers who are already using KrishiMitra AI to grow better</p>
          
          {user ? (
            <Link to="/dashboard" className="btn btn-primary btn-large">
              Go to Dashboard
            </Link>
          ) : (
            <Link to="/signup" className="btn btn-primary btn-large">
              Start Using KrishiMitra AI Free
            </Link>
          )}
          
          <p className="cta-note">✓ No credit card required ✓ Free for farmers ✓ 24/7 Support</p>
        </div>
      </section>
    </div>
  );
}

export default Home;