# main.py
import os
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers import pes, badminton, tenis_meja, admin

load_dotenv()

app = FastAPI(title="Youth Fun Day API")

# =================================================================
# 1. SOLUSI PALU GODAM: MANUAL CORS INJECTOR & ERROR CATCHER
# =================================================================
@app.middleware("http")
async def force_cors_and_catch_errors(request: Request, call_next):
    origin = request.headers.get("Origin") or request.headers.get("origin")
    
    # A. Cegat paksa request OPTIONS (Preflight) dan kembalikan 200 OK secara instan
    if request.method == "OPTIONS":
        response = Response(status_code=200)
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        else:
            response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept, Origin, User-Agent, X-Requested-With"
        return response

    # B. Proses request normal dengan proteksi Crash (Tahan Banting)
    try:
        response = await call_next(request)
    except Exception as exc:
        # Jika kode backend CRASH (Error 500), bungkus errornya menjadi JSON terstruktur
        response = JSONResponse(
            status_code=500,
            content={"detail": f"Internal Server Error: {str(exc)}"}
        )
        
    # C. Paksa sisipkan header CORS pada SETIAP response yang keluar (termasuk saat error!)
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        
    return response

# =================================================================
# 2. CORS MIDDLEWARE BAWAAN (Sebagai Lapis Kedua)
# =================================================================
env_frontend = os.getenv("FRONTEND_ORIGIN", "").rstrip("/")
env_frontend_url = os.getenv("FRONTEND_URL", "").rstrip("/")

origins = [
    "https://youthfunday.belovesport.com",
    "http://youthfunday.belovesport.com",
    "http://localhost:5173",
    "http://localhost:5178",
    "http://localhost:3000",
]
if env_frontend: origins.append(env_frontend)
if env_frontend_url: origins.append(env_frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(set(origins)),
    allow_origin_regex=r"^https?://([a-zA-Z0-9-]+\.)*belovesport\.com$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)

# =================================================================
# 3. REGISTRASI ROUTERS
# =================================================================
app.include_router(pes.router)
app.include_router(badminton.router)
app.include_router(tenis_meja.router)
app.include_router(admin.router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Youth Fun Day API is running (CORS Forced)"}