from fastapi import APIRouter, Depends, Form, UploadFile, File, Request, HTTPException
from core.database import get_supabase
from core.storage import upload_file
from core.security import get_current_user
from core.middleware import get_client_ip
from models.schemas import RegisterResponse
from routers.admin_auth import require_admin_role
from pydantic import BaseModel

router = APIRouter(prefix="/api/pes", tags=["PES"])

MAX_SLOT_KUOTA = 64  # total slot PES yang tersedia, sesuaikan


@router.post("/register", response_model=RegisterResponse)
async def register_pes(
    request: Request,
    nama: str = Form(...),
    no_hp: str = Form(...),
    asal_daerah: str = Form(...),
    slot: int = Form(...),
    bukti_bayar: UploadFile = File(...),
    user=Depends(get_current_user),
):
    if slot not in (1, 2):
        raise HTTPException(400, "Slot maksimal 2 per orang")

    bukti_url = await upload_file(bukti_bayar, folder="pes/bukti-bayar")
    ip = get_client_ip(request)

    supabase = get_supabase()
    try:
        result = supabase.rpc("register_pes_atomic", {
            "p_user_id": user.id,
            "p_nama_peserta": nama,
            "p_no_hp": no_hp,
            "p_asal_daerah": asal_daerah,
            "p_jumlah_slot": slot,
            "p_bukti_bayar_url": bukti_url,
            "p_ip_address": ip,
            "p_max_slots": MAX_SLOT_KUOTA,
        }).execute()
    except Exception as e:
        # RPC melempar exception kalau kuota penuh (RAISE EXCEPTION di SQL)
        raise HTTPException(400, str(e))

    return {"message": "Pendaftaran PES berhasil", "id": str(result.data)}

class BracketPayload(BaseModel):
    team_name: str
    slots: int
    positions: list[int]

@router.get("/bracket/public")
async def get_public_bracket():
    supabase = get_supabase()
    res = supabase.table("pes_brackets").select("*").order("created_at", desc=False).execute()
    return {"data": res.data or []}

@router.post("/bracket", dependencies=[Depends(require_admin_role(["admin_pes", "bendahara"]))])
async def save_pes_bracket(payload: BracketPayload):
    supabase = get_supabase()
    
    # Validasi Anti-Collision: Cek posisi bagan ganda
    existing = supabase.table("pes_brackets").select("positions").execute()
    used_positions = set()
    for row in (existing.data or []):
        used_positions.update(row.get("positions", []))
        
    for pos in payload.positions:
        if pos in used_positions:
            raise HTTPException(
                status_code=400, 
                detail=f"Posisi bagan #{pos} sudah terisi. Sinkronkan ulang antarmuka Anda."
            )

    # Simpan Data Transaksional
    res = supabase.table("pes_brackets").insert({
        "team_name": payload.team_name,
        "slots": payload.slots,
        "positions": payload.positions
    }).execute()

    if not res.data:
        raise HTTPException(status_code=500, detail="Gagal menyimpan bagan ke database")

    return {"message": "Posisi bagan terkunci aman", "data": res.data[0]}