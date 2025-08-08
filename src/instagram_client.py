import logging
import random
import time
from functools import wraps
from typing import Any, Callable, Optional

from instagrapi import Client
from instagrapi.exceptions import (
    ClientError,
    RateLimitError,
    PleaseWaitFewMinutes,
    ChallengeRequired
)

from .config import config
from .session_manager import SessionManager

logger = logging.getLogger(__name__)


def rate_limit(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        delay = random.uniform(config.MIN_DELAY, config.MAX_DELAY)
        logger.debug(f"Rate limiting: waiting {delay:.2f}s before request")
        time.sleep(delay)
        return func(*args, **kwargs)
    return wrapper


def retry_on_error(max_retries: int = None, delay: float = None):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = max_retries or config.MAX_RETRIES
            retry_delay = delay or config.RETRY_DELAY
            
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except (RateLimitError, PleaseWaitFewMinutes) as e:
                    logger.warning(f"Rate limited on attempt {attempt + 1}: {e}")
                    if attempt < retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        logger.info(f"Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                    else:
                        raise
                except ChallengeRequired as e:
                    logger.error(f"Challenge required: {e}")
                    raise
                except ClientError as e:
                    logger.error(f"Client error on attempt {attempt + 1}: {e}")
                    if attempt < retries - 1:
                        time.sleep(retry_delay)
                    else:
                        raise
                except Exception as e:
                    logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                    raise
            
            return None
        return wrapper
    return decorator


class InstagramClient:
    def __init__(self, session_manager: Optional[SessionManager] = None):
        self.session_manager = session_manager or SessionManager()
        self._client: Optional[Client] = None
    
    @property
    def client(self) -> Client:
        if not self._client:
            self._client = self.session_manager.login()
        return self._client
    
    @rate_limit
    @retry_on_error()
    def get_hashtag_info(self, hashtag: str) -> dict:
        hashtag = hashtag.strip('#').lower()  # Instagram hashtags are case-insensitive
        logger.info(f"Fetching info for hashtag: #{hashtag}")
        return self.client.hashtag_info(hashtag)
    
    @rate_limit
    @retry_on_error()
    def get_hashtag_medias_recent(self, hashtag: str, amount: int = 27) -> list:
        hashtag = hashtag.strip('#').lower()  # Instagram hashtags are case-insensitive
        amount = min(amount, config.MAX_POSTS_PER_HASHTAG)
        logger.info(f"Fetching {amount} recent posts for #{hashtag}")
        
        # hashtag_medias_recent expects the hashtag name, not the ID
        return self.client.hashtag_medias_recent(hashtag, amount)
    
    @rate_limit
    @retry_on_error()
    def get_hashtag_medias_top(self, hashtag: str, amount: int = 9) -> list:
        hashtag = hashtag.strip('#').lower()  # Instagram hashtags are case-insensitive
        amount = min(amount, config.MAX_POSTS_PER_HASHTAG)
        logger.info(f"Fetching {amount} top posts for #{hashtag}")
        
        # hashtag_medias_top expects the hashtag name, not the ID
        return self.client.hashtag_medias_top(hashtag, amount)
    
    @rate_limit
    @retry_on_error()
    def get_media_info(self, media_id: str) -> dict:
        logger.debug(f"Fetching detailed info for media: {media_id}")
        return self.client.media_info(media_id).dict()
    
    @rate_limit
    @retry_on_error()
    def get_user_info(self, user_id: str) -> dict:
        logger.debug(f"Fetching user info for: {user_id}")
        return self.client.user_info(user_id).dict()
    
    def close(self):
        if self._client:
            logger.info("Closing Instagram client")
            self.session_manager.logout()