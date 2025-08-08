#!/usr/bin/env python3
import json
import logging
import sys
from pathlib import Path

import click

from src.config import config
from src.scraper import HashtagScraper
from src.session_manager import SessionManager
from src.instagram_client import InstagramClient

logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG to see more details
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('instagram_scraper.log')
    ]
)

logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command()
def login():
    try:
        logger.info("Attempting to login to Instagram...")
        session_manager = SessionManager()
        session_manager.login()
        logger.info("✅ Login successful! Session saved.")
    except Exception as e:
        logger.error(f"❌ Login failed: {e}")
        sys.exit(1)


@cli.command()
@click.option('--hashtag', '-h', required=True, help='Hashtag to scrape (with or without #)')
@click.option('--recent', '-r', default=50, help='Number of recent posts to scrape')
@click.option('--top', '-t', default=9, help='Number of top posts to scrape')
@click.option('--no-top', is_flag=True, help='Skip scraping top posts')
@click.option('--output', '-o', default='output', help='Output directory for JSON files')
@click.option('--pretty', is_flag=True, help='Pretty print output to console')
@click.option('--no-warmup', is_flag=True, help='Skip warm-up session (not recommended)')
def scrape(hashtag, recent, top, no_top, output, pretty, no_warmup):
    try:
        logger.info(f"Starting scrape for hashtag: {hashtag}")
        
        # Create client with warm-up control
        from src.instagram_client import InstagramClient
        client = InstagramClient(warm_up=not no_warmup)
        scraper = HashtagScraper(client=client)
        data = scraper.scrape_hashtag(
            hashtag=hashtag,
            max_recent=recent,
            max_top=top,
            include_top_posts=not no_top
        )
        
        filepath = scraper.save_to_json(data, output)
        
        if pretty:
            print("\n" + "="*50)
            print(f"HASHTAG: #{data.hashtag}")
            print(f"Total posts in hashtag: {data.hashtag_info.media_count:,}")
            print(f"Posts scraped: {data.total_posts_scraped}")
            print(f"Recent posts: {len(data.recent_posts)}")
            print(f"Top posts: {len(data.top_posts)}")
            print("="*50 + "\n")
            
            if data.recent_posts:
                print("SAMPLE RECENT POSTS:")
                for i, post in enumerate(data.recent_posts[:3], 1):
                    print(f"\n{i}. @{post.user.username}")
                    print(f"   Likes: {post.like_count:,} | Comments: {post.comment_count:,}")
                    if post.caption_text:
                        caption_preview = post.caption_text[:100] + "..." if len(post.caption_text) > 100 else post.caption_text
                        print(f"   Caption: {caption_preview}")
                    print(f"   URL: https://instagram.com/p/{post.shortcode}/")
        
        logger.info(f"✅ Scraping completed! Data saved to: {filepath}")
        
    except Exception as e:
        logger.error(f"❌ Scraping failed: {e}")
        sys.exit(1)


@cli.command()
def logout():
    try:
        logger.info("Logging out and clearing session...")
        session_manager = SessionManager()
        session_manager.logout()
        logger.info("✅ Logged out successfully!")
    except Exception as e:
        logger.error(f"❌ Logout failed: {e}")


@cli.command()
@click.option('--duration', '-d', default=60, help='Duration in seconds to warm up (default: 60)')
def warmup(duration):
    """Warm up the session with human-like browsing behavior."""
    try:
        logger.info(f"Starting warm-up session for {duration} seconds...")
        session_manager = SessionManager()
        client = session_manager.login(warm_up=False)  # Don't double warm-up
        
        from src.human_behavior import HumanBehavior
        behavior = HumanBehavior(client)
        behavior.warm_up_session(duration)
        
        logger.info("✅ Warm-up completed successfully!")
    except Exception as e:
        logger.error(f"❌ Warm-up failed: {e}")
        sys.exit(1)


@cli.command()
def status():
    try:
        if not config.SESSION_FILE.exists():
            print("❌ No saved session found")
            return
        
        print("✅ Saved session found")
        print(f"📍 Session file: {config.SESSION_FILE}")
        
        with open(config.SESSION_FILE, 'r') as f:
            session_data = json.load(f)
            if 'user_id' in session_data:
                print(f"👤 User ID: {session_data['user_id']}")
            if 'username' in session_data:
                print(f"📝 Username: {session_data['username']}")
        
    except Exception as e:
        logger.error(f"❌ Could not read session status: {e}")


if __name__ == '__main__':
    cli()