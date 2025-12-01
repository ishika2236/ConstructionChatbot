# 🚀 Deployment Guide

Complete guide to deploy the Construction AI RAG application.

## 📋 Overview

- **Frontend**: Vercel (Free)
- **Backend**: Render (Free tier)
- **Repository**: https://github.com/ishika2236/ConstructionChatbot

---

## 🔧 Backend Deployment (Render)

### Step 1: Sign up for Render

1. Go to https://render.com
2. Sign up with your GitHub account
3. Authorize Render to access your repositories

### Step 2: Create New Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `ishika2236/ConstructionChatbot`
3. Configure the service:

   - **Name**: `construction-ai-backend`
   - **Region**: Oregon (US West) or closest to you
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

### Step 3: Add Environment Variables

In Render dashboard, go to **Environment** and add:

```
AZURE_OPENAI_API_KEY=2ab4c3a499e4468b9f363a150c754699
AZURE_OPENAI_ENDPOINT=https://openai-nowx.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview
CHROMA_PERSIST_DIR=./chroma_db
PYTHON_VERSION=3.9.0
```

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes first time)
3. Your backend will be live at: `https://construction-ai-backend.onrender.com`

### Step 5: Ingest Documents

After deployment, run ingestion via API:

```bash
curl -X POST https://your-backend-url.onrender.com/api/ingest
```

**⚠️ Note**: Free tier on Render spins down after 15 minutes of inactivity. First request after idle may take 30-60 seconds.

---

## 🎨 Frontend Deployment (Vercel)

### Step 1: Sign up for Vercel

1. Go to https://vercel.com
2. Sign up with your GitHub account
3. Import your repository

### Step 2: Import Project

1. Click **"Add New..."** → **"Project"**
2. Import `ishika2236/ConstructionChatbot`
3. Configure the project:

   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)

### Step 3: Add Environment Variables

In Vercel dashboard, go to **Settings** → **Environment Variables**:

```
NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
```

Replace `your-backend-url` with your actual Render backend URL.

### Step 4: Deploy

1. Click **"Deploy"**
2. Wait for build (2-3 minutes)
3. Your frontend will be live at: `https://your-project.vercel.app`

### Step 5: Update CORS (Optional)

If you want to restrict CORS to your Vercel domain only:

1. Edit `backend/main.py`
2. Change `allow_origins=["*"]` to `allow_origins=["https://your-project.vercel.app"]`
3. Commit and push changes

---

## ✅ Post-Deployment Checklist

### Backend Health Check
```bash
curl https://your-backend-url.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "vector_store": "initialized",
  "documents_count": 784
}
```

### Frontend Test

1. Open your Vercel URL
2. Login with: `testingcheckuser1234@gmail.com`
3. Ask a question: "What is the fire rating for corridor partitions?"
4. Verify you get a response with sources

---

## 🔍 Troubleshooting

### Backend Issues

**Problem**: "Application failed to respond"
- **Solution**: Check Render logs, ensure all environment variables are set

**Problem**: "DeploymentNotFound" error
- **Solution**: Verify Azure OpenAI deployment name is correct

**Problem**: No documents in vector store
- **Solution**: Run ingestion endpoint after deployment

### Frontend Issues

**Problem**: API calls failing
- **Solution**: Check `NEXT_PUBLIC_API_URL` is set correctly

**Problem**: CORS errors
- **Solution**: Ensure backend allows your Vercel domain in CORS settings

**Problem**: Login not working
- **Solution**: Check email matches `AUTHORIZED_EMAIL` in backend

---

## 💰 Cost Breakdown

| Service | Plan | Cost | Limitations |
|---------|------|------|-------------|
| **Render** | Free | $0 | - 750 hours/month<br>- Spins down after 15 min idle<br>- 512 MB RAM |
| **Vercel** | Hobby | $0 | - 100 GB bandwidth<br>- Unlimited sites<br>- Auto SSL |
| **Azure OpenAI** | Pay-as-you-go | ~$0.03/1K tokens | Usage-based pricing |
| **HuggingFace Embeddings** | Local | $0 | Runs on server (no API calls) |

**Monthly Estimate**: $5-15 depending on Azure OpenAI usage

---

## 🔄 Continuous Deployment

Both Render and Vercel are connected to your GitHub repository:

1. **Push to `main` branch** → Automatic deployment
2. **Backend**: ~5 minutes to redeploy
3. **Frontend**: ~2 minutes to redeploy

---

## 📊 Monitoring

### Render Dashboard
- View logs: https://dashboard.render.com
- Monitor requests, errors, and performance

### Vercel Dashboard
- View deployments: https://vercel.com/dashboard
- Monitor analytics and errors

---

## 🎯 Production Improvements (Optional)

For production use, consider:

1. **Database**: Replace in-memory conversation storage with PostgreSQL
2. **Authentication**: Add proper JWT-based auth
3. **Rate Limiting**: Add rate limiting middleware
4. **Caching**: Implement Redis for response caching
5. **Monitoring**: Add Sentry or similar for error tracking
6. **Paid Plans**: Upgrade to paid Render plan for better performance

---

## 📝 Environment Variables Summary

### Backend (.env)
```bash
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview
CHROMA_PERSIST_DIR=./chroma_db
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
```

---

## 🎉 Success!

Once deployed:
- ✅ Backend API is live and serving requests
- ✅ Frontend is accessible via HTTPS
- ✅ Documents are indexed and searchable
- ✅ Automatic deployments on git push

Your Construction AI RAG application is now live! 🚀
