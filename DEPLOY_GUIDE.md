# 🚀 Medipredict AI — Railway Deployment Guide

## Step 1 — GitHub Par Upload Karo

```bash
git init
git add .
git commit -m "Initial production deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/medipredict-ai.git
git push -u origin main
```

> ⚠️ **Important:** `.env` file kabhi push mat karna — `.gitignore` mein already hai.

---

## Step 2 — Railway Account + Project

1. **railway.app** par jao → Sign Up (GitHub se login karo)
2. **"New Project"** click karo
3. **"Deploy from GitHub repo"** select karo
4. Apna `medipredict-ai` repo select karo
5. Railway automatically `Procfile` detect karega aur deploy start karega

---

## Step 3 — PostgreSQL Database Add Karo

1. Railway project mein **"+ New"** click karo
2. **"Database" → "PostgreSQL"** select karo
3. Database create hone ke baad, **Variables** tab mein jao
4. `DATABASE_URL` automatically set ho jaata hai ✅

---

## Step 4 — Environment Variables Set Karo

Railway project → **Variables** tab mein yeh sab add karo:

| Variable | Value |
|---|---|
| `SECRET_KEY` | `your-random-secret-key-min-32-chars` |
| `FLASK_ENV` | `production` |
| `ADMIN_EMAIL` | `admin@youremail.com` |
| `ADMIN_PASSWORD` | `YourSecureAdminPass@123` |
| `MAIL_USERNAME` | `yourgmail@gmail.com` |
| `MAIL_PASSWORD` | `gmail-app-password` *(see below)* |
| `MAIL_DEFAULT_SENDER` | `Medipredict AI <yourgmail@gmail.com>` |

### Gmail App Password Kaise Banaye:
1. Google Account → Security → 2-Step Verification ON karo
2. Security → **App passwords** → "Mail" + "Other (Custom)" → Generate
3. 16-char password milega — woh `MAIL_PASSWORD` mein daalo

---

## Step 5 — Domain

Railway deploy ke baad:
- **Free domain:** `yourapp.up.railway.app`
- **Custom domain:** Settings → Domains → Add Custom Domain → DNS mein CNAME add karo

---

## Step 6 — Admin Login

Deploy hone ke baad:
```
URL: https://yourapp.up.railway.app/admin
Username: admin
Password: (jo ADMIN_PASSWORD set kiya)
```

---

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# .env file create karo
cp .env.example .env
# Edit .env with your values

# Run locally
python app.py
# Opens at http://localhost:5000
```

---

## Project Structure

```
medipredict-ai/
├── app.py              # Main Flask app (routes, models, PDF, email)
├── config.py           # Production/Dev config
├── wsgi.py             # Gunicorn entry point
├── Procfile            # Railway/Heroku start command
├── railway.json        # Railway config
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── model/              # ML model .sav files
├── static/
│   ├── style.css       # Animated UI styles
│   └── script.js       # Particles, animations, interactions
└── templates/
    ├── index.html      # Main page
    ├── dashboard.html  # Health history + charts
    ├── admin.html      # Admin panel
    ├── login.html
    └── signup.html
```

---

## Features

| Feature | Status |
|---|---|
| User Auth (Login/Signup) | ✅ |
| 5 Disease Predictions | ✅ |
| Health History Dashboard | ✅ |
| PDF Report Download | ✅ |
| Email Notifications | ✅ |
| Admin Panel | ✅ |
| PostgreSQL Database | ✅ |
| Animated UI + Particles | ✅ |
| Railway Deployment Ready | ✅ |

