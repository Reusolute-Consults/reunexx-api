from supabase import create_client, Client
from app.core.config import settings

# 1. Standard Client (ANON KEY)
# We use this for 99% of requests. In our deps.py, we attach the user's JWT to this client
# so that PostgreSQL Row-Level Security (RLS) is strictly enforced.
supabase_client: Client = create_client(
    supabase_url=settings.SUPABASE_URL, 
    supabase_key=settings.SUPABASE_ANON_KEY
)

# 2. Admin Client (SERVICE ROLE KEY)
# This bypasses RLS completely. It should ONLY be used for backend system operations, 
# such as creating the initial Tenant Workspace during user registration.
supabase_admin: Client = create_client(
    supabase_url=settings.SUPABASE_URL, 
    supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY
)

def get_supabase_client() -> Client:
    """
    Dependency to inject the standard Supabase client into FastAPI routes.
    """
    return supabase_client

def get_supabase_admin() -> Client:
    """
    Dependency to inject the Supabase Admin client. Use with extreme caution.
    """
    return supabase_admin