# InstagramScraper

A professional Instagram scraper that follows best practices for session management and bot detection avoidance. This tool allows you to login once, save your session, and reuse it for all subsequent scraping operations.

## Features

- ✅ **One-time login with persistent session** - Login once and reuse the session forever
- 🛡️ **Anti-bot detection measures** - Random delays, rate limiting, and retry logic
- 🔍 **Hashtag scraping** - Search and scrape posts by hashtag
- 📊 **Comprehensive data extraction** - Extract post data, user info, locations, and media URLs
- 💾 **JSON export** - Save scraped data in structured JSON format
- 🔧 **CLI interface** - Easy-to-use command-line interface

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/InstagramScraper.git
cd InstagramScraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

4. Edit `.env` and add your Instagram credentials:
```env
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
```

## Usage

### 1. First-time login (saves session)
```bash
python main.py login
```

### 2. Scrape a hashtag
```bash
# Basic usage
python main.py scrape -h KetoDiet

# With options
python main.py scrape -h KetoDiet --recent 100 --top 20 --pretty

# Save to specific directory
python main.py scrape -h KetoDiet --output data/

# Skip top posts
python main.py scrape -h KetoDiet --no-top
```

### 3. Check session status
```bash
python main.py status
```

### 4. Logout and clear session
```bash
python main.py logout
```

## CLI Options

### Scrape Command Options:
- `-h, --hashtag`: Hashtag to scrape (required)
- `-r, --recent`: Number of recent posts to scrape (default: 50)
- `-t, --top`: Number of top posts to scrape (default: 9)
- `--no-top`: Skip scraping top posts
- `-o, --output`: Output directory for JSON files (default: output/)
- `--pretty`: Pretty print summary to console

## Data Output

The scraper extracts the following data for each post:
- Post ID and shortcode
- Caption text
- Like and comment counts
- Post timestamp
- Media URLs (without downloading)
- User information (username, full name, verification status)
- Location data (if available)
- Associated hashtags
- Mentioned users

## Configuration

Additional settings can be configured in `.env`:

```env
# Rate limiting (seconds)
MIN_DELAY=1.0
MAX_DELAY=3.0

# Maximum posts per hashtag
MAX_POSTS_PER_HASHTAG=100

# Optional proxy configuration
PROXY_HOST=proxy.example.com
PROXY_PORT=8080
PROXY_USERNAME=proxy_user
PROXY_PASSWORD=proxy_pass
```

## Best Practices

1. **Use consistent IP**: Always access Instagram from the same IP address
2. **Respect rate limits**: The tool automatically adds delays between requests
3. **Session persistence**: The tool saves and reuses sessions to mimic real user behavior
4. **Error handling**: Built-in retry logic with exponential backoff

## Example Output

```json
{
  "hashtag": "KetoDiet",
  "hashtag_info": {
    "id": "123456789",
    "name": "ketodiet",
    "media_count": 5432100
  },
  "scraped_at": "2024-01-20T15:30:00",
  "total_posts_scraped": 59,
  "recent_posts": [
    {
      "post_id": "abc123",
      "shortcode": "Cxyz123",
      "caption_text": "My keto journey...",
      "like_count": 245,
      "comment_count": 12,
      "taken_at": "2024-01-20T14:00:00",
      "media_urls": ["https://..."],
      "user": {
        "username": "ketouser",
        "full_name": "Keto User"
      }
    }
  ]
}
```

## Notes

- The scraper follows Instagram's best practices to avoid detection
- Session files are automatically saved to `session.json`
- All scraping activities are logged to `instagram_scraper.log`
- The tool will not download media files, only extract URLs

## License

MIT License
