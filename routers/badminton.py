from typing import Optional

from fastapi import APIRouter, Depends, Form, UploadFile, File, Request, HTTPException
from core.database import get_supabase
from core.storage import upload_file
from core.security import get_current_user
from core.middleware import get_client_ip
from models.schemas import RegisterResponse

router = APIRouter(prefix="/api/badminton", tags=["Badminton"])

KATEGORI_VALID = {"ganda_putra", "ganda_putri", "campuran"}


@router.post("/register", response_model=RegisterResponse)
async def register_badminton(
    request: Request,
    kategori: str = Form(...),
    nama_team: str = Form(...),
    gereja_asal: str = Form(...),
    nama_peserta_1: str = Form(...),
    nama_peserta_2: str = Form(...),
    no_hp: str = Form(...),
    asal_kota: str = Form(...),
    peserta_2_luar_gereja: bool = Form(False),
    surat_gereja: UploadFile = File(...),
    foto_peserta_1: UploadFile = File(...),
    foto_peserta_2: UploadFile = File(...),
    bukti_bayar: UploadFile = File(...),
    peserta_2_identitas: Optional[UploadFile] = File(None),
    user=Depends(get_current_user),
):
    if kategori not in KATEGORI_VALID:
        raise HTTPException(400, "Kategori tidak valid")

    if peserta_2_luar_gereja and peserta_2_identitas is None:
        raise HTTPException(400, "Foto identitas peserta 2 wajib diunggah karena partner dari luar gereja")

    # Upload semua file dulu
    surat_gereja_url = await upload_file(surat_gereja, folder="badminton/surat-gereja")
    foto1_url = await upload_file(foto_peserta_1, folder="badminton/foto-peserta")
    foto2_url = await upload_file(foto_peserta_2, folder="badminton/foto-peserta")
    bukti_url = await upload_file(bukti_bayar, folder="badminton/bukti-bayar")

    peserta_2_identitas_url = None
    if peserta_2_luar_gereja and peserta_2_identitas is not None:
        peserta_2_identitas_url = await upload_file(peserta_2_identitas, folder="badminton/identitas-peserta")

    supabase = get_supabase()
    result = supabase.table("badminton_registrations").insert({
        "user_id": user.id,
        "kategori": kategori,
        "nama_team": nama_team,
        "gereja_asal": gereja_asal,
        "surat_gereja_url": surat_gereja_url,
        "nama_peserta_1": nama_peserta_1,
        "foto_peserta_1_url": foto1_url,
        "nama_peserta_2": nama_peserta_2,
        "foto_peserta_2_url": foto2_url,
        "peserta_2_luar_gereja": peserta_2_luar_gereja,
        "peserta_2_identitas_url": peserta_2_identitas_url,
        "no_hp": no_hp,
        "asal_kota": asal_kota,
        "bukti_bayar_url": bukti_url,
        "ip_address": get_client_ip(request),
    }).execute()

    new_id = result.data[0]["id"] if result.data else None
    return {"message": "Pendaftaran Badminton berhasil", "id": new_id}