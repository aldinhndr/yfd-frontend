import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from core.middleware import AccessLogMiddleware
from routers import pes, badminton, tenis_meja

load_dotenv()

app = FastAPI(title="Youth Fun Day API")

FRONTEND_ORIGIN = os.environ.get("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AccessLogMiddleware)

app.include_router(pes.router)
app.include_router(badminton.router)
app.include_router(tenis_meja.router)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Youth Fun Day API is running"}