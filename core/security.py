from fastapi import Header, HTTPException
from core.database import get_supabase


async def get_current_user(authorization: str = Header(None)):
    """
    Ambil user dari token JWT yang dikirim frontend setelah login Google via Supabase.
    Frontend wajib kirim header: Authorization: Bearer <access_token>
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Kamu harus login dengan Google dulu")

    token = authorization.split(" ", 1)[1]
    supabase = get_supabase()

    try:
        user_resp = supabase.auth.get_user(token)
    except Exception:
        raise HTTPException(401, "Sesi login tidak valid, silakan login ulang")

    if not user_resp or not user_resp.user:
        raise HTTPException(401, "Sesi login tidak valid, silakan login ulang")

    return user_resp.user  # punya .id, .email, dst
