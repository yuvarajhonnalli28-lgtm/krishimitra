<h1 align="center">🌾 Agricultural Advisory Assistant for Farmers</h1>
# 🌾 KrishiMitra AI - Smart Farming Assistant

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-blue.svg)](https://reactjs.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.16-orange.svg)](https://tensorflow.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Kaggle](https://img.shields.io/badge/Kaggle-Dataset-20beff.svg)](https://www.kaggle.com/datasets/emmarex/plantdisease)

> **KrishiMitra AI** (Hindi: Farmer's Friend) — An intelligent farming companion for Indian farmers

**Crop Disease Detection · Weather Forecasting · Market Prices · Smart Farming Advice**

---

## 📌 **Live Demo**

| Component | URL |
|-----------|-----|
| **Frontend** | https://kashinathbiradar123.github.io/krishimitra-ai/ |
| **Backend API** | https://krishimitra-ai-backend.onrender.com/docs |
| **GitHub** | https://github.com/KashinathBiradar123/krishimitra-ai |
| **Website** | https://krishimitra-ai-beta.vercel.app |

---

## 🧠 **About the Project**

**KrishiMitra AI** is an end-to-end AI platform built to empower Indian farmers with modern technology. Farmers can:

- 📸 **Upload a photo** of a diseased crop leaf → Get instant AI diagnosis
- 🌦️ **Check live weather** → Plan sowing, irrigation, and harvesting
- 💰 **View mandi prices** → Find the best market rates
- 🤖 **Ask farming questions** → Receive actionable advice

Built with the goal of **bridging the technology gap for rural and semi-urban farmers across India**.

---

## ✨ **Features**

| Feature | Description | Status |
|---------|-------------|--------|
| 🔬 **Crop Disease Detection** | Upload leaf image → MobileNetV2 model identifies disease (87% accuracy) | ✅ Complete |
| 🌦️ **Weather Forecasting** | 7-day location-based weather with farming advice | ✅ Complete |
| 📈 **Market (Mandi) Prices** | Live commodity prices with best price highlighting 👑 | ✅ Complete |
| 🤖 **AI Farming Advice** | Intelligent chatbot for crop, pest, fertilizer questions | ✅ Complete |
| 🌓 **Dark/Light Mode** | User-friendly theme toggle for day/night usage | ✅ Complete |
| 📱 **Mobile Responsive** | Works on all devices (phone, tablet, desktop) | ✅ Complete |

---

## 🏗️ **Project Structure**
<img width="700" height="730" alt="image" src="https://github.com/user-attachments/assets/9013418a-cb77-46e8-80d9-26d20192d18a" />
<img width="640" height="890" alt="image" src="https://github.com/user-attachments/assets/6bb6ab41-130b-43a2-9b38-85eb13ab4eb1" />
<img width="817" height="399" alt="image" src="https://github.com/user-attachments/assets/4da04e75-ca7e-4a69-812e-bc126e063fee" />

---

## 🤖 **Model Details**

| Parameter | Value |
|-----------|-------|
| **Architecture** | MobileNetV2 (Transfer Learning) |
| **Task** | Multi-class image classification (crop leaf diseases) |
| **Dataset** | PlantVillage Dataset (20,638 images, 15 classes) |
| **Framework** | TensorFlow 2.16 / Keras |
| **Input Size** | 224 x 224 pixels |
| **Output** | Disease name + Confidence score + Treatment |
| **Accuracy** | **87.14%** on validation set |
| **Model Size** | 13.4 MB |
| **Inference Time** | <2 seconds on CPU |

### **Supported Crops & Diseases**

| Crop | Diseases Detected |
|------|-------------------|
| **Tomato** | Bacterial spot, Early blight, Late blight, Leaf Mold, Septoria leaf spot, Spider mites, Target Spot, Yellow Leaf Curl Virus, Mosaic virus, Healthy |
| **Potato** | Early blight, Late blight, Healthy |
| **Pepper** | Bacterial spot, Healthy |

---

## 🛠️ **Tech Stack**

### **Backend**

| Tool | Purpose |
|------|---------|
| **Python 3.12** | Main programming language |
| **FastAPI** | High-performance web framework |
| **TensorFlow/Keras** | ML model training & inference |
| **MobileNetV2** | Pre-trained CNN architecture |
| **OpenCV / PIL** | Image preprocessing |
| **Uvicorn** | ASGI server |
| **JWT** | Authentication |
| **bcrypt** | Password hashing |

### **Frontend**

| Tool | Purpose |
|------|---------|
| **React 18** | UI framework |
| **Vite** | Build tool (fast development) |
| **React Router** | Navigation |
| **Context API** | State management (dark mode, auth) |
| **CSS3** | Custom styling with dark/light themes |
| **Axios** | HTTP requests |

### **External APIs**

| API | Purpose |
|-----|---------|
| **OpenWeatherMap** | Weather forecasts |
| **Kaggle** | PlantVillage dataset |
| **Google Drive** | Pre-trained model hosting |

---

## 🚀 **Getting Started**

### **Prerequisites**

- Python 3.12+
- Node.js 18+
- npm or yarn
- Git

### **Installation**

#### **1. Clone the repository**
```bash
git clone https://github.com/KashinathBiradar123/krishimitra-ai.git
cd krishimitra-ai
### 2. Set up the backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 3. Download the dataset
```bash
python download_dataset_mendeley.py
```

### 4. Open the frontend

Open `frontend/index.html` in your browser, or serve it locally:
```bash
cd frontend
npx serve .
```
## 📓 Notebooks

The `notebooks/` folder contains:
- **EDA** — Exploratory Data Analysis of crop disease image data
- **Model Training** — MobileNetV2 fine-tuning pipeline
- **Evaluation** — Accuracy, Confusion Matrix, per-class metrics

---

## 🌱 Roadmap

- [ ] Multilingual support (Hindi, Marathi, Kannada)
- [ ] Mobile app (React Native / Flutter)
- [ ] Offline inference for low-connectivity rural areas
- [ ] Government scheme recommendations (PM-Kisan, crop insurance)
- [ ] Soil health input integration

---

## 🙋 Author

**Kashinath Biradar**  
[GitHub](https://github.com/KashinathBiradar123) · Made with for Indian farmers

---



