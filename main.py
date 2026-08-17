# main.py
import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from core.middleware import AccessLogMiddleware
from routers import pes, badminton, tenis_meja, admin

load_dotenv()

app = FastAPI(title="Youth Fun Day API")

# 1. Daftar Origin Spesifik
allowed_origins = [
    "https://youthfunday.belovesport.com",
    "http://youthfunday.belovesport.com",
    "http://localhost:5178",
    "http://localhost:5173",
    "http://localhost:3000",
]

# 2. Pasang CORSMiddleware sebagai Middleware TERLUAR
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.belovesport\.com",  # Izinkan seluruh subdomain belovesport.com
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)

# 3. Pasang AccessLogMiddleware di dalam layer CORS
app.add_middleware(AccessLogMiddleware)

# 4. Handler Preflight OPTIONS Global
@app.options("/{full_path:path}")
async def preflight_handler(request: Request, full_path: str):
    response = Response()
    origin = request.headers.get("origin", "")
    response.headers["Access-Control-Allow-Origin"] = origin if origin else "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = request.headers.get("access-control-request-headers", "*")
    response.headers["Access-Control-Max-Age"] = "86400"
    return response

# 5. Register Routers
app.include_router(pes.router)
app.include_router(badminton.router)
app.include_router(tenis_meja.router)
app.include_router(admin.router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Youth Fun Day API is running"}