"""Utility functions for YouTube to Doc MVP."""

try:
    import tiktoken
except ImportError:
    tiktoken = None


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human-readable format."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def estimate_tokens(text: str) -> int:
    """Estimate token count for the given text."""
    if tiktoken:
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except:
            pass
    
    # Fallback: rough estimation (1 token ≈ 4 characters)
    return len(text) // 4
