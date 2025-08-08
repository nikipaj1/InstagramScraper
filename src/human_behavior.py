import logging
import random
import time
from typing import Optional, List

from instagrapi import Client
from instagrapi.types import Media

logger = logging.getLogger(__name__)


class HumanBehavior:
    """Simulates human-like Instagram browsing behavior to avoid detection."""
    
    def __init__(self, client: Client):
        self.client = client
        
    def warm_up_session(self, duration_seconds: int = 60):
        """
        Warm up the session by browsing timeline like a human would.
        
        Args:
            duration_seconds: How long to browse for (default 60 seconds)
        """
        logger.info(f"Starting warm-up session for {duration_seconds} seconds...")
        start_time = time.time()
        posts_viewed = 0
        
        while time.time() - start_time < duration_seconds:
            try:
                # Scroll timeline
                posts_viewed += self._browse_timeline()
                
                # Sometimes check stories
                if random.random() < 0.3:
                    self._check_stories()
                
                # Sometimes check explore page
                if random.random() < 0.2:
                    self._browse_explore()
                
                # Random long pause (like reading a post)
                if random.random() < 0.3:
                    reading_time = random.uniform(5, 15)
                    logger.debug(f"Reading post for {reading_time:.1f}s...")
                    time.sleep(reading_time)
                
            except Exception as e:
                logger.warning(f"Error during warm-up: {e}")
                time.sleep(5)
        
        logger.info(f"Warm-up complete. Viewed approximately {posts_viewed} posts")
    
    def _browse_timeline(self) -> int:
        """Browse timeline and return number of posts viewed."""
        try:
            # Get timeline feed
            timeline = self.client.get_timeline_feed()
            
            if not timeline:
                return 0
            
            # Random number of posts to "view"
            num_to_view = random.randint(3, 8)
            posts_viewed = 0
            
            # Get the actual media items from timeline
            medias = []
            if isinstance(timeline, list):
                medias = timeline[:num_to_view]
            elif isinstance(timeline, dict):
                # Handle dict response from instagrapi
                if 'feed_items' in timeline:
                    for item in timeline['feed_items'][:num_to_view]:
                        if isinstance(item, dict) and 'media_or_ad' in item:
                            medias.append(item['media_or_ad'])
                        elif hasattr(item, 'media_or_ad'):
                            medias.append(item.media_or_ad)
            elif hasattr(timeline, 'feed_items'):
                for item in timeline.feed_items[:num_to_view]:
                    if hasattr(item, 'media_or_ad') and item.media_or_ad:
                        medias.append(item.media_or_ad)
            
            for media in medias:
                # Get username and media id
                username = None
                media_id = None
                
                if isinstance(media, dict):
                    username = media.get('user', {}).get('username', 'unknown')
                    media_id = media.get('id') or media.get('pk')
                else:
                    username = getattr(media.user, 'username', 'unknown') if hasattr(media, 'user') else 'unknown'
                    media_id = getattr(media, 'id', None) or getattr(media, 'pk', None)
                
                # Simulate viewing time
                view_time = random.uniform(1.5, 4.0)
                logger.debug(f"Viewing post from @{username} for {view_time:.1f}s")
                time.sleep(view_time)
                
                # Sometimes like posts (but rarely)
                if random.random() < 0.05 and media_id:
                    try:
                        self.client.media_like(media_id)
                        logger.debug(f"Liked post from @{username}")
                        time.sleep(random.uniform(0.5, 1.5))
                    except:
                        pass
                
                # Sometimes view comments
                if random.random() < 0.15 and media_id:
                    self._view_comments(media_id)
                
                posts_viewed += 1
            
            # Simulate scrolling
            scroll_time = random.uniform(1, 3)
            time.sleep(scroll_time)
            
            return posts_viewed
            
        except Exception as e:
            logger.debug(f"Error browsing timeline: {e}")
            return 0
    
    def _check_stories(self):
        """Check a few stories."""
        try:
            logger.debug("Checking stories...")
            
            # Get story feed using the correct method
            reels = self.client.get_reels_tray_feed()
            
            tray = []
            if isinstance(reels, dict) and 'tray' in reels:
                tray = reels['tray']
            elif hasattr(reels, 'tray'):
                tray = reels.tray
            
            if tray:
                # View 1-3 stories
                num_stories = min(random.randint(1, 3), len(tray))
                
                for reel in tray[:num_stories]:
                    username = None
                    user_pk = None
                    
                    if isinstance(reel, dict):
                        user = reel.get('user', {})
                        username = user.get('username', 'unknown')
                        user_pk = user.get('pk')
                    elif hasattr(reel, 'user'):
                        username = getattr(reel.user, 'username', 'unknown')
                        user_pk = getattr(reel.user, 'pk', None)
                        
                    if username:
                        logger.debug(f"Viewing story from @{username}")
                        
                        # Mark story as seen
                        if user_pk:
                            try:
                                story_feed = self.client.user_stories(user_pk)
                                if story_feed:
                                    # Simulate watching time
                                    watch_time = random.uniform(2, 5)
                                    time.sleep(watch_time)
                            except:
                                pass
            
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            logger.debug(f"Error checking stories: {e}")
    
    def _browse_explore(self):
        """Browse explore page briefly."""
        try:
            logger.debug("Browsing explore page...")
            
            # Get explore feed using the correct method
            explore = self.client.explore_page()
            
            items = []
            if isinstance(explore, dict) and 'items' in explore:
                items = explore['items']
            elif hasattr(explore, 'items'):
                items = explore.items
            elif isinstance(explore, list):
                items = explore
                
            if items:
                # View 2-5 posts
                num_to_view = min(random.randint(2, 5), len(items))
                
                for item in items[:num_to_view]:
                    media = None
                    if isinstance(item, dict) and 'media' in item:
                        media = item['media']
                    elif hasattr(item, 'media'):
                        media = item.media
                        
                    if media:
                        view_time = random.uniform(1, 3)
                        logger.debug(f"Viewing explore post for {view_time:.1f}s")
                        time.sleep(view_time)
            
        except Exception as e:
            logger.debug(f"Error browsing explore: {e}")
    
    def _view_comments(self, media_id: str):
        """View comments on a post."""
        try:
            logger.debug("Viewing comments...")
            time.sleep(random.uniform(2, 4))
        except Exception as e:
            logger.debug(f"Error viewing comments: {e}")
    
    def random_action_delay(self):
        """Add a random delay between actions."""
        delay = random.uniform(0.5, 2.0)
        time.sleep(delay)
    
    def simulate_typing(self, text: str) -> float:
        """
        Simulate human typing speed and return the time it would take.
        
        Args:
            text: The text being "typed"
            
        Returns:
            Time in seconds it would take to type
        """
        # Average typing speed: 40 words per minute
        # With variations and pauses
        words = len(text.split())
        base_time = (words / 40) * 60  # Convert to seconds
        
        # Add some randomness
        typing_time = base_time * random.uniform(0.8, 1.3)
        
        # Add thinking pauses
        typing_time += random.uniform(1, 3)
        
        return typing_time