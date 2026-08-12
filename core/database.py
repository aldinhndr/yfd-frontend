import os
from functools import lru_cache
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]


@lru_cache
def get_supabase() -> Client:
    # service_role key -> backend bypass RLS, aman karena tidak pernah dikirim ke frontend
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
