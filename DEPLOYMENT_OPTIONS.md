# Deployment Options for Backend

## Issue
Render's free tier (512MB RAM) is insufficient for this application stack:
- FastAPI + Uvicorn: ~50MB
- ChromaDB: ~100MB
- Sentence Transformers model: ~100-150MB
- LangChain + dependencies: ~100MB
- Total: ~400-450MB (exceeds 512MB limit)

## Recommended Solutions

### Option 1: Railway (FREE - Recommended)
**Pros:**
- $5 free credit per month (enough for this app)
- Better memory handling
- No cold starts
- Easy deployment

**Steps:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize and deploy
railway init
railway up

# Set environment variables in Railway dashboard
```

**Environment Variables to Set:**
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION`
- `CHROMA_PERSIST_DIR=./chroma_db`

---

### Option 2: Render Paid Tier ($7/month)
**Pros:**
- 2GB RAM - plenty of headroom
- Current setup works as-is
- Already configured

**Steps:**
1. Go to Render dashboard
2. Upgrade service to "Starter" plan ($7/month)
3. Redeploy

---

### Option 3: Fly.io (FREE with credit card)
**Pros:**
- Free tier with 256MB shared RAM
- Might work with optimizations
- Global edge deployment

**Steps:**
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Launch app
flyctl launch

# Deploy
flyctl deploy
```

---

### Option 4: Azure App Service (FREE F1 tier)
**Pros:**
- 1GB RAM
- Already using Azure OpenAI
- Free tier available

**Cons:**
- More complex setup
- Cold starts

---

## My Recommendation

**For this assignment: Use Railway**
- Free (within $5 credit)
- Easy to set up
- No memory issues
- Professional deployment URL

**For production: Render Paid or Azure App Service**
- More reliable
- Better uptime guarantees
- Scalable

---

## Alternative: Optimize Further

If you must use Render free tier, you could:
1. Remove ChromaDB persistence (loses data on restart)
2. Use even smaller embedding model
3. Reduce chunk size/overlap
4. But this impacts functionality significantly

**Not recommended for this technical assignment.**
