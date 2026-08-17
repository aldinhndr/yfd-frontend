import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers import pes, badminton, tenis_meja, admin

load_dotenv()

app = FastAPI(title="Youth Fun Day API")


# ============================================================
# CORS
# ============================================================

origins = [
    "https://youthfunday.belovesport.com",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5178",
]

frontend_origin = os.getenv("FRONTEND_ORIGIN", "").rstrip("/")
frontend_url = os.getenv("FRONTEND_URL", "").rstrip("/")

if frontend_origin:
    origins.append(frontend_origin)

if frontend_url:
    origins.append(frontend_url)


app.add_middleware(
    CORSMiddleware,
    allow_origins=list(set(origins)),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(pes.router)
app.include_router(badminton.router)
app.include_router(tenis_meja.router)
app.include_router(admin.router)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "Youth Fun Day API is running"
    }