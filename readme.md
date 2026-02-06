# SafeRoute AI 🚦

**Live Demo:** https://saferoute-production-8593.up.railway.app  
**Repository:** https://github.com/Charan-57/saferoute

SafeRoute AI is an intelligent web application that recommends the **safest travel routes** by combining maps, machine learning, and community-reported crime data.

Unlike traditional navigation apps that optimize only distance or time, SafeRoute AI **prioritizes personal safety** — especially for women, students, night-shift workers, and solo travelers.

---

## 🚨 Problem Statement

Most navigation systems (e.g., Google Maps) provide the fastest or shortest route but ignore safety factors such as:

- Crime-prone areas  
- Night travel risk  
- Real-world incidents  

People traveling in unfamiliar or high-risk areas lack tools that help them choose safer paths.

---

## ✅ Solution

SafeRoute AI provides:

- Safety-based route recommendations  
- Crime heatmaps along travel paths  
- Community crime reporting & comments  
- AI-powered risk scoring of route segments  
- Visual indicators for safe (green) and unsafe (red) areas  

---

## 🧠 AI Workflow

1. User enters source and destination  
2. Locations are geocoded using OpenStreetMap (Nominatim)  
3. Multiple routes are fetched using OSRM  
4. Routes are divided into segments  
5. A lightweight Machine Learning model predicts crime probability per segment using:
   - Crime density
   - Time of day  
6. Routes are ranked by safety score  
7. Safer routes are shown in green, unsafe alternatives in red  
8. Crime heatmaps and community reports are overlaid on the map  

---

## 🛠 Tech Stack

### Frontend
- HTML, CSS, JavaScript  
- Leaflet.js (maps)

### Backend
- FastAPI (Python)

### Machine Learning
- Scikit-learn (Logistic Regression)

### Maps & Routing
- OpenStreetMap  
- OSRM  
- Nominatim

### Deployment
- Railway (cloud hosting)

### Storage (MVP)
- JSON files for reports and comments

---

## 🌟 Features

- Safe route recommendation
- Crime density heatmap
- Community crime reporting
- Visual unsafe zone marking
- Lightweight AI risk prediction
- Fully deployed live application

---

## 🌍 Live Demo

👉 https://saferoute-production-8593.up.railway.app

---

## 🚀 How to Run Locally

```bash
git clone https://github.com/Charan-57/saferoute
cd saferoute
pip install -r requirements.txt
uvicorn main:app --reload
