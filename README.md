# YouTube to Doc MVP

A simplified version of YouTube-to-Doc that converts YouTube videos into documentation format with metadata and transcripts.

## Features

- 📺 YouTube Video Processing: Extract video metadata and descriptions
- 📝 Transcript Extraction: Automatically extract video transcripts in multiple languages
- ⚡ Fast Processing: Efficient video processing with rate limiting
- 🌍 Multi-Language Support: Support for transcripts in 9+ languages
- 📱 Simple Web Interface: Clean HTML form interface

## Tech Stack

- **Backend**: FastAPI + Python 3.11+
- **Video Processing**: yt-dlp, pytube, youtube-transcript-api
- **Token Estimation**: tiktoken
- **Rate Limiting**: slowapi

## Installation

### Local Installation

```bash
# Clone the repository
git clone https://github.com/gitmvp-com/yt-doc-mvp.git
cd yt-doc-mvp

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## Usage

### Web Interface

1. Open your browser and navigate to `http://localhost:8000`
2. Enter a YouTube video URL
3. Configure processing options:
   - **Transcript Length**: Maximum characters to include
   - **Language**: Preferred transcript language (en, es, fr, de, etc.)
4. Click "Create Docs" to process the video

### API Usage

```bash
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "url=https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  -d "max_transcript_length=10000" \
  -d "language=en"
```

## Supported YouTube URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`

## Supported Languages

- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Japanese (ja)
- Korean (ko)
- Chinese (zh)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Home page with video processing form |
| `POST` | `/process` | Process a YouTube video |
| `GET` | `/health` | Health check endpoint |

## Rate Limits

- Main endpoint: 10 requests per minute per IP

## License

This project is licensed under the MIT License.

## Acknowledgments

- Original project: [YouTube-to-Doc](https://github.com/filiksyos/Youtube-to-Doc)
- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube video processing
