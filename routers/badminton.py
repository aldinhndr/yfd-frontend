# routers/badminton.py
from typing import Optional
from fastapi import APIRouter, Depends, Form, UploadFile, File, Request, HTTPException, status
from core.database import get_supabase
from core.storage import upload_file
from core.security import get_current_user
from core.middleware import get_client_ip
from models.schemas import RegisterResponse

router = APIRouter(prefix="/api/badminton", tags=["Badminton"])

KATEGORI_VALID = {"ganda_putra", "ganda_putri", "campuran"}
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
ALLOWED_DOC_TYPES = ALLOWED_IMAGE_TYPES.union({"application/pdf"})
MAX_FILE_SIZE = 5 * 1024 * 1024  # Maksimal 5 MB per file


def is_valid_file(file: Optional[UploadFile]) -> bool:
    """Mengecek apakah file benar-benar diunggah (bukan objek file kosong dari FormData)."""
    return bool(file and file.filename and file.filename.strip())


async def validate_file_security(file: UploadFile, allowed_types: set, label: str):
    """Validasi ekstensi, content-type, dan batas ukuran file."""
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Format berkas {label} tidak didukung. Gunakan format JPG, PNG, atau PDF.",
        )
    
    # Baca file untuk cek ukuran
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ukuran berkas {label} melebihi batas maksimal 5 MB.",
        )
    # Kembalikan cursor stream ke awal setelah dibaca
    await file.seek(0)


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
    # 1. Validasi Kategori
    if kategori not in KATEGORI_VALID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kategori tidak valid.",
        )

    # 2. Validasi Bukti Pembayaran (Wajib)
    if not is_valid_file(bukti_bayar):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bukti pembayaran wajib diunggah.",
        )
    await validate_file_security(bukti_bayar, ALLOWED_DOC_TYPES, "Bukti Bayar")

    # 3. Validasi Logika Bisnis & Berkas
    if not is_gpin:
        # Jalur Umum
        if not gereja_asal or not gereja_asal.strip():
            raise HTTPException(400, "Gereja asal wajib diisi untuk pendaftar umum.")
        
        if not is_valid_file(surat_gereja):
            raise HTTPException(400, "Surat pengantar gereja wajib diunggah untuk pendaftar umum.")
        await validate_file_security(surat_gereja, ALLOWED_DOC_TYPES, "Surat Pengantar Gereja")

        if not is_valid_file(foto_peserta_1) or not is_valid_file(foto_peserta_2):
            raise HTTPException(400, "Foto peserta 1 dan peserta 2 wajib diunggah untuk pendaftar umum.")
        await validate_file_security(foto_peserta_1, ALLOWED_IMAGE_TYPES, "Foto Peserta 1")
        await validate_file_security(foto_peserta_2, ALLOWED_IMAGE_TYPES, "Foto Peserta 2")

        if peserta_2_luar_gereja:
            if not is_valid_file(peserta_2_identitas):
                raise HTTPException(400, "Kartu identitas peserta 2 wajib diunggah jika berasal dari luar gereja.")
            await validate_file_security(peserta_2_identitas, ALLOWED_DOC_TYPES, "Identitas Peserta 2")
    else:
        # Jalur GPIN
        if not gpin_gereja or not gpin_gereja.strip():
            raise HTTPException(400, "Cabang gereja GPIN wajib dipilih.")

        if partner_luar_gpin:
            if not is_valid_file(foto_peserta_2):
                raise HTTPException(400, "Foto peserta 2 wajib diunggah jika partner berasal dari luar GPIN.")
            await validate_file_security(foto_peserta_2, ALLOWED_IMAGE_TYPES, "Foto Peserta 2")

            if not is_valid_file(peserta_2_identitas):
                raise HTTPException(400, "Identitas peserta 2 wajib diunggah jika partner berasal dari luar GPIN.")
            await validate_file_security(peserta_2_identitas, ALLOWED_DOC_TYPES, "Identitas Peserta 2")

    # 4. Upload Berkas ke Storage (Hanya berkas yang valid)
    surat_gereja_url = await upload_file(surat_gereja, folder="badminton/surat-gereja") if is_valid_file(surat_gereja) else None
    foto1_url = await upload_file(foto_peserta_1, folder="badminton/foto-peserta") if is_valid_file(foto_peserta_1) else None
    foto2_url = await upload_file(foto_peserta_2, folder="badminton/foto-peserta") if is_valid_file(foto_peserta_2) else None
    bukti_url = await upload_file(bukti_bayar, folder="badminton/bukti-bayar")

    peserta_2_identitas_url = None
    if is_valid_file(peserta_2_identitas):
        peserta_2_identitas_url = await upload_file(peserta_2_identitas, folder="badminton/identitas-peserta")

    # 5. Simpan Data ke Database
    try:
        supabase = get_supabase()
        result = supabase.table("badminton_registrations").insert({
            "user_id": user.id,
            "kategori": kategori,
            "nama_team": nama_team.strip(),
            "gereja_asal": gpin_gereja.strip() if is_gpin else gereja_asal.strip(),
            "surat_gereja_url": surat_gereja_url,
            "nama_peserta_1": nama_peserta_1.strip(),
            "foto_peserta_1_url": foto1_url,
            "nama_peserta_2": nama_peserta_2.strip(),
            "foto_peserta_2_url": foto2_url,
            "peserta_2_luar_gereja": partner_luar_gpin if is_gpin else peserta_2_luar_gereja,
            "peserta_2_identitas_url": peserta_2_identitas_url,
            "no_hp": no_hp.strip(),
            "asal_kota": "GPIN Internal" if is_gpin else (asal_kota.strip() if asal_kota else "-"),
            "bukti_bayar_url": bukti_url,
            "is_gpin": is_gpin,
            "gpin_gereja": gpin_gereja.strip() if gpin_gereja else None,
            "partner_luar_gpin": partner_luar_gpin,
            "ip_address": get_client_ip(request),
            "status": "pending",
        }).execute()

        if not result.data:
            raise HTTPException(500, "Gagal menyimpan pendaftaran ke database.")

        new_id = result.data[0]["id"]
        return {"message": "Pendaftaran Badminton berhasil", "id": new_id}

    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise exc
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan saat memproses data: {str(exc)}",
        )