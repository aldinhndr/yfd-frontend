import uuid

from fastapi import APIRouter, Depends, Form, Request, UploadFile, File, HTTPException
from core.database import get_supabase
from core.security import get_current_user
from core.middleware import get_client_ip
from models.schemas import RegisterResponse

router = APIRouter(prefix="/api/tenis-meja", tags=["Tenis Meja"])

BUCKET_NAME = "bukti-pembayaran"


@router.post("/register", response_model=RegisterResponse)
async def register_tenis_meja(
    request: Request,
    nama: str = Form(...),
    no_hp: str = Form(...),
    gereja_asal: str = Form(...),
    bukti_bayar: UploadFile = File(...),
    user=Depends(get_current_user),
):
    supabase = get_supabase()

    # Validasi tipe file dasar
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if bukti_bayar.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Bukti pembayaran harus berupa gambar (JPG/PNG/WEBP)")

    file_bytes = await bukti_bayar.read()
    ext = bukti_bayar.filename.split(".")[-1] if "." in bukti_bayar.filename else "jpg"
    file_path = f"tenis-meja/{user.id}/{uuid.uuid4()}.{ext}"

    upload_result = supabase.storage.from_(BUCKET_NAME).upload(
        file_path,
        file_bytes,
        {"content-type": bukti_bayar.content_type},
    )

    if getattr(upload_result, "error", None):
        raise HTTPException(status_code=500, detail="Gagal mengunggah bukti pembayaran")

    bukti_bayar_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_path)

    result = supabase.table("tenis_meja_registrations").insert({
        "nama_peserta": nama,
        "no_hp": no_hp,
        "gereja_asal": gereja_asal,
        "bukti_bayar_url": bukti_bayar_url,
        "user_id": user.id,
        "added_by": user.id,
    }).execute()

    new_id = result.data[0]["id"] if result.data else None
    return {"message": "Pendaftaran Tenis Meja berhasil", "id": new_id}