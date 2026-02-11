"""
Supabase client initialization and database utilities.
"""

from supabase import create_client, Client
from .config import get_settings

settings = get_settings()

# Initialize Supabase client
supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_KEY
)

# Service client for admin operations (if needed)
def get_service_client() -> Client:
    """Get Supabase client with service role key for admin operations."""
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_KEY
    )


def get_db() -> Client:
    """Dependency to get database client."""
    return supabase
