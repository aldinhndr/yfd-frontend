import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from core.database import get_supabase


def get_client_ip(request: Request) -> str:
    # Utamakan header dari reverse proxy (Railway/Render/Vercel), fallback ke IP langsung
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class AccessLogMiddleware(BaseHTTPMiddleware):
    """Catat tiap request: siapa (IP), buka apa (path), berapa lama (ms), status berapa."""

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = int((time.perf_counter() - start) * 1000)

        # Jangan blok response gara-gara logging gagal
        try:
            supabase = get_supabase()
            supabase.table("access_logs").insert({
                "ip_address": get_client_ip(request),
                "user_agent": request.headers.get("user-agent"),
                "path": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            }).execute()
        except Exception:
            pass

        return response
