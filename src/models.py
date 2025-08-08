from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class UserInfo(BaseModel):
    pk: str
    username: str
    full_name: Optional[str] = None
    is_private: bool = False
    follower_count: Optional[int] = None
    following_count: Optional[int] = None
    media_count: Optional[int] = None
    biography: Optional[str] = None


class LocationInfo(BaseModel):
    pk: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    lng: Optional[float] = None
    lat: Optional[float] = None


class MediaInfo(BaseModel):
    id: str
    code: str
    taken_at: datetime
    media_type: int
    product_type: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PostData(BaseModel):
    post_id: str = Field(alias="id")
    shortcode: str = Field(alias="code")
    caption_text: Optional[str] = None
    like_count: int
    comment_count: int
    taken_at: datetime
    media_url: Optional[str] = None
    media_urls: List[str] = Field(default_factory=list)
    user: UserInfo
    location: Optional[LocationInfo] = None
    hashtags: List[str] = Field(default_factory=list)
    mentioned_users: List[str] = Field(default_factory=list)
    is_paid_partnership: bool = False
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HashtagInfo(BaseModel):
    id: str
    name: str
    media_count: int
    profile_pic_url: Optional[str] = None


class ScrapedHashtagData(BaseModel):
    hashtag: str
    hashtag_info: HashtagInfo
    scraped_at: datetime = Field(default_factory=datetime.now)
    total_posts_scraped: int
    recent_posts: List[PostData] = Field(default_factory=list)
    top_posts: List[PostData] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }