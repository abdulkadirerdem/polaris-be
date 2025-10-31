# Polaris Finance — Backend & Supabase Architecture (Progress Overview)

## 📘 Project Summary
Polaris Finance is a **FastAPI-based backend** integrated with **Supabase (PostgreSQL + Auth)** for a financial data analysis and forecasting platform.

The goal is to build a backend that handles:
- **User authentication (Supabase Auth)**
- **Financial entities** (shares, sectors, indicators, forecasts, news, etc.)
- **ML-driven forecasts** (RF, LGBM, XGB, LSTM)
- **Risk and sector metrics**
- **Automated batch updates (via n8n)**

---

## 🧱 System Overview

### Core Components
| Component | Technology | Purpose |
|------------|-------------|----------|
| Backend | FastAPI + SQLAlchemy | Main API layer |
| Database | Supabase (PostgreSQL) | Persistent data & RLS policies |
| Auth | Supabase Auth | Email/Google/Apple login |
| Automations | n8n | Scheduled data refresh & ML task orchestration |
| Models | RF, LGBM, XGB, LSTM | Technical & directional forecasting |
| Hosting | Ubuntu 4GB / 2vCPU | App deployment + Dockerized services |

---

## 📊 Supabase Schema

### ✅ Core Tables
| Table | Description |
|--------|--------------|
| **users** | Stores user info (auth type, subscription, favorites, etc.) |
| **shares_master** | Static list of available stocks |
| **share_prices** | Daily open/high/low/close data per stock |
| **minute_scores** | Intraday data points (timestamped) |
| **sectors_master** | All sectors with GICS codes and mapping |
| **sector_metrics_daily** | Daily sector-level change and averages |
| **indicators_master** | Registered technical indicators |
| **daily_indicators** | Daily calculated indicator results per stock |
| **model_registry** | Registered ML models (name, version, type) |
| **forecasts** | ML-generated predictions with model linkage |
| **news** | News data with related shares, sectors, people |
| **risk_metrics** | Daily/periodic risk ratios (Sharpe, Sortino, etc.) |
| **financial_statements** | Balance Sheet, IS, CF data + AI commentary |

---

## 🔗 Table Relationships

- `forecasts.model_id → model_registry.id`
- `forecasts.share_id → shares_master.id`
- `share_prices.share_id → shares_master.id`
- `daily_indicators.share_id → shares_master.id`
- `risk_metrics.share_id → shares_master.id`
- `financial_statements.share_id → shares_master.id`
- `sectors_master.id → shares_master.sector_id`

---

## 📈 Forecasts Table (Key Logic)

| Field | Description |
|--------|-------------|
| `forecast_date` | When the prediction was made |
| `target_date` | Prediction’s target day |
| `model_id` | FK to model_registry |
| `model_name` / `version` | ML model metadata |
| `used_indicators` | List of indicators used |
| `prediction` | Probability/score |
| `direction` | up / down / neutral |
| `confidence` | Model confidence |
| `sl_target` / `tp_target` | Stop-loss / take-profit suggestions |

This table supports **UPSERTs** via `(share_id, model_id, range_days, target_date)`.

---

## ⚙️ Backend Architecture

```
app/
├── api/
│   └── v1/
│       └── forecasts/
│           ├── router.py
│           └── repo.py
├── core/
│   ├── config.py
│   └── security.py
├── db/
│   ├── base.py
│   └── models.py
├── schemas/
│   └── forecast.py
└── main.py
```

---

## 🧠 Authentication
- Managed by Supabase Auth.
- FastAPI verifies JWT using Supabase **JWKS endpoint**.
- Local endpoints use `Depends(get_current_user)` for protection.

---

## 🔐 Security
- Supabase RLS enabled for all user data.
- Public read for stocks/sectors/news.
- Backend-only write access for forecasts/risk_metrics.

---

## 📦 FastAPI Highlights

### `POST /api/v1/forecasts/upsert`
Upserts a forecast for a given stock & model combination.

### `POST /api/v1/forecasts/bulk_upsert`
Batch insert/update for ML jobs (n8n / model scripts).

### `GET /api/v1/forecasts/latest`
Fetch latest forecast by symbol (optionally range_days).

### `GET /api/v1/forecasts`
Query forecasts by date or range.

---

## 🤖 Machine Learning Integration Plan

Current stage: **batch forecasting + DB storage.**
- Forecasts are calculated offline (RF, LGBM, XGB, LSTM).
- Results are pushed to `/api/v1/forecasts/bulk_upsert`.
- Supabase holds long-term model results.

Later phase: **hybrid online inference**.
- Real-time predictions can be added via `/predict` endpoints.
- Existing schema supports incremental transition.

---

## 🧮 Risk & Financial Extensions

### `risk_metrics`
Stores ratios like:
- Sharpe
- Sortino
- Calmar
- Max Drawdown
- Confidence Score

### `financial_statements`
Stores JSON-based BS/IS/CF + AI commentary.

---

## 🧩 Model Registry
Centralized model metadata.

| Column | Example |
|---------|----------|
| model_name | 'lgbm' |
| version | 'v1.3' |
| type | 'directional' |
| description | 'Predicts 30–180d price movement' |

Used for versioning and linking to `forecasts`.

---

## 🧭 Current Status (as of Oct 2025)
✅ Supabase schema created  
✅ Forecasts table + model_registry linked  
✅ Risk metrics & financials added  
✅ FastAPI backend (JWT-secured) operational  
✅ Forecast CRUD API completed  
🚧 Next: integrate shares, sectors, news routers

---

## 🧩 Summary
We’ve built a modular, scalable backend that cleanly separates:
- **Data ingestion (Supabase)**  
- **Prediction layer (ML)**  
- **Automation (n8n)**  
- **Presentation (Frontend)**  

The system supports both **daily batch analytics** and future **real-time ML inference** — keeping all financial metrics, forecasts, and risks synchronized in Supabase.

