from fastapi import Depends, HTTPException, status, UploadFile
from .auth import get_current_user
from .models import User
MAX_UPLOAD_MB = 10
async def require_user(user: User = Depends(get_current_user)) -> User: return user
async def validate_image(file: UploadFile) -> UploadFile:
    ct = file.content_type or ""
    if not ct.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Only image/* files are allowed")
    return file
