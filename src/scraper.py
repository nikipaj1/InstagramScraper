import json
import logging
import random
import re
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from .config import config
from .instagram_client import InstagramClient
from .models import (
    PostData,
    UserInfo,
    LocationInfo,
    HashtagInfo,
    ScrapedHashtagData
)

logger = logging.getLogger(__name__)


class HashtagScraper:
    def __init__(self, client: Optional[InstagramClient] = None):
        self.client = client or InstagramClient()
    
    def scrape_hashtag(
        self,
        hashtag: str,
        max_recent: int = 50,
        max_top: int = 9,
        include_top_posts: bool = True
    ) -> ScrapedHashtagData:
        hashtag = hashtag.strip('#')
        logger.info(f"Starting scrape for hashtag: #{hashtag}")
        
        try:
            hashtag_info = self._get_hashtag_info(hashtag)
            
            recent_posts = self._scrape_recent_posts(hashtag, max_recent)
            logger.info(f"Scraped {len(recent_posts)} recent posts")
            
            top_posts = []
            if include_top_posts:
                top_posts = self._scrape_top_posts(hashtag, max_top)
                logger.info(f"Scraped {len(top_posts)} top posts")
            
            scraped_data = ScrapedHashtagData(
                hashtag=hashtag,
                hashtag_info=hashtag_info,
                total_posts_scraped=len(recent_posts) + len(top_posts),
                recent_posts=recent_posts,
                top_posts=top_posts
            )
            
            logger.info(f"Successfully scraped #{hashtag}: {scraped_data.total_posts_scraped} posts")
            return scraped_data
            
        except Exception as e:
            logger.error(f"Failed to scrape #{hashtag}: {e}")
            raise
    
    def _get_hashtag_info(self, hashtag: str) -> HashtagInfo:
        info = self.client.get_hashtag_info(hashtag)
        return HashtagInfo(
            id=str(info.id),
            name=info.name,
            media_count=info.media_count,
            profile_pic_url=str(info.profile_pic_url) if info.profile_pic_url else None
        )
    
    def _scrape_recent_posts(self, hashtag: str, max_posts: int) -> List[PostData]:
        medias = self.client.get_hashtag_medias_recent(hashtag, max_posts)
        posts = []
        for i, media in enumerate(medias):
            posts.append(self._extract_post_data(media))
            # Add small random delay between processing posts to appear more human-like
            if i < len(medias) - 1:
                time.sleep(random.uniform(0.1, 0.3))
        return posts
    
    def _scrape_top_posts(self, hashtag: str, max_posts: int) -> List[PostData]:
        medias = self.client.get_hashtag_medias_top(hashtag, max_posts)
        posts = []
        for i, media in enumerate(medias):
            posts.append(self._extract_post_data(media))
            # Add small random delay between processing posts to appear more human-like
            if i < len(medias) - 1:
                time.sleep(random.uniform(0.1, 0.3))
        return posts
    
    def _extract_post_data(self, media: Any) -> PostData:
        try:
            hashtags = self._extract_hashtags(media.caption_text) if media.caption_text else []
            mentioned_users = self._extract_mentions(media.caption_text) if media.caption_text else []
            
            user_info = UserInfo(
                pk=str(media.user.pk),
                username=media.user.username,
                full_name=media.user.full_name,
                is_private=media.user.is_private,
                is_verified=media.user.is_verified
            )
            
            location_info = None
            if media.location:
                location_info = LocationInfo(
                    pk=str(media.location.pk) if media.location.pk else None,
                    name=media.location.name,
                    address=media.location.address,
                    city=media.location.city,
                    lng=media.location.lng,
                    lat=media.location.lat
                )
            
            media_urls = []
            if hasattr(media, 'thumbnail_url') and media.thumbnail_url:
                media_urls.append(str(media.thumbnail_url))
            elif hasattr(media, 'video_url') and media.video_url:
                media_urls.append(str(media.video_url))
            
            if hasattr(media, 'resources') and media.resources:
                for resource in media.resources:
                    if hasattr(resource, 'thumbnail_url') and resource.thumbnail_url:
                        media_urls.append(str(resource.thumbnail_url))
            
            return PostData(
                post_id=media.id,
                shortcode=media.code,
                caption_text=media.caption_text,
                like_count=media.like_count or 0,
                comment_count=media.comment_count or 0,
                taken_at=media.taken_at,
                media_url=media_urls[0] if media_urls else None,
                media_urls=media_urls,
                user=user_info,
                location=location_info,
                hashtags=hashtags,
                mentioned_users=mentioned_users,
                is_paid_partnership=getattr(media, 'is_paid_partnership', False)
            )
        except Exception as e:
            logger.error(f"Error extracting post data: {e}")
            raise
    
    def _extract_hashtags(self, text: str) -> List[str]:
        if not text:
            return []
        pattern = r'#(\w+)'
        return re.findall(pattern, text)
    
    def _extract_mentions(self, text: str) -> List[str]:
        if not text:
            return []
        pattern = r'@(\w+)'
        return re.findall(pattern, text)
    
    def save_to_json(self, data: ScrapedHashtagData, output_dir: str = "output"):
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{data.hashtag}_{timestamp}.json"
        filepath = output_path / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data.dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Data saved to: {filepath}")
        return filepath