# 💰 BudgetPro - Personal Budget Tracker

A full-stack personal finance management application built with React, FastAPI, and Supabase.

![Budget Tracker](https://img.shields.io/badge/Status-Production-green) ![React](https://img.shields.io/badge/React-18-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green) ![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-purple)

## ✨ Features

- 🔐 **Secure Authentication** - Email/password auth with Supabase
- 📊 **Dashboard Analytics** - Visual spending breakdown with charts
- 💸 **Expense Tracking** - Add, edit, delete expenses by category
- 🎯 **Budget Management** - Set monthly budgets per category
- 🚨 **Smart Alerts** - Warnings when approaching/exceeding budgets
- 📱 **Responsive Design** - Works on desktop and mobile
- 🌙 **Dark Mode** - Premium dark theme UI

## 🏗️ Tech Stack

### Frontend
- React 18 with Vite
- Tailwind CSS v4
- React Router v6
- Recharts for data visualization
- Lucide React icons

### Backend
- FastAPI (Python)
- Supabase Client
- Pydantic for validation
- JWT Authentication

### Database
- Supabase (PostgreSQL)
- Row Level Security enabled
- Real-time capable

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Supabase account

### 1. Set up Supabase

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to SQL Editor and run the schema from `database/schema.sql`
3. Copy your project URL and anon key from Settings > API

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Supabase credentials

# Run development server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your Supabase and API URLs

# Run development server
npm run dev
```

### 4. Access the App

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📁 Project Structure

```
budget-tracker-full/
├── frontend/               # React + Vite frontend
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── contexts/      # React contexts (Auth)
│   │   ├── hooks/         # Custom hooks
│   │   ├── lib/           # Utilities and API client
│   │   └── pages/         # Page components
│   └── ...
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── routes/       # API route handlers
│   │   ├── models.py     # Pydantic models
│   │   ├── auth.py       # Authentication logic
│   │   └── main.py       # App entry point
│   └── ...
└── database/             # SQL schemas
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Sign in
- `POST /api/auth/logout` - Sign out
- `GET /api/auth/me` - Get current user

### Expenses
- `GET /api/expenses/` - List expenses (with filters)
- `POST /api/expenses/` - Create expense
- `PATCH /api/expenses/{id}` - Update expense
- `DELETE /api/expenses/{id}` - Delete expense

### Budgets
- `GET /api/budgets/` - List budgets
- `POST /api/budgets/` - Create/update budget
- `PATCH /api/budgets/{id}` - Update budget amount
- `DELETE /api/budgets/{id}` - Delete budget

### Dashboard
- `GET /api/dashboard/` - Get dashboard data
- `GET /api/dashboard/alerts` - Get budget alerts

## 🚢 Deployment

### Frontend (Vercel)

```bash
cd frontend
npm run build
# Deploy dist folder to Vercel
```

### Backend (Render)

1. Create a new Web Service on Render
2. Connect your GitHub repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `.env.example`

## 🔒 Environment Variables

### Frontend (.env)
```
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
VITE_API_URL=http://localhost:8000
```

### Backend (.env)
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
FRONTEND_URL=http://localhost:5173
```

## 📝 Categories

- 🍔 Food
- 🚗 Transport
- 🎬 Entertainment
- 📄 Bills
- 🛍️ Shopping
- 💊 Health
- 📚 Education
- 📦 Other

## 👩‍💻 Author

**Shreya Srivastava**

---

Made with ❤️ for better financial management
