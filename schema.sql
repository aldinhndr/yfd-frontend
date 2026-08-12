-- ============================================
-- YOUTH FUN DAY — DATABASE SCHEMA
-- Jalankan di Supabase SQL Editor
-- ============================================

create extension if not exists "pgcrypto";

-- PES
create table if not exists pes_registrations (
  id uuid primary key default gen_random_uuid(),
  nama text not null,
  no_hp text not null,
  asal_daerah text not null,
  slot int not null check (slot in (1,2)),
  bukti_bayar_url text,
  status text not null default 'pending' check (status in ('pending','verified','rejected')),
  ip_address text,
  created_at timestamptz default now()
);

-- BADMINTON
create table if not exists badminton_registrations (
  id uuid primary key default gen_random_uuid(),
  kategori text not null check (kategori in ('ganda_putra','ganda_putri','campuran')),
  nama_team text not null,
  gereja_asal text not null,
  surat_gereja_url text,
  nama_peserta_1 text not null,
  foto_peserta_1_url text,
  nama_peserta_2 text not null,
  foto_peserta_2_url text,
  no_hp text not null,
  asal_kota text not null,
  bukti_bayar_url text,
  status text not null default 'pending' check (status in ('pending','verified','rejected')),
  ip_address text,
  created_at timestamptz default now()
);

-- TENIS MEJA (internal, input manual admin biasanya, tapi tetap sediakan tabel)
create table if not exists tenis_meja_registrations (
  id uuid primary key default gen_random_uuid(),
  nama text not null,
  no_hp text not null,
  gereja_asal text not null,
  status text not null default 'pending' check (status in ('pending','verified','rejected')),
  ip_address text,
  created_at timestamptz default now()
);

-- ACCESS LOG (buat pantau kinerja & IP tracking nanti)
create table if not exists access_logs (
  id uuid primary key default gen_random_uuid(),
  ip_address text,
  user_agent text,
  path text,
  method text,
  status_code int,
  duration_ms int,
  created_at timestamptz default now()
);

-- Index biar query admin dashboard cepat
create index if not exists idx_pes_status on pes_registrations(status);
create index if not exists idx_badminton_status on badminton_registrations(status);
create index if not exists idx_tenismeja_status on tenis_meja_registrations(status);
create index if not exists idx_logs_created on access_logs(created_at desc);

-- Storage bucket untuk file upload (bukti bayar, foto, surat gereja)
insert into storage.buckets (id, name, public)
values ('yfd-uploads', 'yfd-uploads', true)
on conflict (id) do nothing;
