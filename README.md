# News Summary App - System Architecture Overview

## Overview
News Summary Web App is a **SvelteKit-based** frontend integrated with a **FastAPI backend**, featuring **Firebase authentication**, and a **self-hosted PostgreSQL database**. The infrastructure is designed to be **scalable, efficient, and cloud-agnostic** with **Cloudflare for CDN & hosting**.

---

## 📦 **Components Breakdown**

### **1️⃣ SvelteKit Frontend**
- **Framework:** SvelteKit
- **UI Library:** Tailwind CSS + shadcn/ui
- **State Management:** Svelte Stores (`$store`)
- **Authentication:** Firebase Auth (Google, Email, etc.)
- **Deployment:** Cloudflare Pages (auto-deployed from GitHub)
- **Role:**
  - Provides a **fast, lightweight UI** for users.
  - Embeds **Unity WebGL** for visualization.
  - Handles user authentication via Firebase.
  - Communicates with the FastAPI backend for user-specific data.

---

### **2️⃣ FastAPI Backend (Self-Hosted on VPS)**
- **Framework:** FastAPI (Python)
- **Database Connection:** PostgreSQL (self-hosted)
- **Auth Handling:** Firebase JWT validation
- **Endpoints:**
  - `/api/user` → Fetch user profile from PostgreSQL.
  - `/api/data` → Provide Unity WebGL with necessary data.
  - `/api/settings` → Store user preferences.
- **Deployment:** Self-hosted on **Marcin's second machine** (VPS)
- **Role:**
  - Handles all business logic and API requests.
  - Manages user data and preferences.
  - Interfaces with PostgreSQL for persistent storage.

---

### **3️⃣ PostgreSQL Database (Self-Hosted)**
- **Database:** PostgreSQL (self-hosted)
- **Schema:**
  - `users` → Stores user profiles & settings.
  - `session_data` → Stores session info for Unity WebGL.
- **Role:**
  - Stores **user authentication data** (linked to Firebase UID).
  - Holds **user preferences & visualization settings**.
  - Provides **session data for Unity WebGL**.

---

### **4️⃣ Unity WebGL Visualization**
- **Hosted On:** Cloudflare R2
- **Frontend Access:** Embedded in SvelteKit
- **Role:**
  - Loads and runs **3D visualization** for COBEY.
  - Fetches necessary session data from the **FastAPI backend**.

---

### **5️⃣ Cloudflare Services**
- **Cloudflare Pages:** Hosts **SvelteKit frontend**.
- **Cloudflare R2:** Stores and serves **Unity WebGL assets**.
- **Cloudflare CDN:** Speeds up content delivery globally.
- **Cloudflare DNS & SSL:** Ensures secure access.

---

## 🔄 **How Components Interact**
1. **User accesses the app via Cloudflare Pages**.
2. **SvelteKit handles UI & authentication** (Firebase Auth).
3. **Authenticated requests go to FastAPI backend** (JWT-verified).
4. **FastAPI retrieves/stores data in PostgreSQL**.
5. **Unity WebGL fetches session data via FastAPI**.
6. **Unity assets (WebGL) load from Cloudflare R2**.

---

## 🚀 **Deployment Plan**
### **Frontend (SvelteKit)**
- Hosted on **Cloudflare Pages**.
- Auto-deployed from **GitHub**.

### **Backend (FastAPI)**
- Runs on **self-hosted VPS (Marcin’s second machine)**.
- Exposed via **reverse proxy (Nginx or Caddy recommended).**

### **Database (PostgreSQL)**
- Runs on the **same VPS** for now.
- May migrate to **cloud-managed PostgreSQL** if needed.

### **Unity WebGL Hosting**
- Uploaded to **Cloudflare R2**.
- Served with **Cloudflare CDN**.

---

## 🛠️ **Future Improvements**
- **Containerization**: Deploy FastAPI in a **Docker container** for better portability.
- **Database Migration**: Move PostgreSQL to a **managed cloud service** if needed.
- **Backend Scaling**: Consider moving to a **Linode/DigitalOcean VPS** for more compute power.

---

## 🤖 **Development Setup**
### **1. Clone the repository**
```sh
git clone https://github.com/your-repo/cobey-webapp.git
cd cobey-webapp
```

### **2. Install dependencies**
```sh
npm install  # For frontend
pip install -r requirements.txt  # For FastAPI backend
```
### **3. Start Development**
```sh
npm run dev  # Start SvelteKit frontend
uvicorn main:app --reload  # Start FastAPI backend
```

### **4. Database Setup**
Install PostgreSQL and create a database:

```sh
psql -U postgres
CREATE DATABASE cobey_db;
```
Run migrations (if using Alembic):

```sh
alembic upgrade head
```

📜 License
MIT License © 2025 COBEY

---

### **Summary**
- ✅ **SvelteKit (Cloudflare Pages) for frontend**
- ✅ **FastAPI (Self-hosted VPS) for backend**
- ✅ **PostgreSQL (Self-hosted) for data**
- ✅ **Firebase for authentication**
- ✅ **Cloudflare R2 + CDN for Unity WebGL storage**
- ✅ **Cloudflare Workers (optional for future edge computing needs)**
