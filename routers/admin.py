# routers/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from routers.admin_auth import get_admin_user
from core.database import get_supabase
from pydantic import BaseModel
from typing import Optional
import logging

router = APIRouter(prefix="/api/admin", tags=["Admin Dashboard"])

LOMBA_TABLES = {
    "pes": "pes_registrations",
    "badminton": "badminton_registrations",
    "tenis": "tenis_meja_registrations"
}

class UpdateStatusRequest(BaseModel):
    status: str
    admin_note: Optional[str] = None


@router.get("/me")
async def get_admin_profile(admin = Depends(get_admin_user)):
    return {
        "user_id": admin["user_id"],
        "email": admin["email"],
        "role": admin["role"]
    }


@router.get("/registrations")
async def get_all_registrations(admin = Depends(get_admin_user)):
    supabase = get_supabase()
    role = admin["role"]
    all_rows = []

    allowed_branches = []
    if role in ["super_admin", "bendahara"]:
        allowed_branches = ["pes", "badminton", "tenis"]
    elif role.startswith("admin_"):
        branch = role.replace("admin_", "")
        if branch in LOMBA_TABLES:
            allowed_branches = [branch]

    if not allowed_branches:
        raise HTTPException(status_code=403, detail="Role tidak memiliki akses")

    for branch in allowed_branches:
        table_name = LOMBA_TABLES[branch]
        try:
            res = supabase.table(table_name).select("*").order("created_at", desc=True).execute()
            for row in (res.data or []):
                row["_lomba"] = branch
                all_rows.append(row)
        except Exception as e:
            logging.warning(f"Gagal mengambil data {table_name}: {str(e)}")
            continue

    return {"data": all_rows}


@router.get("/stats")
async def get_admin_stats(admin = Depends(get_admin_user)):
    supabase = get_supabase()
    role = admin["role"]

    allowed_branches = []
    if role in ["super_admin", "bendahara"]:
        allowed_branches = ["pes", "badminton", "tenis"]
    elif role.startswith("admin_"):
        branch = role.replace("admin_", "")
        if branch in LOMBA_TABLES:
            allowed_branches = [branch]

    stats = {}
    total_pendaftar_all = 0
    total_slot_all = 0

    for branch in allowed_branches:
        table_name = LOMBA_TABLES[branch]
        try:
            res = supabase.table(table_name).select("*").execute()
            rows = res.data or []
            
            count_pendaftar = len(rows)
            sum_slots = sum(item.get("jumlah_slot") or 1 for item in rows)

            # Khusus Badminton: Breakdown berdasarkan sub-kategori
            categories_breakdown = {}
            if branch == "badminton":
                for item in rows:
                    kat = item.get("kategori") or "Umum"
                    if kat not in categories_breakdown:
                        categories_breakdown[kat] = {"pendaftar": 0, "total_slot": 0}
                    categories_breakdown[kat]["pendaftar"] += 1
                    categories_breakdown[kat]["total_slot"] += (item.get("jumlah_slot") or 1)

            stats[branch] = {
                "pendaftar": count_pendaftar,
                "total_slot": sum_slots,
                "sub_categories": categories_breakdown if branch == "badminton" else None
            }

            total_pendaftar_all += count_pendaftar
            total_slot_all += sum_slots
        except Exception as e:
            logging.warning(f"Gagal menghitung statistik {table_name}: {str(e)}")
            stats[branch] = {"pendaftar": 0, "total_slot": 0, "sub_categories": None}

    return {
        "overall": {
            "total_pendaftar": total_pendaftar_all,
            "total_slot": total_slot_all
        },
        "by_lomba": stats
    }


@router.patch("/registrations/{lomba}/{registration_id}")
async def update_registration_status(
    lomba: str,
    registration_id: str,
    payload: UpdateStatusRequest,
    admin = Depends(get_admin_user)
):
    if lomba not in LOMBA_TABLES:
        raise HTTPException(status_code=400, detail="Cabang lomba tidak ditemukan")

    role = admin["role"]
    if role not in ["super_admin", "bendahara"] and f"admin_{lomba}" != role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Akses ditolak untuk mengelola cabang lomba ini"
        )

    if payload.status not in ["pending", "verified", "rejected"]:
        raise HTTPException(status_code=400, detail="Status tidak valid")

    supabase = get_supabase()
    table_name = LOMBA_TABLES[lomba]

    res = supabase.table(table_name).update({
        "status": payload.status,
        "admin_note": payload.admin_note
    }).eq("id", registration_id).execute()

    if not res.data:
        raise HTTPException(status_code=404, detail="Data pendaftaran tidak ditemukan")

    return {"message": "Status berhasil diperbarui", "data": res.data[0]}