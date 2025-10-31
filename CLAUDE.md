# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Polaris Finance Backend is a FastAPI-based financial forecasting platform integrated with Supabase (PostgreSQL + Auth). It provides REST APIs for managing financial forecasts, user authentication, and data analysis for stocks/sectors.

## Development Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template and configure
cp .env.example .env
# Edit .env with your Supabase credentials

# Run development server
uvicorn app.main:app --reload

# Alternative with specific host/port
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Docker Development
```bash
# Build image
docker build -t polaris-be .

# Run container
docker run -p 8000:8000 --env-file .env polaris-be

# Or use docker-compose (when configured)
docker-compose up --build
```

### Database Operations
```bash
# Generate migration (when alembic is properly configured)
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Downgrade migration
alembic downgrade -1
```

## Architecture Overview

### Core Components
- **FastAPI Application**: Main API server (`app/main.py`)
- **Database Layer**: Async SQLAlchemy with PostgreSQL via Supabase
- **Authentication**: Supabase JWT verification using JWKS endpoint
- **API Versioning**: All endpoints under `/api/v1/`

### Key Directories
- `app/api/v1/*/`: API endpoint routers (currently only forecasts implemented)
- `app/core/`: Configuration, security, and dependencies
- `app/db/`: Database models and session management
- `app/schemas/`: Pydantic models for request/response validation
- `alembic/`: Database migrations (not yet initialized)

### Database Models (app/db/models.py)
- **ShareMaster**: Stock information with sector relationships
- **ModelRegistry**: ML model metadata and versioning
- **Forecast**: Financial predictions with model results and confidence scores

### Authentication Flow
1. Client authenticates with Supabase Auth
2. Receives JWT token
3. FastAPI verifies JWT using Supabase JWKS endpoint (`app/core/security.py`)
4. Protected endpoints use `get_current_user` dependency

### Current API Endpoints
- `POST /api/v1/forecasts/upsert` - Create/update single forecast
- `POST /api/v1/forecasts/bulk_upsert` - Batch forecast updates (for ML jobs)
- `GET /api/v1/forecasts/latest` - Get latest forecasts by symbol
- `GET /api/v1/forecasts/` - Search forecasts with filters
- `GET /health` - Health check endpoint

## Environment Configuration

Required environment variables (see `.env.example`):
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_ANON_KEY`: Public API key
- `SUPABASE_JWKS_URL`: JWT verification endpoint
- `DATABASE_URL`: PostgreSQL connection string with SSL required
- `APP_ENV`: dev/prod
- `LOG_LEVEL`: Logging level

## Development Status

✅ **Completed**:
- FastAPI project structure with versioned APIs
- Forecast CRUD operations with authentication
- Supabase integration for auth and database
- Docker configuration
- Database models for core entities

🚧 **In Progress/Planned**:
- Authentication router implementation
- Additional endpoints: news, sectors, shares, users
- Alembic migrations setup
- Test suite implementation
- API documentation enhancement

## Important Notes

- **No Test Framework**: Currently no pytest configuration or tests exist
- **Alembic Not Configured**: Migration system present but not initialized
- **Empty Config Files**: `pyproject.toml` and `docker-compose.yml` are empty
- **Turkish Comments**: Code contains Turkish language comments
- **Supabase-First**: Heavy integration with Supabase for auth and database services
- **SSL Required**: Database connection must use `sslmode=require`
- **Async Patterns**: Uses async/await throughout with SQLAlchemy 2.0

## ML Integration

The system supports batch forecasting results from ML models (RF, LGBM, XGB, LSTM) through the `/bulk_upsert` endpoint. The forecasts table links to model_registry for versioning and tracking model performance.