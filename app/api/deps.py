from fastapi import Depends, HTTPException, status, Header, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.database import get_supabase_client
from supabase import Client
from typing import Annotated

security = HTTPBearer()

async def get_current_user_and_tenant(
    credentials: Annotated[HTTPAuthorizationCredentials, Security(security)],
    x_tenant_id: Annotated[str, Header(description="The active workspace ID")],
    supabase: Client = Depends(get_supabase_client)
) -> dict:
    """
    Validates the Supabase JWT and strictly enforces that the user 
    has access to the requested x_tenant_id.
    """
    token = credentials.credentials
    
    # 1. Validate the JWT with Supabase
    try:
        # We set the session on the supabase client to adopt the user's identity
        # This is CRITICAL for PostgreSQL Row-Level Security (RLS) to work downstream.
        supabase.auth.set_session(access_token=token, refresh_token="")
        user_response = supabase.auth.get_user()
        user = user_response.user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Validate Tenant Access
    # Check if this user actually belongs to the x_tenant_id they are trying to query
    try:
        tenant_check = supabase.table("users").select("role").eq("id", user.id).eq("tenant_id", x_tenant_id).execute()
        
        if not tenant_check.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this workspace."
            )
            
        user_role = tenant_check.data[0]["role"]
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    # Return the validated context to the endpoint
    return {
        "user_id": user.id,
        "email": user.email,
        "tenant_id": x_tenant_id,
        "role": user_role
    }