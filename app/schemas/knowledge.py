from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class DocumentResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    filename: str
    file_type: str
    status: str
    created_at: Optional[datetime] = None

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]