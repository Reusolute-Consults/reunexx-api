from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.core.database import get_supabase_client, get_supabase_admin
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, AuthResponse, UserProfileResponse
from app.api.deps import get_current_user_and_tenant

router = APIRouter()

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserRegisterRequest, 
    supabase: Client = Depends(get_supabase_client)
):
    """
    Registers a new company workspace and its founding user (Owner).
    """
    try:
        # 1. Create the User in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": payload.email,
            "password": payload.password
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Registration failed.")
            
        user_id = auth_response.user.id

        # 2. Create the Tenant Workspace using the Admin Client (Bypasses RLS)
        admin_client = get_supabase_admin()
        
        tenant_res = admin_client.table("tenants").insert({
            "name": payload.company_name,
            "subscription_tier": "Free"
        }).execute()
        
        tenant_id = tenant_res.data[0]["id"]

        # 3. Bind the User to the Tenant as 'Owner'
        admin_client.table("users").insert({
            "id": user_id,
            "tenant_id": tenant_id,
            "email": payload.email,
            "role": "Owner"
        }).execute()

        return AuthResponse(
            access_token=auth_response.session.access_token,
            user_id=user_id,
            tenant_id=tenant_id,
            role="Owner"
        )

    except Exception as e:
        # Gracefully return a 400 error string if something fails
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=AuthResponse)
async def login_user(
    payload: UserLoginRequest, 
    supabase: Client = Depends(get_supabase_client)
):
    """
    Authenticates a user and returns their JWT and bound tenant context.
    """
    try:
        # 1. Authenticate via Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": payload.email,
            "password": payload.password
        })

        if not auth_response.session:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_id = auth_response.user.id

        # 2. Fetch the user's workspace context (Tenant ID & Role)
        # Using admin_client to avoid RLS block during login fetch
        admin_client = get_supabase_admin()
        user_data = admin_client.table("users").select("tenant_id, role").eq("id", user_id).single().execute()

        return AuthResponse(
            access_token=auth_response.session.access_token,
            user_id=user_id,
            tenant_id=user_data.data["tenant_id"],
            role=user_data.data["role"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect email or password."
        )


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_context: dict = Depends(get_current_user_and_tenant),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Validates the active session and returns the hydrated user profile.
    This route is protected by our deps.py Gatekeeper!
    """
    # Fetch subscription tier from the tenants table using the validated tenant_id
    tenant_data = supabase.table("tenants").select("subscription_tier").eq("id", current_context["tenant_id"]).single().execute()

    return UserProfileResponse(
        id=current_context["user_id"],
        email=current_context["email"],
        tenant_id=current_context["tenant_id"],
        role=current_context["role"],
        subscription_tier=tenant_data.data["subscription_tier"]
    )