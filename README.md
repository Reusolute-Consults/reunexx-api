# Reunexx.ai Core API

Welcome to the backend repository for **Reunexx.ai**, a multi-tenant Agentic AI-as-a-Service platform. This backend powers the visual workflow canvas, manages the multi-agent state execution (via LangGraph), handles vector-based RAG operations, and strictly enforces multi-tenant data isolation.

## 🛠 Tech Stack

* **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
* **Database & Auth:** [Supabase](https://supabase.com/) (PostgreSQL, GoTrue, pgvector, Storage)
* **Data Validation:** [Pydantic v2](https://docs.pydantic.dev/)
* **Server:** [Uvicorn](https://www.uvicorn.org/)

## 📂 Project Structure

This project follows a modular, domain-driven architecture to ensure scalability as we add more AI agents and tool integrations.

``` bash
reunexx-backend/
├── app/
│   ├── main.py                 # FastAPI application entry point & CORS
│   ├── core/
│   │   ├── config.py           # Environment variables (Pydantic Settings)
│   │   └── database.py         # Supabase connection pools (Standard & Admin)
│   ├── api/
│   │   ├── deps.py             # Security Gatekeeper (JWT & Tenant Validation)
│   │   └── v1/
│   │       ├── router.py       # Main API router registry
│   │       └── endpoints/
│   │           ├── auth.py     # Registration, Login, User Profile
│   │           └── health.py   # System status checks
│   ├── schemas/                # Pydantic models for strict payload validation
│   └── services/               # Core business logic and background tasks
├── requirements.txt            # Strictly pinned dependencies
└── .env                        # Local environment variables (Ignored in git)
```

🔐 Security Architecture: The Gatekeeper
Security is non-negotiable. Reunexx.ai operates on a strict Multi-Tenant model.

Every protected API route utilizes the get_current_user_and_tenant dependency found in app/api/deps.py. To access a protected endpoint, the frontend client must pass two headers:

Authorization: Bearer <jwt_token> (Validates identity)

x-tenant-id: <uuid> (Validates workspace context)

The backend intercepts these headers, verifies the user belongs to the requested tenant, and securely adopts the user's identity on the Supabase client to enforce PostgreSQL Row-Level Security (RLS) at the database engine layer.

💻 Local Development Setup
1. Prerequisites
Python 3.10+

A local or cloud Supabase project instance.

2. Environment Variables
Create a .env file in the root directory and populate it with your Supabase credentials:

``` bash
Code snippet
PROJECT_NAME="Reunexx Core API"
VERSION="1.0.0"

# Supabase Credentials
SUPABASE_URL="[https://your-project-id.supabase.co](https://your-project-id.supabase.co)"
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI..."
SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI..."
(Warning: Never expose the SUPABASE_SERVICE_ROLE_KEY to the frontend. It is used exclusively on the backend to bypass RLS during system-level operations like tenant creation).
```

3. Installation
We highly recommend using a virtual environment to avoid dependency conflicts.

``` bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
4. Running the Server
Start the Uvicorn server with hot-reloading enabled:

uvicorn app.main:app --reload --port 8000
Once running, you can access the Interactive API Documentation (Swagger UI) at:
👉 http://127.0.0.1:8000/v1/docs
```

📡 API Endpoints (v1)
System
GET /v1/health/ - Returns the operational status of the core engine.

Authentication
POST /v1/auth/register - Creates a new user in Supabase Auth, provisions a new Tenant Workspace, and binds the user as the 'Owner'.

POST /v1/auth/login - Authenticates user credentials and returns the JWT and associated tenant_id.

GET /v1/auth/me - (Protected) Validates the active session and returns the hydrated user profile.

Current Development Phase: Sprint 2 (The Secure Knowledge Engine & RAG Implementation)