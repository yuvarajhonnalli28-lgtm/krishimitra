import React, { useContext, useState } from "react";
import { AuthContext } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import toast from "react-hot-toast";
import "./Profile.css";

function Profile() {
  const { user, logout } = useContext(AuthContext);
  const { isDarkMode, toggleTheme } = useTheme();
  const [activeTab, setActiveTab] = useState("overview");

  // Mock user data
  const userStats = {
    scansThisMonth: 3,
    totalScans: 27,
    savedCrops: 5,
    memberSince: "January 2025"
  };

  const recentActivity = [
    { id: 1, action: "Disease Scan - Tomato", date: "2 hours ago", result: "Healthy" },
    { id: 2, action: "Weather Check", date: "Yesterday", result: "Rain forecast" },
    { id: 3, action: "Market Price - Wheat", date: "2 days ago", result: "₹2200/quintal" },
  ];

  if (!user) {
    return (
      <div className="profile-container">
        <div className="profile-card">
          <h2>Please Login</h2>
          <p>You need to be logged in to view your profile.</p>
          <a href="/login" className="btn btn-primary">Go to Login</a>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <div className="profile-header">
        <div className="profile-cover"></div>
        <div className="profile-info">
          <div className="profile-avatar">
            {user.name ? user.name[0].toUpperCase() : "👤"}
          </div>
          <div className="profile-details">
            <h1>{user.name || "Farmer"}</h1>
            <p className="profile-email">{user.email || "farmer@example.com"}</p>
            <p className="profile-member">Member since {userStats.memberSince}</p>
          </div>
          <button onClick={logout} className="btn btn-outline logout-btn">
            Logout
          </button>
        </div>
      </div>

      <div className="profile-tabs">
        <button 
          className={`tab-btn ${activeTab === "overview" ? "active" : ""}`}
          onClick={() => setActiveTab("overview")}
        >
          Overview
        </button>
        <button 
          className={`tab-btn ${activeTab === "activity" ? "active" : ""}`}
          onClick={() => setActiveTab("activity")}
        >
          Activity
        </button>
        <button 
          className={`tab-btn ${activeTab === "settings" ? "active" : ""}`}
          onClick={() => setActiveTab("settings")}
        >
          Settings
        </button>
      </div>

      <div className="profile-content">
        {activeTab === "overview" && (
          <div className="overview-tab">
            <div className="stats-grid">
              <div className="stat-card">
                <span className="stat-icon">🔍</span>
                <span className="stat-value">{userStats.scansThisMonth}</span>
                <span className="stat-label">Scans this month</span>
              </div>
              <div className="stat-card">
                <span className="stat-icon">📊</span>
                <span className="stat-value">{userStats.totalScans}</span>
                <span className="stat-label">Total scans</span>
              </div>
              <div className="stat-card">
                <span className="stat-icon">🌾</span>
                <span className="stat-value">{userStats.savedCrops}</span>
                <span className="stat-label">Saved crops</span>
              </div>
            </div>

            <div className="recent-activity">
              <h3>Recent Activity</h3>
              <div className="activity-list">
                {recentActivity.map(activity => (
                  <div key={activity.id} className="activity-item">
                    <div className="activity-icon">📋</div>
                    <div className="activity-details">
                      <h4>{activity.action}</h4>
                      <p>{activity.result}</p>
                    </div>
                    <span className="activity-date">{activity.date}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === "activity" && (
          <div className="activity-tab">
            <h3>Complete Activity History</h3>
            <p>Your full activity log will appear here...</p>
          </div>
        )}

        {activeTab === "settings" && (
          <div className="settings-tab">
            <h3>Settings</h3>
            
            <div className="settings-section">
              <h4>Appearance</h4>
              <div className="setting-item">
                <span>Dark Mode</span>
                <button 
                  onClick={toggleTheme}
                  className="theme-toggle-btn"
                >
                  {isDarkMode ? "☀️ Light" : "🌙 Dark"}
                </button>
              </div>
            </div>

            <div className="settings-section">
              <h4>Notifications</h4>
              <div className="setting-item">
                <span>Email notifications</span>
                <label className="switch">
                  <input type="checkbox" defaultChecked />
                  <span className="slider"></span>
                </label>
              </div>
              <div className="setting-item">
                <span>Market price alerts</span>
                <label className="switch">
                  <input type="checkbox" defaultChecked />
                  <span className="slider"></span>
                </label>
              </div>
            </div>

            <div className="settings-section">
              <h4>Account</h4>
              <button className="btn btn-outline">Change Password</button>
              <button className="btn btn-danger">Delete Account</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Profile;