# Directory Structure

reunexx-backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   ├── config.py           # Environment variables & settings
│   │   ├── security.py         # JWT parsing and crypto utilities
│   │   └── database.py         # Supabase client initialization
│   ├── api/
│   │   ├── deps.py             # Dependency injection (Auth & Tenant gating)
│   │   └── v1/
│   │       ├── router.py       # Main v1 API router
│   │       └── endpoints/
│   │           ├── auth.py     # Login, Register, Me
│   │           └── tenant.py   # Workspace management
│   ├── schemas/                # Pydantic models for request/response validation
│   └── services/               # Business logic (e.g., Auth wrappers)
├── requirements.txt
└── .env