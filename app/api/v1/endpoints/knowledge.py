from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from supabase import Client
from app.core.database import get_supabase_client
from app.schemas.knowledge import DocumentResponse, DocumentListResponse
from app.api.deps import get_current_user_and_tenant
import uuid

router = APIRouter()

BUCKET_NAME = "reunexx-documents"

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_context: dict = Depends(get_current_user_and_tenant),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Uploads a business document to supabase Storage and logs it in the datase.
    Strictly isolated by tenant_id.
    """

    tenant_id = current_context["tenant_id"]

    # 1. Validate file type (MVP supports pdf, text, markdown)
    allowed_extensions = ["pdf", "txt", "md", "docx"]
    file_ext = file.filename.solit(".")[-1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    try:
        # 2. Read the file bytes
        file_byts = await file.read()

        # Create a unique file path: {tenant_id}/{uuid()}.{ext} to prevent overwriting
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        storage_path = f"{tenant_id}/{unique_filename}"

        # 3. Upload to Supabase Storage
        # Having passed the JWT via our deps.py, RLS ensures this tenant can only upload to their own folder path
        supabase.storage.from_(BUCKET_NAME).upload(
            file=file_bytes,
            path=storage_path,
            file_options={"content-type": file.content_type}
        )

        # 4. Insert metadata into the Postgres 'knowledge_documents' table
        db_res = supabase.table("knowledge_documents").insert({
            "tenant_id": tenant_id,
            "filename": file.filename,
            "file_type": file_ext,
            "status": "uploaded", # Status will change to 'processing' when Celery picks itup later
            "storage_path": storage_path
        }).execute()

        document_record = db_res.data[0]

        return DocumentResponse(**document_record)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        await file.close()


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    current_context: dict = Depends(get_current_user_and_tenant),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Returns a list of all uploaded documents for the active tenant.
    """
    try:
        tenant_id = current_context["tenant_id"]
        
        # Postgres RLS automatically filters this, but we explicitly query by tenant_id as best practice
        res = supabase.table("knowledge_documents").select("*").eq("tenant_id", tenant_id).execute()
        
        return DocumentListResponse(documents=res.data)
        
    except Exception as e:
        # This except block MUST align with the 'try' block above it!
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))