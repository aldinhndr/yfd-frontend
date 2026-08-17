# main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from core.middleware import AccessLogMiddleware
from routers import pes, badminton, tenis_meja, admin

load_dotenv()

app = FastAPI(title="Youth Fun Day API")

# Daftar Origin Spesifik
allowed_origins = [
    "https://youthfunday.belovesport.com",
    "http://youthfunday.belovesport.com",
    "http://localhost:5178",
    "http://localhost:5173",
    "http://localhost:3000",
]

# CORSMiddleware bawaan FastAPI sudah otomatis menangani preflight OPTIONS,
# TIDAK perlu route handler manual untuk OPTIONS (itu justru bikin konflik).
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.belovesport\.com",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)

app.add_middleware(AccessLogMiddleware)

app.include_router(pes.router)
app.include_router(badminton.router)
app.include_router(tenis_meja.router)
app.include_router(admin.router)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Youth Fun Day API is running"}