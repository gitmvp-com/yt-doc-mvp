"""Main FastAPI application for YouTube to Doc MVP."""

import os
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.responses import Response

from .processor import YouTubeProcessor
from .schemas import VideoQuery
from .utils import format_duration, estimate_tokens

# Load environment variables
load_dotenv()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(title="YouTube to Doc MVP")
app.state.limiter = limiter

# Setup templates
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Initialize YouTube processor
processor = YouTubeProcessor()

# Rate limit exception handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "error": "Rate limit exceeded. Please try again later."
        },
        status_code=429
    )


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page with video processing form."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/process", response_class=HTMLResponse)
@limiter.limit("10/minute")
async def process_video(
    request: Request,
    url: str = Form(...),
    max_transcript_length: int = Form(10000),
    language: str = Form("en")
):
    """Process a YouTube video and return formatted documentation."""
    try:
        # Create query object
        query = VideoQuery(
            url=url,
            max_transcript_length=max_transcript_length,
            language=language,
            include_comments=False
        )
        
        # Process the video
        video_info, transcript, _ = await processor.process_video(query)
        
        # Format the output
        output = format_output(video_info, transcript)
        
        # Estimate tokens
        token_count = estimate_tokens(output)
        
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "video_info": video_info,
                "output": output,
                "token_count": token_count,
                "transcript_available": transcript is not None
            }
        )
        
    except ValueError as e:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": str(e)},
            status_code=400
        )
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": f"Error processing video: {str(e)}"},
            status_code=500
        )


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


def format_output(video_info: Dict, transcript: str = None) -> str:
    """Format video information and transcript into documentation."""
    output = []
    output.append("# YouTube Video Documentation\n")
    output.append(f"## {video_info.get('title', 'Unknown Title')}\n")
    
    # Metadata section
    output.append("### Metadata\n")
    output.append(f"- **Video ID**: {video_info.get('video_id', 'N/A')}")
    output.append(f"- **Channel**: {video_info.get('channel', 'N/A')}")
    output.append(f"- **Duration**: {format_duration(video_info.get('duration', 0))}")
    
    if video_info.get('view_count'):
        output.append(f"- **Views**: {video_info['view_count']:,}")
    
    if video_info.get('upload_date'):
        output.append(f"- **Upload Date**: {video_info['upload_date']}")
    
    output.append(f"- **URL**: {video_info.get('url', 'N/A')}\n")
    
    # Description section
    if video_info.get('description'):
        output.append("### Description\n")
        output.append(video_info['description'])
        output.append("\n")
    
    # Transcript section
    if transcript:
        output.append("### Transcript\n")
        if video_info.get('detected_transcript_language'):
            output.append(f"*Language: {video_info['detected_transcript_language']}*\n")
        output.append(transcript)
    else:
        output.append("### Transcript\n")
        output.append("*Transcript not available for this video.*\n")
    
    return "\n".join(output)
