// frontend/src/components/WeatherCard.jsx
import React from 'react';
import './WeatherCard.css';

const WeatherCard = ({ day, icon }) => {
  return (
    <div className="weather-card">
      <div className="weather-card-date">
        {new Date(day.date).toLocaleDateString('en-IN', { 
          weekday: 'short', 
          day: 'numeric', 
          month: 'short' 
        })}
      </div>
      
      <div className="weather-card-icon">
        {icon}
      </div>
      
      <div className="weather-card-temp">
        <span className="max-temp">{day.max_temp}°</span>
        <span className="min-temp">{day.min_temp}°</span>
      </div>
      
      <div className="weather-card-condition">
        {day.condition}
      </div>
      
      <div className="weather-card-details">
        <div className="weather-card-detail">
          <span>💧</span> {day.humidity}%
        </div>
        <div className="weather-card-detail">
          <span>🌧️</span> {day.rain_chance}%
        </div>
      </div>
      
      {day.advice && (
        <div className="weather-card-advice">
          {day.advice}
        </div>
      )}
    </div>
  );
};

export default WeatherCard;