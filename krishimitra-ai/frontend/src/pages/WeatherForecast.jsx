// Weather forecast page
import React, { useState, useEffect, useContext } from "react";
import { Link } from "react-router-dom";  // 👈 FIX 2: Added missing Link import
import { AuthContext } from "../context/AuthContext";
import toast from "react-hot-toast";
import WeatherCard from "../components/WeatherCard";
import "./WeatherForecast.css";

// 👈 FIX 1: Fixed variable name (removed space)
const API_BASE_URL = "http://localhost:8000/api";

function WeatherForecast() {
  const { user } = useContext(AuthContext);
  
  // State for weather data
  const [currentWeather, setCurrentWeather] = useState(null);
  const [forecast, setForecast] = useState([]);
  const [advisory, setAdvisory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // State for user input
  const [location, setLocation] = useState("");
  const [searchLocation, setSearchLocation] = useState("");
  const [forecastDays, setForecastDays] = useState(5);

  // Fetch weather data on component mount
  useEffect(() => {
    fetchWeatherData();
  }, []);

  // Fetch weather data from backend
  const fetchWeatherData = async (customLocation = "") => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch current weather
      const weatherUrl = customLocation 
        ? `${API_BASE_URL}/weather/location/${encodeURIComponent(customLocation)}`
        : `${API_BASE_URL}/weather/`;
      
      console.log("Fetching weather from:", weatherUrl); // For debugging
      const weatherRes = await fetch(weatherUrl);
      
      if (!weatherRes.ok) {
        const errorData = await weatherRes.json();
        throw new Error(errorData.detail || "Failed to fetch weather data");
      }
      
      const weatherData = await weatherRes.json();
      setCurrentWeather(weatherData);

      // Fetch forecast
      const forecastUrl = customLocation
        ? `${API_BASE_URL}/weather/forecast?days=${forecastDays}&location=${encodeURIComponent(customLocation)}`
        : `${API_BASE_URL}/weather/forecast?days=${forecastDays}`;
      
      const forecastRes = await fetch(forecastUrl);
      if (!forecastRes.ok) throw new Error("Failed to fetch forecast");
      
      const forecastData = await forecastRes.json();
      setForecast(forecastData.forecast || []);

      // Fetch daily advisory (if logged in)
      if (user) {
        const advisoryRes = await fetch(`${API_BASE_URL}/weather/advisory/daily`);
        if (advisoryRes.ok) {
          const advisoryData = await advisoryRes.json();
          setAdvisory(advisoryData);
        }
      }

      toast.success("Weather data updated successfully!");

    } catch (err) {
      setError(err.message);
      toast.error("Failed to load weather data. Please try again.");
      console.error("Weather fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  // Handle location search
  const handleSearch = (e) => {
    e.preventDefault();
    if (searchLocation.trim()) {
      setLocation(searchLocation);
      fetchWeatherData(searchLocation);
      toast.success(`Loading weather for ${searchLocation}...`);
    }
  };

  // Handle refresh
  const handleRefresh = () => {
    fetchWeatherData(location);
    toast.success("Weather data refreshed!");
  };

  // 👈 FIX 3: Handle forecast days change
  const handleDaysChange = (days) => {
    setForecastDays(days);
    // Small delay to ensure state updates before fetching
    setTimeout(() => {
      fetchWeatherData(location);
    }, 100);
  };

  // Get weather icon based on condition
  const getWeatherIcon = (condition) => {
    const icons = {
      "Sunny": "☀️",
      "Cloudy": "☁️",
      "Partly Cloudy": "⛅",
      "Rainy": "🌧️",
      "Thunderstorm": "⛈️",
      "Clear": "🌙",
      "default": "🌤️"
    };
    return icons[condition] || icons.default;
  };

  if (loading && !currentWeather) {
    return (
      <div className="weather-loading">
        <div className="spinner"></div>
        <p>Fetching weather data...</p>
      </div>
    );
  }

  return (
    <div className="weather-page">
      
      {/* Header Section */}
      <div className="weather-header">
        <h1>🌤️ Weather Forecast</h1>
        <p>Get accurate weather updates tailored for your farm</p>
      </div>

      {/* Search Bar */}
      <form onSubmit={handleSearch} className="weather-search">
        <input
          type="text"
          placeholder="Enter your village/city name (e.g., Pune, Delhi)"
          value={searchLocation}
          onChange={(e) => setSearchLocation(e.target.value)}
          className="search-input"
        />
        <button type="submit" className="btn btn-primary search-btn">
          🔍 Search
        </button>
        <button type="button" className="btn btn-outline refresh-btn" onClick={handleRefresh}>
          🔄 Refresh
        </button>
      </form>

      {/* Error Display */}
      {error && (
        <div className="error-message">
          <p>❌ {error}</p>
          <button onClick={() => fetchWeatherData(location)} className="btn btn-outline">
            Try Again
          </button>
        </div>
      )}

      {/* Current Weather */}
      {currentWeather && (
        <div className="current-weather-card">
          <div className="weather-location">
            <h2>{currentWeather.location || "Current Location"}</h2>
            <span className="weather-timestamp">
              Last updated: {new Date(currentWeather.timestamp).toLocaleString()}
            </span>
          </div>

          <div className="weather-main">
            <div className="weather-icon-large">
              {getWeatherIcon(currentWeather.condition)}
            </div>
            <div className="weather-temp-large">
              {currentWeather.temperature}°C
            </div>
            <div className="weather-condition">
              {currentWeather.condition}
            </div>
          </div>

          <div className="weather-details-grid">
            <div className="weather-detail-item">
              <span className="detail-label">💧 Humidity</span>
              <span className="detail-value">{currentWeather.humidity}%</span>
            </div>
            <div className="weather-detail-item">
              <span className="detail-label">🌧️ Rain Chance</span>
              <span className="detail-value">{currentWeather.rain_chance || 0}%</span>
            </div>
            <div className="weather-detail-item">
              <span className="detail-label">💨 Wind Speed</span>
              <span className="detail-value">{currentWeather.wind_speed} km/h</span>
            </div>
            <div className="weather-detail-item">
              <span className="detail-label">🌡️ Rainfall</span>
              <span className="detail-value">{currentWeather.rainfall || 0} mm</span>
            </div>
          </div>

          {currentWeather.advice && (
            <div className="weather-advice">
              <strong>🌱 Farming Advice:</strong>
              <p>{currentWeather.advice}</p>
            </div>
          )}
        </div>
      )}

      {/* Daily Advisory (for logged in users) */}
      {advisory && user && (
        <div className="advisory-card">
          <h3>📋 Today's Farming Advisory</h3>
          <p className="advisory-date">For {new Date(advisory.date).toLocaleDateString()}</p>
          
          <div className="advisory-content">
            <div className="advisory-section">
              <h4>✅ Recommended Tasks</h4>
              <ul>
                {advisory.farming_tasks?.map((task, index) => (
                  <li key={index}>{task}</li>
                ))}
              </ul>
            </div>
            
            <div className="advisory-section">
              <h4>⚠️ Cautions</h4>
              <ul>
                {advisory.cautions?.map((caution, index) => (
                  <li key={index}>{caution}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* 5-Day Forecast */}
      {forecast.length > 0 && (
        <div className="forecast-section">
          <div className="forecast-header">
            <h3>📅 {forecastDays}-Day Forecast</h3>
            <div className="forecast-days-selector">
              <button 
                className={`days-btn ${forecastDays === 3 ? 'active' : ''}`}
                onClick={() => handleDaysChange(3)}  // 👈 FIX 3: Using handler
              >
                3 Days
              </button>
              <button 
                className={`days-btn ${forecastDays === 5 ? 'active' : ''}`}
                onClick={() => handleDaysChange(5)}  // 👈 FIX 3: Using handler
              >
                5 Days
              </button>
              <button 
                className={`days-btn ${forecastDays === 7 ? 'active' : ''}`}
                onClick={() => handleDaysChange(7)}  // 👈 FIX 3: Using handler
              >
                7 Days
              </button>
            </div>
          </div>

          <div className="forecast-grid">
            {forecast.map((day, index) => (
              <WeatherCard 
                key={index}
                day={day}
                icon={getWeatherIcon(day.condition)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Farming Tips Section */}
      <div className="farming-tips-section">
        <h3>🌾 Weather-Based Farming Tips</h3>
        <div className="tips-grid">
          <div className="tip-card sunny">
            <div className="tip-icon">☀️</div>
            <h4>Sunny Day</h4>
            <p>Good for harvesting, pesticide application, and drying crops</p>
          </div>
          <div className="tip-card rainy">
            <div className="tip-icon">🌧️</div>
            <h4>Rainy Day</h4>
            <p>Check drainage, avoid walking in fields, watch for fungal diseases</p>
          </div>
          <div className="tip-card cloudy">
            <div className="tip-icon">☁️</div>
            <h4>Cloudy Day</h4>
            <p>Good for transplanting, apply organic mulch, inspect for pests</p>
          </div>
          <div className="tip-card windy">
            <div className="tip-icon">💨</div>
            <h4>Windy Day</h4>
            <p>Avoid spraying pesticides, check for wind damage, secure stakes</p>
          </div>
        </div>
      </div>

      {/* Login Prompt for Non-Logged In Users */}
      {!user && (
        <div className="login-prompt">
          <p>🔒 <Link to="/login">Login</Link> to get personalized daily farming advisories!</p>
        </div>
      )}
    </div>
  );
}

export default WeatherForecast;