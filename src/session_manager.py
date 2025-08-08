import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from instagrapi import Client
from instagrapi.exceptions import LoginRequired, PleaseWaitFewMinutes

from .config import config

logger = logging.getLogger(__name__)


class SessionManager:
    def __init__(self, session_file: Optional[Path] = None):
        self.session_file = session_file or config.SESSION_FILE
        self.client = Client()
        self._setup_client()
    
    def _setup_client(self):
        proxy_url = config.get_proxy_url()
        if proxy_url:
            self.client.set_proxy(proxy_url)
            logger.info("Proxy configured")
        
        self.client.request_timeout = config.REQUEST_TIMEOUT
        
        # Load device settings if they exist to maintain consistency
        if self.session_file.exists():
            try:
                session_data = self._load_session_file()
                if 'device_settings' in session_data:
                    self.client.set_device(session_data['device_settings'])
                    logger.debug("Loaded existing device settings")
            except Exception:
                pass
    
    def login(self) -> Client:
        try:
            if self._try_load_session():
                logger.info("Successfully logged in using saved session")
                return self.client
        except Exception as e:
            logger.warning(f"Failed to use saved session: {e}")
        
        try:
            logger.info("Attempting fresh login...")
            config.validate()
            
            self.client.login(
                config.INSTAGRAM_USERNAME,
                config.INSTAGRAM_PASSWORD
            )
            
            self._save_session()
            logger.info("Login successful and session saved")
            return self.client
            
        except PleaseWaitFewMinutes as e:
            logger.error(f"Rate limited: {e}")
            raise
        except Exception as e:
            logger.error(f"Login failed: {e}")
            raise
    
    def _try_load_session(self) -> bool:
        if not self.session_file.exists():
            logger.debug("No saved session found")
            return False
        
        try:
            session_data = self._load_session_file()
            self.client.set_settings(session_data)
            
            # Validate session without logging in again
            self.client.get_timeline_feed()
            return True
            
        except LoginRequired:
            logger.debug("Session expired or invalid")
            return False
        except Exception as e:
            logger.debug(f"Session validation failed: {e}")
            return False
    
    def _save_session(self):
        try:
            session_data = self.client.get_settings()
            self.session_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            logger.debug(f"Session saved to {self.session_file}")
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
    
    def _load_session_file(self) -> Dict[str, Any]:
        with open(self.session_file, 'r') as f:
            return json.load(f)
    
    def logout(self):
        try:
            self.client.logout()
            if self.session_file.exists():
                self.session_file.unlink()
            logger.info("Logged out and session cleared")
        except Exception as e:
            logger.error(f"Logout error: {e}")