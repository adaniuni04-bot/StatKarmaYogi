# StatKarmaYogi Platform - Vercel Deployment & GitHub Guide

This guide explains how to deploy your platform to **Vercel** with pure Python FastAPI backend support so that **both the Next.js frontend and Python FastAPI backend run together with zero errors and real dynamic persistence**.

---

## 🛠️ Summary of Fixes Applied

1. **Shifted Backend Exclusively to Python FastAPI**:
   - Removed all mock TypeScript route handlers (`frontend/app/api/[[...slug]]/route.ts`).
   - All 107+ routes (authentication, live AI evaluations, skill gaps, personalized learning paths, assessments, and AI tutor) are handled exclusively by Python FastAPI.
2. **Fixed Serverless Statelessness / "Rahul Sharma" Hardcoded Bug**:
   - In serverless environments (like Vercel), separate function calls execute in stateless, isolated containers.
   - Updated `backend/app/core/security.py` and `backend/app/api/deps.py` so that upon registration or login, the user's complete profile and dynamic AI skill evaluation are cryptographically encoded inside the signed JWT access token.
   - Whenever any serverless container cold-starts, it automatically recovers and reconstructs the user's profile and dynamic gap analysis. Your dashboard will **always display your real registered name, target role, and dynamic AI skill gaps**!
3. **Unified Next.js + Python Structure**:
   - Configured `package.json`, `next.config.js`, `api/index.py`, and `requirements.txt` at the root.
   - Vercel auto-detects **Next.js** for the frontend and **@vercel/python** for the FastAPI backend.
4. **Lightweight Folder Size (~2.8 MB)**:
   - Cleaned all temporary build files (`node_modules` and `.next`) so it pushes to GitHub in seconds without hitting the 100 MB limit.

---

## 🎯 What to Choose in Vercel (Exact Settings)

When importing your project into Vercel or checking **Project Settings**:

### 1. General Settings
| Setting | Exact Value to Choose | Notes |
| :--- | :--- | :--- |
| **Framework Preset** | **`Next.js`** | **Must be `Next.js`** *(Do NOT select "FastAPI" or "Other").* |
| **Root Directory** | **`./`** (Leave blank / default root) | Do NOT select `frontend` or `backend`. Leave it at the repository root! |

### 2. Build and Output Settings (IMPORTANT)
Leave all toggles **OFF** (use Vercel defaults):
| Setting | Toggle Position | Why |
| :--- | :--- | :--- |
| **Build Command** | **OFF** (Disabled / Gray) | Vercel uses `next build` automatically. |
| **Output Directory** | **OFF** (Disabled / Gray) | Vercel automatically finds `.next`. |
| **Install Command** | **OFF** (Disabled / Gray) | Vercel uses `npm install` automatically. |

### 3. Environment Variables
In your Vercel Project -> **Settings** -> **Environment Variables**, add:
- `GROQ_API_KEY`: Your free Groq API key from https://console.groq.com/keys (e.g. `gsk_...`)
- `JWT_SECRET`: `stat_karma_yogi_production_secret_key_2026` (or any 32+ character string)
- `ENVIRONMENT`: `production`

---

## 📋 Step-by-Step Deployment Instructions

### Step 1: Push / Upload to GitHub
1. Commit and push the latest repository to your GitHub repo (`git add .`, `git commit -m "Pure Python FastAPI backend with Next.js"`, `git push origin main`).
2. Alternatively, use GitHub Desktop or upload files from `C:\Users\sjtha\OneDrive\Desktop\StatKarmaYogi-Platform\stat-skill-platform` or extract `StatKarmaYogi-Platform.zip`.

---

### Step 2: Configure & Deploy on Vercel
1. Go to [vercel.com](https://vercel.com) -> Select your project -> Go to **Settings** -> **General**.
   *(Or if importing new: Click **"Add New..."** -> **"Project"** -> Select your repository).*
2. Verify:
   - **Framework Preset**: **`Next.js`**
   - **Root Directory**: **`./`** (default root)
   - **Output Directory toggle**: **OFF** (Gray / Not overridden).
3. Under **Environment Variables**, verify `GROQ_API_KEY` and `JWT_SECRET`.
4. Click **"Deploy"** (or click **"Redeploy"** under the Deployments tab)!

---

### Step 3: Verify Your Live Website
1. Open your live URL (e.g. `https://your-project.vercel.app`).
2. Register a new user with any custom role (e.g., *Penetration Tester*, *AI Engineer*, *Cloud Solutions Architect*), select your skills, and click **Create Profile & Launch Evaluation**.
3. You will be directed to `/dashboard`:
   - Your real registered name and role will display in the banner.
   - The AI will evaluate your exact declared skills against canonical industry benchmarks.
   - 100% powered by pure Python FastAPI in the background!
