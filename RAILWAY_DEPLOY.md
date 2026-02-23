# 🚀 Railway Deployment Guide

Deploy GraphRAG Expert Consultant Bot to Railway.app

## ✅ Prerequisites

- Railway account (you have it already ✓)
- GitHub account connected to Railway
- Neo4j Aura account (free) OR Docker on Railway
- Anthropic Claude API key (from https://console.anthropic.com/)
- Telegram bot token

## 🎯 Deployment Steps (5 minutes)

### Step 1: Push code to GitHub

```bash
cd C:\Users\fazyl\Documents\Goszakup_GraphRAG

# Add deployment files
git add Procfile runtime.txt Dockerfile docker-compose.yml .env.railway.example
git commit -m "Add Railway deployment configuration"
git push origin feature/graphrak-core
```

### Step 2: Create Neo4j Instance

#### Option A: Neo4j Aura (Recommended - Easiest)

1. Go to https://neo4j.com/cloud/aura/
2. Click "Create a Free Instance"
3. Sign up / Login
4. Create instance (takes ~2 minutes)
5. Copy these values:
   - **URI**: `neo4j+s://xxxxxxxx.databases.neo4j.io`
   - **Username**: `neo4j`
   - **Password**: (from creation)

#### Option B: Neo4j on Railway (Using Docker)

- Railway will auto-start from docker-compose.yml
- No setup needed!
- URI: `bolt://neo4j:7687`

### Step 3: Create Railway Project

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub"
4. Find and select: `Aldan76/Goszakup_GraphRAG`
5. Select branch: `feature/graphrak-core` (or `main`)

### Step 4: Add Environment Variables

In Railway Dashboard → Variables:

```
TELEGRAM_BOT_TOKEN=8617987568:AAGkDlRS5yQxxfA2ZUrgTbQj-V3uFJGuKmU
ANTHROPIC_API_KEY=sk-ant-your-key-here
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io  (or bolt://neo4j:7687)
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j
ANTHROPIC_LLM_MODEL=claude-3-sonnet-20240229
ANTHROPIC_FALLBACK_MODEL=claude-3-haiku-20240307
EMBEDDINGS_MODEL=sentence-transformers/all-MiniLM-L6-v2
LOG_LEVEL=INFO
TELEGRAM_ADMIN_IDS=your-id-here
```

### Step 5: Deploy

1. Railway auto-detects `Procfile`
2. Installs requirements from `requirements.txt`
3. Starts bot with: `python main.py bot`
4. **Done!** 🎉

### Step 6: Verify Bot Works

In Telegram:
```
/start
# Bot should respond immediately!
```

Check logs in Railway:
- Dashboard → "Logs" tab
- Should see: "🤖 Запуск Telegram бота..."

## 📊 Option Comparison

### Simple Option (Procfile + Neo4j Aura)
```
Pros:
✅ Fast (5 minutes)
✅ Cheap (free tier works)
✅ No Docker knowledge needed
✅ Managed Neo4j

Cons:
❌ Depends on Aura service
```

### Docker Option (docker-compose.yml)
```
Pros:
✅ Everything on Railway
✅ Self-contained
✅ Better for scaling

Cons:
⚠️ Uses more resources
⚠️ Needs Docker knowledge
```

## 🔧 Railway Configuration Files

Created files for deployment:

1. **Procfile** - Tells Railway how to start bot
2. **runtime.txt** - Specifies Python version
3. **Dockerfile** - Container configuration
4. **docker-compose.yml** - Multi-service setup (Neo4j + Bot)
5. **.env.railway.example** - Environment variable template

## 📝 Configuration Details

### Neo4j Aura (Option A)

```env
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=from-aura-dashboard
```

### Neo4j Docker (Option B)

```env
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-strong-password
```

Railway will auto-setup Neo4j from `docker-compose.yml`

## 🚨 Troubleshooting

### Bot not responding

Check logs:
```
Railway Dashboard → Logs → Search for errors
```

Common issues:
```
❌ "TELEGRAM_BOT_TOKEN not set"
   → Add variable to Railway dashboard

❌ "Neo4j connection failed"
   → Check NEO4J_URI format
   → For Aura: neo4j+s://...
   → For Docker: bolt://neo4j:7687

❌ "Claude API error"
   → Check ANTHROPIC_API_KEY is valid
   → Check account has credits
   → Verify API key format (starts with sk-ant-)
```

### Bot keeps restarting

Check in Railway:
- Resources usage (might be out of memory)
- Increase plan if needed
- Check logs for errors

## 💰 Cost Estimate

```
Railway (free plan):
- $5/month included credits (usually free for bot)

Neo4j Aura (free):
- 100k requests/month free

Anthropic Claude (variable):
- ~$0.003-0.015 per user query (depending on model)
- $5-20/month for active bot with Sonnet model
- Cheaper with Haiku model (~$0.8-5/month)
```

## 📈 Monitoring

In Railway Dashboard:

- **Logs** - See bot activity
- **Metrics** - CPU, Memory, Network usage
- **Deployments** - See deployment history
- **Environment** - Manage variables

## 🔄 Updates & Redeployment

To update bot:

```bash
# Make changes locally
git add .
git commit -m "Update bot feature"
git push origin feature/graphrak-core

# Railway auto-redeploys!
# Check Deployments tab to see progress
```

## 🎓 Advanced Options

### Custom Domain
- Railway → Settings → Domains
- Point your custom domain

### Database Backups
- Use Neo4j Aura backups
- Or set up periodic exports

### Scaling
- Railway → Plan → Upgrade to Premium
- Auto-scaling enabled

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Neo4j instance created (Aura or Docker)
- [ ] Railway project connected
- [ ] All environment variables added
- [ ] Deployment started (check Logs)
- [ ] Bot responds in Telegram
- [ ] Logs show no errors

## 📞 Support

If issues:

1. Check Railway logs
2. Verify environment variables
3. Test locally: `python main.py bot`
4. Check Neo4j connectivity
5. Verify OpenAI API key

---

**Bot is now running 24/7 on Railway!** 🚀
