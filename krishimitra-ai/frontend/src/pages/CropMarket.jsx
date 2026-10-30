// Crop market page
import React, { useState, useEffect } from "react";
import toast from "react-hot-toast";
import "./CropMarket.css";

const API_BASE_URL = "http://localhost:8000/api";

function CropMarket() {
  const [markets, setMarkets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchInput, setSearchInput] = useState(""); // For input field
  const [searchTerm, setSearchTerm] = useState(""); // For actual filtering
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [categories, setCategories] = useState(["All"]);
  const [sortBy, setSortBy] = useState("crop");
  const [marketSummary, setMarketSummary] = useState(null);

  useEffect(() => {
    fetchMarketPrices();
  }, []);

  const fetchMarketPrices = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/market/`);
      
      if (!response.ok) {
        throw new Error("Failed to fetch market prices");
      }

      const data = await response.json();
      
      setMarkets(data.prices || []);
      setMarketSummary(data.summary || null);
      
      // Extract unique categories safely
      const uniqueCategories = ["All", 
        ...new Set(data.prices?.map(item => item.category).filter(Boolean) || [])
      ];
      setCategories(uniqueCategories);

      toast.success("Market data loaded successfully!");

    } catch (error) {
      toast.error("Unable to load market prices");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // Handle search
  const handleSearch = () => {
    setSearchTerm(searchInput);
    if (searchInput.trim()) {
      toast.success(`Searching for "${searchInput}"...`);
    }
  };

  // Handle key press (Enter)
  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  // Clear search
  const clearSearch = () => {
    setSearchInput("");
    setSearchTerm("");
    toast.success("Search cleared");
  };

  // Safe filtering with null checks
  const filteredMarkets = markets
    .filter((item) => {
      const matchesSearch = (item.crop || "")
        .toLowerCase()
        .includes((searchTerm || "").toLowerCase());
      
      const matchesCategory = selectedCategory === "All" || 
        (item.category || "General") === selectedCategory;
      
      return matchesSearch && matchesCategory;
    })
    .sort((a, b) => {
      if (sortBy === "price") {
        return (b.price || 0) - (a.price || 0);
      }
      if (sortBy === "change") {
        return Math.abs(b.change || 0) - Math.abs(a.change || 0);
      }
      return (a.crop || "").localeCompare(b.crop || "");
    });

  // Calculate max price for highlighting
  const maxPrice = Math.max(...filteredMarkets.map(m => m.price || 0), 0);

  // Format price in Indian Rupees
  const formatPrice = (price) => {
    if (!price && price !== 0) return "N/A";
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(price);
  };

  // Get trend icon
  const getTrendIcon = (change) => {
    if (!change) return "➡️";
    if (change > 0) return "📈";
    if (change < 0) return "📉";
    return "➡️";
  };

  // Get trend class
  const getTrendClass = (change) => {
    if (!change) return "";
    if (change > 0) return "positive";
    if (change < 0) return "negative";
    return "";
  };

  // Generate stable unique key
  const getUniqueKey = (item, index) => {
    const cropPart = (item.crop || 'unknown').replace(/\s+/g, '-').toLowerCase();
    const marketPart = (item.market || 'unknown').replace(/\s+/g, '-').toLowerCase();
    return `${cropPart}-${marketPart}-${index}`;
  };

  if (loading) {
    return (
      <div className="market-loading">
        <div className="spinner"></div>
        <p>Fetching live mandi prices from across India...</p>
        <div className="loading-skeleton">
          {[1,2,3,4,5].map(i => (
            <div key={`skeleton-${i}`} className="skeleton-row"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="market-page">

      {/* Header Section */}
      <div className="market-header">
        <h1>💰 Crop Market Prices</h1>
        <p>Live mandi prices to help farmers sell at the best rate</p>
      </div>

      {/* Market Summary Cards */}
      {marketSummary && (
        <div className="market-summary">
          <div className="summary-card">
            <span className="summary-label">Average Price</span>
            <span className="summary-value">{formatPrice(marketSummary.average_price)}</span>
          </div>
          <div className="summary-card">
            <span className="summary-label">Highest Price</span>
            <span className="summary-value">{formatPrice(marketSummary.highest_price)}</span>
          </div>
          <div className="summary-card">
            <span className="summary-label">Lowest Price</span>
            <span className="summary-value">{formatPrice(marketSummary.lowest_price)}</span>
          </div>
          <div className="summary-card">
            <span className="summary-label">Total Crops</span>
            <span className="summary-value">{markets.length}</span>
          </div>
        </div>
      )}

      {/* Search and Filter Bar */}
      <div className="market-controls">
        <div className="market-search-group">
          <div className="market-search">
            <input
              type="text"
              placeholder="🔍 Search crop (e.g., Wheat, Tomato, Rice)"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onKeyPress={handleKeyPress}
              className="search-input"
            />
            <button 
              onClick={handleSearch} 
              className="btn btn-primary search-btn"
            >
              Search
            </button>
            {searchTerm && (
              <button 
                onClick={clearSearch} 
                className="btn btn-outline clear-btn"
                title="Clear search"
              >
                ✕
              </button>
            )}
          </div>
          {searchTerm && (
            <div className="search-active">
              Showing results for: <strong>"{searchTerm}"</strong>
            </div>
          )}
        </div>

        <div className="market-filters">
          <select 
            value={selectedCategory} 
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="filter-select"
          >
            {categories.map(cat => (
              <option key={`cat-${cat}`} value={cat}>{cat}</option>
            ))}
          </select>

          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
            className="filter-select"
          >
            <option value="crop">Sort by Crop Name</option>
            <option value="price">Sort by Price (High to Low)</option>
            <option value="change">Sort by Price Change</option>
          </select>

          <button onClick={fetchMarketPrices} className="btn btn-outline refresh-btn" title="Refresh prices">
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Results Count */}
      <div className="results-count">
        Found <strong>{filteredMarkets.length}</strong> crop{filteredMarkets.length !== 1 ? 's' : ''}
        {searchTerm && <span> matching "<strong>{searchTerm}</strong>"</span>}
        {selectedCategory !== "All" && <span> in category <strong>{selectedCategory}</strong></span>}
      </div>

      {/* Market Table */}
      <div className="market-table-container">
        <table className="market-table">
          <thead>
            <tr>
              <th>Crop</th>
              <th>Category</th>
              <th>Mandi</th>
              <th>State</th>
              <th>Price (per quintal)</th>
              <th>Change</th>
              <th>Trend</th>
            </tr>
          </thead>

          <tbody>
            {filteredMarkets.length > 0 ? (
              filteredMarkets.map((item, index) => {
                const isBestPrice = item.price === maxPrice && maxPrice > 0;
                
                return (
                  <tr 
                    key={getUniqueKey(item, index)}
                    className={`
                      ${item.trend === 'up' ? 'price-up' : item.trend === 'down' ? 'price-down' : ''}
                      ${isBestPrice ? 'best-price-row' : ''}
                    `}
                  >
                    <td>
                      <strong>{item.crop || "Unknown"}</strong>
                      {isBestPrice && <span className="best-price-badge" title="Best price today">👑</span>}
                    </td>
                    <td>{item.category || "General"}</td>
                    <td>{item.market || "N/A"}</td>
                    <td>{item.state || "N/A"}</td>
                    <td className={`price-column ${isBestPrice ? 'best-price' : ''}`}>
                      {formatPrice(item.price)}
                      {isBestPrice && <small className="best-price-label"> Best</small>}
                    </td>
                    <td className={`change-column ${getTrendClass(item.change)}`}>
                      {item.change > 0 ? '+' : ''}{item.change || 0}%
                    </td>
                    <td className="trend-column">
                      {getTrendIcon(item.change)} {item.trend || 'stable'}
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan="7" className="no-data-message">
                  <div className="no-data-content">
                    <span className="no-data-icon">🔍</span>
                    <p>No crops found matching your criteria</p>
                    <button onClick={clearSearch} className="btn btn-primary btn-small">
                      Clear Search
                    </button>
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Best Price Advice - Only show when there are results */}
      {filteredMarkets.length > 0 && (
        <div className="price-advice">
          <div className="advice-banner">
            <span className="advice-icon">💡</span>
            <p>
              <strong>Pro Tip:</strong> The <span className="highlight">👑 crown icon</span> shows the highest price today. 
              Consider selling at these mandis for maximum profit!
            </p>
          </div>
        </div>
      )}

      {/* Market News Section - Only show when there are results */}
      {filteredMarkets.length > 0 && (
        <div className="market-news">
          <h3>📰 Market News & Tips</h3>
          <div className="news-grid">
            {filteredMarkets.slice(0, 3).map((item, index) => {
              const newsText = item.news || 
                `${item.crop || 'Crop'} prices are ${item.trend || 'stable'} in ${item.market || 'major mandis'}. ${
                  item.change > 0 ? 'Prices are rising!' : 
                  item.change < 0 ? 'Prices have dropped.' : 
                  'Market is stable.'
                }`;
              
              return (
                <div key={`news-${index}`} className="news-card">
                  <h4>{item.crop || "Market Update"}</h4>
                  <p>{newsText}</p>
                  <span className="news-time">Updated just now</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Farming Advice - Always show */}
      <div className="farming-advice">
        <h3>🌾 Selling Advice for Better Profits</h3>
        <div className="advice-cards">
          <div className="advice-card">
            <span className="advice-icon">⏰</span>
            <h4>Best Time to Sell</h4>
            <p>Morning hours (8-11 AM) usually get better prices. Avoid selling during peak afternoon heat.</p>
          </div>
          <div className="advice-card">
            <span className="advice-icon">📦</span>
            <h4>Quality Grading</h4>
            <p>Clean, sorted produce gets 10-15% higher price. Remove damaged items before going to mandi.</p>
          </div>
          <div className="advice-card">
            <span className="advice-icon">🏪</span>
            <h4>Compare Multiple Mandis</h4>
            <p>Check prices in 2-3 nearby mandis. Sometimes traveling 20km can get you ₹200-300 more per quintal.</p>
          </div>
          <div className="advice-card">
            <span className="advice-icon">📊</span>
            <h4>Track Price Trends</h4>
            <p>Prices are usually higher on Mondays and Fridays. Avoid selling on holidays when demand is low.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CropMarket;