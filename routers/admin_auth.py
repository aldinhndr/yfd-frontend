# routers/admin_auth.py
from fastapi import Depends, HTTPException, status
from core.security import get_current_user
from core.database import get_supabase

async def get_admin_user(current_user = Depends(get_current_user)):
    supabase = get_supabase()
    
    # Query ke tabel admin_users berdasarkan email user yang sedang login
    response = (
        supabase.table("admin_users")
        .select("*")
        .eq("email", current_user.email)
        .execute()
    )
    
    if not response.data or len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Anda bukan administrator."
        )
    
    admin_data = response.data[0]
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "role": admin_data["role"]  # Mengambil nilai role dari tabel admin_users
    }

def require_admin_role(allowed_roles: list[str]):
    def role_checker(admin = Depends(get_admin_user)):
        if admin["role"] not in allowed_roles and admin["role"] != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akses ditolak. Peran administrator tidak mencukupi."
            )
        return admin
    return role_checker