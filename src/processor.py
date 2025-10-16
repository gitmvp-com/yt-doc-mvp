"""YouTube video processor for extracting video data and transcripts."""

import asyncio
import os
from typing import Optional, Tuple, List, Dict, Any

from dotenv import load_dotenv

load_dotenv()

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.formatters import TextFormatter
except ImportError:
    YouTubeTranscriptApi = None
    TextFormatter = None

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

try:
    from pytube import YouTube
except ImportError:
    YouTube = None

from .schemas import VideoQuery


class YouTubeProcessor:
    """Processor for extracting YouTube video information and content."""
    
    def __init__(self):
        """Initialize the YouTube processor."""
        self.text_formatter = TextFormatter() if TextFormatter else None
    
    async def process_video(
        self, 
        query: VideoQuery
    ) -> Tuple[Dict[str, Any], Optional[str], Optional[List[str]]]:
        """Process a YouTube video and extract information and transcript."""
        video_id = query.extract_video_id()
        
        # Extract video information
        video_info = await self._get_video_info(video_id, query.url)
        
        # Extract transcript
        transcript, detected_language = await self._get_transcript(
            video_id, 
            query.language, 
            query.max_transcript_length
        )
        
        # Add detected language to video info
        if detected_language:
            video_info["detected_transcript_language"] = detected_language
        
        return video_info, transcript, None
    
    async def _get_video_info(self, video_id: str, url: str) -> Dict[str, Any]:
        """Extract video information using available libraries."""
        # Try yt-dlp first
        if yt_dlp:
            try:
                return await self._get_video_info_yt_dlp(video_id, url)
            except Exception as e:
                print(f"yt-dlp failed: {e}")
        
        # Fallback to pytube
        if YouTube:
            try:
                return await self._get_video_info_pytube(url)
            except Exception as e:
                print(f"pytube failed: {e}")
        
        # Minimal fallback
        return {
            "title": f"Video {video_id}",
            "description": "Description not available",
            "duration": 0,
            "view_count": None,
            "channel": "Unknown Channel",
            "upload_date": None,
            "url": url,
            "video_id": video_id,
            "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        }
    
    async def _get_video_info_yt_dlp(self, video_id: str, url: str) -> Dict[str, Any]:
        """Extract video info using yt-dlp."""
        def extract_info():
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    "title": info.get('title', 'Unknown Title'),
                    "description": info.get('description', ''),
                    "duration": info.get('duration', 0),
                    "view_count": info.get('view_count'),
                    "channel": info.get('uploader', 'Unknown Channel'),
                    "upload_date": info.get('upload_date'),
                    "url": url,
                    "video_id": video_id,
                    "thumbnail_url": info.get('thumbnail')
                }
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, extract_info)
    
    async def _get_video_info_pytube(self, url: str) -> Dict[str, Any]:
        """Extract video info using pytube."""
        def extract_info():
            yt = YouTube(url)
            return {
                "title": yt.title,
                "description": yt.description,
                "duration": yt.length,
                "view_count": yt.views,
                "channel": yt.author,
                "upload_date": yt.publish_date.strftime('%Y%m%d') if yt.publish_date else None,
                "url": url,
                "video_id": yt.video_id,
                "thumbnail_url": yt.thumbnail_url
            }
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, extract_info)
    
    async def _get_transcript(
        self, 
        video_id: str, 
        language: str = "en", 
        max_length: int = 10000
    ) -> Tuple[Optional[str], Optional[str]]:
        """Extract video transcript using YouTube Transcript API."""
        if not YouTubeTranscriptApi or not self.text_formatter:
            return None, None
        
        def extract_transcript():
            try:
                # Try to get transcript list
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                
                # Try manual captions first, then auto-generated
                transcript = None
                detected_language = language
                
                try:
                    transcript = transcript_list.find_manually_created_transcript([language])
                except:
                    try:
                        transcript = transcript_list.find_generated_transcript([language])
                    except:
                        # Fall back to any available transcript
                        for t in transcript_list:
                            if not t.is_generated:
                                transcript = t
                                detected_language = t.language_code
                                break
                        if not transcript:
                            for t in transcript_list:
                                transcript = t
                                detected_language = t.language_code
                                break
                
                if not transcript:
                    return None, None
                
                # Fetch and format transcript
                fetched_transcript = transcript.fetch()
                formatted_text = self.text_formatter.format_transcript(fetched_transcript)
                
                # Trim to max length if specified
                if max_length and len(formatted_text) > max_length:
                    formatted_text = formatted_text[:max_length] + "\n[Transcript truncated...]"
                
                return formatted_text, detected_language
                
            except Exception as e:
                print(f"Transcript extraction failed: {e}")
                return None, None
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, extract_transcript)
