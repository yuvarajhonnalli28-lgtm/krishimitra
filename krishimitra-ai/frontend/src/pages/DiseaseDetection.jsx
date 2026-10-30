// Disease detection page
import React, { useState, useRef } from "react";
import toast from "react-hot-toast";
import "./DiseaseDetection.css";

function DiseaseDetection() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [cropType, setCropType] = useState("");
  const fileInputRef = useRef(null);

  const supportedCrops = ["Tomato", "Potato", "Rice", "Wheat", "Corn"];

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith("image/")) {
      toast.error("Please upload a valid image file");
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error("Image size should be less than 5MB");
      return;
    }

    setImage(file);
    setPreview(URL.createObjectURL(file));
    setResult(null); // Clear previous results
  };

  const handleDetect = () => {
    if (!image) {
      toast.error("Please upload a leaf image");
      return;
    }

    setLoading(true);

    // Simulate API call
    setTimeout(() => {
      // Temporary AI result (frontend demo)
      const fakeResult = {
        disease: "Leaf Blight",
        scientific_name: "Phytophthora infestans",
        confidence: "92",
        severity: "Moderate",
        treatment: {
          chemical: "Spray copper fungicide (Mancozeb) once every 7 days",
          organic: "Apply neem oil spray or garlic extract",
          prevention: "Ensure proper air circulation, avoid overhead watering"
        },
        symptoms: [
          "Dark lesions on leaves",
          "Yellowing around spots",
          "White fungal growth in humid conditions"
        ]
      };

      setResult(fakeResult);
      setLoading(false);
      toast.success("✅ Disease analysis completed!");
    }, 2000);
  };

  const handleReset = () => {
    setImage(null);
    setPreview(null);
    setResult(null);
    setCropType("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) {
      setImage(file);
      setPreview(URL.createObjectURL(file));
    } else {
      toast.error("Please drop a valid image file");
    }
  };

  // Get confidence color
  const getConfidenceColor = (confidence) => {
    const num = parseInt(confidence);
    if (num >= 85) return "#4caf50";
    if (num >= 70) return "#ff9800";
    return "#f44336";
  };

  return (
    <div className="disease-page">

      {/* Header */}
      <div className="disease-header">
        <h1>🌿 Crop Disease Detection</h1>
        <p>Upload a photo of your crop leaf to instantly detect diseases</p>
      </div>

      {/* Main Container */}
      <div className="disease-container">
        
        {/* Left Column - Upload Section */}
        <div className="upload-card">
          <h2>📸 Upload Leaf Image</h2>

          {/* Upload Area */}
          <div
            className={`upload-area ${preview ? 'has-image' : ''}`}
            onClick={() => fileInputRef.current?.click()}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            {preview ? (
              <img src={preview} alt="Preview" className="image-preview" />
            ) : (
              <div className="upload-placeholder">
                <span className="upload-icon">📤</span>
                <p>Click to upload or drag & drop</p>
                <p className="upload-hint">PNG, JPG up to 5MB</p>
              </div>
            )}
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleImageChange}
              accept="image/*"
              className="file-input"
            />
          </div>

          {/* Crop Type Selector */}
          <div className="crop-selector">
            <label htmlFor="cropType">Select Crop (Optional)</label>
            <select
              id="cropType"
              value={cropType}
              onChange={(e) => setCropType(e.target.value)}
              className="crop-select"
              disabled={loading}
            >
              <option value="">-- Select crop for better accuracy --</option>
              {supportedCrops.map(crop => (
                <option key={crop} value={crop}>{crop}</option>
              ))}
            </select>
          </div>

          {/* Action Buttons */}
          <div className="action-buttons">
            <button
              onClick={handleDetect}
              className="btn btn-primary detect-btn"
              disabled={!image || loading}
            >
              {loading ? (
                <>
                  <span className="spinner-small"></span>
                  Analyzing...
                </>
              ) : (
                "🔍 Detect Disease"
              )}
            </button>

            {preview && (
              <button
                onClick={handleReset}
                className="btn btn-outline reset-btn"
                disabled={loading}
              >
                🔄 Reset
              </button>
            )}
          </div>

          {/* Tips */}
          <div className="upload-tips">
            <h4>📋 Tips for best results:</h4>
            <ul>
              <li>Take photo in good lighting</li>
              <li>Focus on affected area</li>
              <li>Include healthy part for comparison</li>
              <li>Avoid blurry or dark images</li>
            </ul>
          </div>
        </div>

        {/* Right Column - Results Section */}
        <div className="results-card">
          {loading && (
            <div className="loading-container">
              <div className="spinner"></div>
              <p>AI is analyzing your image...</p>
              <p className="loading-sub">This may take a few seconds</p>
            </div>
          )}

          {!loading && !result && (
            <div className="empty-state">
              <div className="empty-icon">🌱</div>
              <h3>No analysis yet</h3>
              <p>Upload a leaf image to detect diseases</p>
            </div>
          )}

          {!loading && result && (
            <div className="result-card">
              <div className="result-header">
                <h3>🔍 Analysis Result</h3>
              </div>

              {/* Disease Name */}
              <div className="disease-name">
                <h2>{result.disease}</h2>
                <p className="scientific-name">{result.scientific_name}</p>
              </div>

              {/* Confidence Meter */}
              <div className="confidence-meter">
                <div className="confidence-label">
                  <span>Confidence</span>
                  <span style={{ color: getConfidenceColor(result.confidence) }}>
                    {result.confidence}%
                  </span>
                </div>
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${result.confidence}%`,
                      backgroundColor: getConfidenceColor(result.confidence)
                    }}
                  ></div>
                </div>
              </div>

              {/* Severity */}
              <div className="severity-badge">
                <span className="severity-label">Severity:</span>
                <span className={`severity-value ${result.severity.toLowerCase()}`}>
                  {result.severity}
                </span>
              </div>

              {/* Symptoms */}
              <div className="symptoms-section">
                <h4>⚠️ Common Symptoms</h4>
                <ul className="symptoms-list">
                  {result.symptoms.map((symptom, index) => (
                    <li key={index}>{symptom}</li>
                  ))}
                </ul>
              </div>

              {/* Treatment */}
              <div className="treatment-section">
                <h4>💊 Treatment Recommendations</h4>
                
                <div className="treatment-item chemical">
                  <span className="treatment-icon">🧪</span>
                  <div>
                    <strong>Chemical:</strong>
                    <p>{result.treatment.chemical}</p>
                  </div>
                </div>

                <div className="treatment-item organic">
                  <span className="treatment-icon">🌱</span>
                  <div>
                    <strong>Organic:</strong>
                    <p>{result.treatment.organic}</p>
                  </div>
                </div>

                <div className="treatment-item prevention">
                  <span className="treatment-icon">🛡️</span>
                  <div>
                    <strong>Prevention:</strong>
                    <p>{result.treatment.prevention}</p>
                  </div>
                </div>
              </div>

              {/* Disclaimer */}
              <div className="disclaimer">
                <p>⚠️ AI-powered analysis. Consult local expert for confirmation.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default DiseaseDetection;