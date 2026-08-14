# routers/badminton.py
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
    no_hp: str = Form(...),
    nama_peserta_1: str = Form(...),
    nama_peserta_2: str = Form(...),
    is_gpin: bool = Form(False),
    gpin_gereja: Optional[str] = Form(None),
    gereja_asal: Optional[str] = Form(None),
    asal_kota: Optional[str] = Form(None),
    partner_luar_gpin: bool = Form(False),
    peserta_2_luar_gereja: bool = Form(False),
    # File upload
    bukti_bayar: UploadFile = File(...),
    surat_gereja: Optional[UploadFile] = File(None),
    foto_peserta_1: Optional[UploadFile] = File(None),
    foto_peserta_2: Optional[UploadFile] = File(None),
    peserta_2_identitas: Optional[UploadFile] = File(None),
    user=Depends(get_current_user),
):
    if kategori not in KATEGORI_VALID:
        raise HTTPException(400, "Kategori tidak valid")

    # Validasi Berkas Jalur Umum
    if not is_gpin:
        if not gereja_asal:
            raise HTTPException(400, "Gereja asal wajib diisi untuk pendaftar umum")
        if not surat_gereja:
            raise HTTPException(400, "Surat pengantar gereja wajib diunggah")
        if not foto_peserta_1 or not foto_peserta_2:
            raise HTTPException(400, "Foto peserta 1 dan peserta 2 wajib diunggah untuk pendaftar umum")
        if peserta_2_luar_gereja and not peserta_2_identitas:
            raise HTTPException(400, "Kartu identitas peserta 2 wajib diunggah")
    else:
        # Validasi Jalur GPIN
        if partner_luar_gpin:
            if not foto_peserta_2:
                raise HTTPException(400, "Foto peserta 2 wajib diunggah jika partner berasal dari luar GPIN")

    # Upload Berkas (Hanya jika file dikirimkan)
    surat_gereja_url = await upload_file(surat_gereja, folder="badminton/surat-gereja") if surat_gereja else None
    foto1_url = await upload_file(foto_peserta_1, folder="badminton/foto-peserta") if foto_peserta_1 else None
    foto2_url = await upload_file(foto_peserta_2, folder="badminton/foto-peserta") if foto_peserta_2 else None
    bukti_url = await upload_file(bukti_bayar, folder="badminton/bukti-bayar")
    
    peserta_2_identitas_url = None
    if (peserta_2_luar_gereja or partner_luar_gpin) and peserta_2_identitas:
        peserta_2_identitas_url = await upload_file(peserta_2_identitas, folder="badminton/identitas-peserta")

    supabase = get_supabase()
    result = supabase.table("badminton_registrations").insert({
        "user_id": user.id,
        "kategori": kategori,
        "nama_team": nama_team,
        "gereja_asal": gpin_gereja if is_gpin else gereja_asal,
        "surat_gereja_url": surat_gereja_url,
        "nama_peserta_1": nama_peserta_1,
        "foto_peserta_1_url": foto1_url,
        "nama_peserta_2": nama_peserta_2,
        "foto_peserta_2_url": foto2_url,
        "peserta_2_luar_gereja": partner_luar_gpin if is_gpin else peserta_2_luar_gereja,
        "peserta_2_identitas_url": peserta_2_identitas_url,
        "no_hp": no_hp,
        "asal_kota": "GPIN Internal" if is_gpin else (asal_kota or "-"),
        "bukti_bayar_url": bukti_url,
        "is_gpin": is_gpin,
        "gpin_gereja": gpin_gereja,
        "partner_luar_gpin": partner_luar_gpin,
        "ip_address": get_client_ip(request),
    }).execute()

    new_id = result.data[0]["id"] if result.data else None
    return {"message": "Pendaftaran Badminton berhasil", "id": new_id}