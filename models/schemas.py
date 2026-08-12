from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime


class RegisterResponse(BaseModel):
    """Response standar setelah berhasil daftar — dipakai di semua router."""
    message: str
    id: Optional[str] = None


class PesRegistration(BaseModel):
    """Bentuk data pendaftaran PES, dipakai untuk dokumentasi & validasi tambahan."""
    nama: str
    no_hp: str
    asal_daerah: str
    slot: Literal[1, 2]


class BadmintonRegistration(BaseModel):
    kategori: Literal["ganda_putra", "ganda_putri", "campuran"]
    nama_team: str
    gereja_asal: str
    nama_peserta_1: str
    nama_peserta_2: str
    no_hp: str
    asal_kota: str


class TenisMejaRegistration(BaseModel):
    nama: str
    no_hp: str
    gereja_asal: str


class RegistrationOut(BaseModel):
    """Dipakai admin dashboard nanti — bentuk data saat ditampilkan/read."""
    id: str
    status: Literal["pending", "verified", "rejected"]
    created_at: datetime
    ip_address: Optional[str] = None
