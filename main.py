import os
from fastapi import FastAPI
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

# 2. Pasang CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 3. Pasang Custom Middleware (Access Log)
app.add_middleware(AccessLogMiddleware)

# 4. Register Routers
app.include_router(pes.router)
app.include_router(badminton.router)
app.include_router(tenis_meja.router)
app.include_router(admin.router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Youth Fun Day API is running"}