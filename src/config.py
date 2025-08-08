import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


class Config:
    BASE_DIR = Path(__file__).parent.parent
    SESSION_FILE = BASE_DIR / "session.json"
    
    INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
    INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
    
    PROXY_HOST: Optional[str] = os.getenv("PROXY_HOST")
    PROXY_PORT: Optional[int] = int(os.getenv("PROXY_PORT", 0)) or None
    PROXY_USERNAME: Optional[str] = os.getenv("PROXY_USERNAME")
    PROXY_PASSWORD: Optional[str] = os.getenv("PROXY_PASSWORD")
    
    MIN_DELAY = float(os.getenv("MIN_DELAY", "1.0"))
    MAX_DELAY = float(os.getenv("MAX_DELAY", "3.0"))
    MAX_POSTS_PER_HASHTAG = int(os.getenv("MAX_POSTS_PER_HASHTAG", "100"))
    
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    
    @classmethod
    def get_proxy_url(cls) -> Optional[str]:
        if cls.PROXY_HOST and cls.PROXY_PORT:
            if cls.PROXY_USERNAME and cls.PROXY_PASSWORD:
                return f"http://{cls.PROXY_USERNAME}:{cls.PROXY_PASSWORD}@{cls.PROXY_HOST}:{cls.PROXY_PORT}"
            return f"http://{cls.PROXY_HOST}:{cls.PROXY_PORT}"
        return None
    
    @classmethod
    def validate(cls):
        if not cls.INSTAGRAM_USERNAME or not cls.INSTAGRAM_PASSWORD:
            raise ValueError("Instagram credentials not found in environment variables")


config = Config()