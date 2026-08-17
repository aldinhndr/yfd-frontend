import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from core.middleware import AccessLogMiddleware
from routers import pes, badminton, tenis_meja, admin

load_dotenv()

app = FastAPI(title="Youth Fun Day API")

frontend_env = os.environ.get("FRONTEND_URL") or os.environ.get("FRONTEND_ORIGIN") or ""
frontend_clean = frontend_env.strip().rstrip("/")

allowed_origins = [
    "https://youthfunday.belovesport.com",
    "http://youthfunday.belovesport.com",
    "http://localhost:5178",
    "http://localhost:5173",
    "http://localhost:3000",
]

if frontend_clean and frontend_clean not in allowed_origins:
    allowed_origins.append(frontend_clean)

# 1. Pasang Custom Middleware terlebih dahulu agar CORSMiddleware dieksekusi di LAPISAN TERLUAR
app.add_middleware(AccessLogMiddleware)

# 2. Pasang CORSMiddleware paling akhir agar menangani preflight request pertama kali
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)

# 3. Explicit Global OPTIONS Handler (Menjamin response preflight selalu 200 OK & pasang CORS)
@app.options("/{full_path:path}")
async def preflight_handler(request: Request, full_path: str):
    response = Response()
    origin = request.headers.get("origin")
    
    if origin in allowed_origins or "*" in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = request.headers.get("access-control-request-headers", "*")
        response.headers["Access-Control-Max-Age"] = "86400"
    return response

# 4. Register Routers
app.include_router(pes.router)
app.include_router(badminton.router)
app.include_router(tenis_meja.router)
app.include_router(admin.router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Youth Fun Day API is running"}