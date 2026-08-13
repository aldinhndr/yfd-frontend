# routers/admin_auth.py
from fastapi import Depends, HTTPException, status
from core.security import get_current_user
from core.database import get_supabase
import logging

logger = logging.getLogger(__name__)

async def get_admin_user(current_user = Depends(get_current_user)):
    if not current_user or not hasattr(current_user, "id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kredensial autentikasi tidak valid."
        )

    supabase = get_supabase()
    user_id = str(current_user.id)
    user_email = (getattr(current_user, "email", "") or "").strip().lower()

    try:
        # 1. Kueri Utama: Cek ketersediaan berdasarkan ID unik (UUID)
        response = (
            supabase.table("admin_users")
            .select("*")
            .eq("id", user_id)
            .execute()
        )

        # 2. Fallback Kueri: Jika tidak ditemukan berdasarkan ID, cek berdasarkan Email (Case-Insensitive)
        if not response.data:
            response = (
                supabase.table("admin_users")
                .select("*")
                .ilike("email", user_email)
                .execute()
            )

        # Jika tetap tidak ditemukan di tabel admin_users
        if not response.data:
            logger.warning(f"Akses Admin Ditolak: ID={user_id}, Email={user_email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Akses ditolak. Akun ({user_email}) tidak terdaftar sebagai administrator."
            )

        admin_data = response.data[0]

        return {
            "user_id": admin_data["id"],
            "email": admin_data["email"],
            "role": admin_data["role"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pada verifikasi admin: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan internal saat memverifikasi hak akses admin."
        )


def require_admin_role(allowed_roles: list[str]):
    def role_checker(admin = Depends(get_admin_user)):
        current_role = admin.get("role")
        
        if current_role != "super_admin" and current_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akses ditolak. Peran administrator Anda tidak memiliki izin untuk tindakan ini."
            )
        return admin
    return role_checker