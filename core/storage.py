import uuid
from fastapi import UploadFile, HTTPException
from core.database import get_supabase

BUCKET = "yfd-uploads"
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
MAX_SIZE_MB = 5


async def upload_file(file: UploadFile, folder: str) -> str:
    """Upload 1 file ke Supabase Storage, return public URL-nya."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"Tipe file tidak didukung: {file.content_type}")

    content = await file.read()
    if len(content) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(400, f"File maksimal {MAX_SIZE_MB}MB")

    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    path = f"{folder}/{uuid.uuid4()}.{ext}"

    supabase = get_supabase()
    supabase.storage.from_(BUCKET).upload(
        path, content, {"content-type": file.content_type}
    )
    return supabase.storage.from_(BUCKET).get_public_url(path)
