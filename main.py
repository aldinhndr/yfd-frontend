# main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers import pes, badminton, tenis_meja, admin

load_dotenv()

app = FastAPI(title="Youth Fun Day API")

# 1. Daftarkan router terlebih dahulu
app.include_router(pes.router)
app.include_router(badminton.router)
app.include_router(tenis_meja.router)
app.include_router(admin.router)

# 2. Ambil origins dari env jika ada, gabungkan dengan default
env_frontend = os.getenv("FRONTEND_ORIGIN", "").rstrip("/")
env_frontend_url = os.getenv("FRONTEND_URL", "").rstrip("/")

origins = [
    "https://youthfunday.belovesport.com",
    "http://youthfunday.belovesport.com",
    "http://localhost:5173",
    "http://localhost:5178",
    "http://localhost:3000",
]
if env_frontend:
    origins.append(env_frontend)
if env_frontend_url:
    origins.append(env_frontend_url)

# 3. Pasang CORSMiddleware di lapisan terluar dengan regex fallback
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(set(origins)),
    # Regex ini mengizinkan https://youthfunday.belovesport.com dan semua subdomain belovesport
    allow_origin_regex=r"^https?://([a-zA-Z0-9-]+\.)*belovesport\.com$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Youth Fun Day API is running"}