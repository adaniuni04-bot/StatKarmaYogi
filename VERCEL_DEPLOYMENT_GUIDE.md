# StatKarmaYogi Platform - Vercel Deployment & GitHub Guide

This guide explains how to deploy your platform to **Vercel** with the correct settings so that **both the Next.js frontend and FastAPI backend run live together**.

---

## 🛠️ Summary of Fixes Applied

1. **Fixed "No Output Directory named 'public' found"**:
   - Created the missing `public/` directory with `robots.txt` and `index.html` in both `frontend/public` and root.
   - Added `vercel.json` locking `"framework": "nextjs"`.
   - **Crucial Setting**: In Vercel's Build & Development Settings, the **Output Directory override toggle must be turned OFF** so Vercel uses Next.js default output (`.next`).
2. **Fixed "Command 'uv pip install' exited with 1"**:
   - Pinned Python version to `3.12` in `.python-version` so Vercel does not use experimental Python 3.14.
   - Removed obsolete build blockers (`psycopg[binary]==3.1.19`, `pgvector`, and `pytest`) from `requirements.txt`.
3. **Security Vulnerability Patched (`next@14.2.15` -> `^14.2.35`)**:
   - Upgraded `next` in `frontend/package.json` to `^14.2.35` (the official security-patched release).
4. **Lightweight Folder Size (2.55 MB)**:
   - Cleaned all temporary build files (`node_modules` and `.next`) so it uploads to GitHub in seconds without hitting the 100 MB limit.

---

## 🎯 What to Choose in Vercel (Exact Settings)

When importing your project into Vercel or checking **Project Settings**:

### 1. General Settings
| Setting | Exact Value to Choose | Notes |
| :--- | :--- | :--- |
| **Framework Preset** | **`Next.js`** | **Must be `Next.js`** (not "Other"). |
| **Root Directory** | **`frontend`** | Click **"Edit"**, choose or type **`frontend`**, and save. |

### 2. Build and Output Settings (IMPORTANT)
Under the **Build and Output Settings** section, check the three toggle switches:

| Setting | Toggle Position | Why |
| :--- | :--- | :--- |
| **Build Command** | **OFF** (Disabled / Gray) | Vercel uses `next build` automatically. |
| **Output Directory** | **OFF** (Disabled / Gray) | **Must be OFF!** If this toggle is ON with `public`, Vercel fails to find `.next`. Turning it OFF lets Vercel auto-detect Next.js output! |
| **Install Command** | **OFF** (Disabled / Gray) | Vercel uses `npm install` automatically. |

---

## 📋 Step-by-Step Deployment Instructions

### Step 1: Upload to GitHub
1. Upload the files from `C:\Users\sjtha\OneDrive\Desktop\StatKarmaYogi-Platform\stat-skill-platform` to your GitHub repo.
2. Commit your changes.

---

### Step 2: Configure & Deploy on Vercel
1. Go to [vercel.com](https://vercel.com) -> Select your project -> Go to **Settings** -> **General**.
   *(Or if importing new: Click **"Add New..."** -> **"Project"**)*
2. Verify:
   - **Framework Preset**: **`Next.js`**
   - **Root Directory**: **`frontend`**
   - **Output Directory toggle**: **OFF** (Gray / Not overridden).
3. In **Environment Variables**, ensure you have:
   - `GROQ_API_KEY`: Your Groq Cloud Qwen API key (`gsk_...`)
   - `DEMO_MODE`: `false`
   - `ENVIRONMENT`: `production`
4. Click **"Deploy"** (or **"Redeploy"** under Deployments)!

---

### Step 3: Verify Your Live Website
1. Click your live URL (e.g. `https://stat-skill-platform-xxx.vercel.app`).
2. Log in with demo credentials:
   - **Email**: `employee@example.com`
   - **Password**: `employee123`
3. Click **"Re-evaluate with Grok Qwen AI"** to verify real-time AI scoring and role readiness.
