"""
Configuration settings for the Budget Tracker API.
Loads environment variables and provides app-wide settings.
"""

import os
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")  # anon key for client
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")  # service role
    
    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # API Settings
    API_VERSION: str = "1.0.0"
    API_TITLE: str = "Budget Tracker API"
    
    def validate(self) -> bool:
        """Validate that required settings are present."""
        required = [self.SUPABASE_URL, self.SUPABASE_KEY]
        return all(required)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
