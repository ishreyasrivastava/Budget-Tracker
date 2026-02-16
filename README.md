# 💰 Budget Tracker — AI-Powered Personal Finance Manager

![Backend CI](https://github.com/ishreyasrivastava/Budget-Tracker/actions/workflows/backend-ci.yml/badge.svg)

A full-stack personal finance management app with **AI-powered expense prediction**, **anomaly detection**, and **smart spending insights**. Built with React + FastAPI + Supabase.

## ✨ Features

### Core
- 📊 **Expense Tracking** — Full CRUD with category-based organization
- 💰 **Budget Management** — Set monthly budgets per category with real-time tracking
- 📈 **Dashboard** — Visual spending breakdown, trends, and budget alerts
- 🔐 **Authentication** — Secure JWT-based auth via Supabase

### 🤖 AI-Powered Analytics
- 🔮 **Expense Prediction** — Forecasts next month's spending using Weighted Moving Average + Linear Trend analysis
- 🚨 **Anomaly Detection** — Flags unusual expenses using Z-score and IQR statistical methods
- 💡 **Smart Insights** — Category dominance warnings, budget utilization alerts, spending pattern analysis

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, Vite, Tailwind CSS |
| **Backend** | FastAPI (Python), Pydantic validation |
| **Database** | PostgreSQL via Supabase |
| **Auth** | Supabase Auth (JWT) |
| **AI/ML** | Custom statistical engine (WMA, Linear Regression, Z-score, IQR) |
| **CI/CD** | GitHub Actions |
| **Deployment** | Vercel (frontend) + Render (backend) |

## 📁 Project Structure

```
Budget-Tracker/
├── frontend/                  # React SPA
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── contexts/          # Auth context provider
│   │   ├── pages/             # Dashboard, Expenses, Budgets, Login
│   │   └── lib/               # Supabase client, API helpers, constants
│   └── package.json
├── backend/                   # FastAPI server
│   ├── app/
│   │   ├── ai/                # AI/ML modules
│   │   │   ├── predictor.py   # Expense prediction engine
│   │   │   └── anomaly.py     # Anomaly detection & insights
│   │   ├── routes/
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── expenses.py    # Expense CRUD
│   │   │   ├── budgets.py     # Budget management
│   │   │   ├── dashboard.py   # Analytics dashboard
│   │   │   └── ai.py          # AI prediction & anomaly routes
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── models.py          # Pydantic schemas
│   │   ├── database.py        # Supabase client
│   │   ├── auth.py            # JWT auth middleware
│   │   └── config.py          # Environment configuration
│   ├── tests/
│   │   ├── test_predictor.py  # Prediction engine tests
│   │   └── test_anomaly.py    # Anomaly detection tests
│   └── requirements.txt
├── database/
│   └── schema.sql             # PostgreSQL schema with RLS policies
└── .github/
    └── workflows/
        └── backend-ci.yml     # CI pipeline
```

## 🤖 AI Engine — How It Works

### Expense Prediction
Uses a **hybrid approach** combining:
1. **Weighted Moving Average (WMA)** — Recent months weighted higher for short-term accuracy
2. **Linear Trend Analysis** — Detects long-term spending trajectory

Confidence levels based on available data:
- **High** (6+ months) → Reliable forecasts
- **Medium** (3-5 months) → Reasonable estimates
- **Low** (1-2 months) → Rough projections

### Anomaly Detection
Two complementary methods:
1. **Z-Score** — Flags expenses >2σ from category mean (configurable threshold)
2. **IQR (Interquartile Range)** — More robust against extreme outliers, uses Q1/Q3 fences

### Smart Insights
Analyzes patterns to generate actionable recommendations:
- Category dominance warnings (>40% in one category)
- Budget utilization alerts (approaching/exceeding limits)
- Spending frequency analysis
- Trend-based predictions

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Supabase account

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your Supabase credentials to .env
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env
# Add your Supabase & API credentials to .env
npm run dev
```

### Database Setup
Run `database/schema.sql` in your Supabase SQL Editor.

### Run Tests
```bash
cd backend
pip install pytest
python -m pytest tests/ -v
```

## 📡 API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register new user |
| POST | `/api/auth/signin` | Login |
| GET | `/api/auth/me` | Get current user |

### Expenses
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/expenses/` | Create expense |
| GET | `/api/expenses/` | List expenses (with filters) |
| GET | `/api/expenses/{id}` | Get expense |
| PATCH | `/api/expenses/{id}` | Update expense |
| DELETE | `/api/expenses/{id}` | Delete expense |

### Budgets
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/budgets/` | Create/update budget |
| GET | `/api/budgets/` | List budgets |
| GET | `/api/budgets/{id}` | Get budget |
| PATCH | `/api/budgets/{id}` | Update budget |
| DELETE | `/api/budgets/{id}` | Delete budget |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/` | Get dashboard summary |
| GET | `/api/dashboard/alerts` | Get budget alerts |

### 🤖 AI Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/ai/predict` | Predict next month's spending |
| GET | `/api/ai/anomalies` | Detect spending anomalies |
| GET | `/api/ai/insights` | Get smart spending insights |

## 👩‍💻 Author

**Shreya Srivastava** — [GitHub](https://github.com/ishreyasrivastava)

---

*Built with discipline. Powered by data. 💰🤖*
