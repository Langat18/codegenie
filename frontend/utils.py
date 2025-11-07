"""
Utility functions for Codebase Genius frontend
"""

from typing import Dict, List, Optional
from datetime import datetime
import re


def validate_github_url(url: str) -> tuple[bool, str]:
    """
    Validate GitHub repository URL
    
    Args:
        url: GitHub URL to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "URL cannot be empty"
    
    # Basic GitHub URL pattern
    pattern = r'^https://github\.com/[\w-]+/[\w.-]+/?$'
    
    if not re.match(pattern, url):
        return False, "Invalid GitHub URL format. Expected: https://github.com/username/repository"
    
    return True, ""


def format_timestamp(iso_timestamp: str) -> str:
    """
    Format ISO timestamp to human-readable format
    
    Args:
        iso_timestamp: ISO format timestamp
        
    Returns:
        Formatted string
    """
    try:
        dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return iso_timestamp


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human-readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "2m 30s")
    """
    if seconds < 60:
        return f"{seconds}s"
    
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    
    if minutes < 60:
        return f"{minutes}m {remaining_seconds}s"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    return f"{hours}h {remaining_minutes}m"


def format_file_size(bytes_size: int) -> str:
    """
    Format file size to human-readable format
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(bytes_size)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.2f} {units[unit_index]}"


def extract_repo_name(url: str) -> str:
    """
    Extract repository name from GitHub URL
    
    Args:
        url: GitHub repository URL
        
    Returns:
        Repository name
    """
    match = re.search(r'github\.com/[\w-]+/([\w.-]+)', url)
    if match:
        repo_name = match.group(1)
        return repo_name.replace('.git', '')
    return "unknown"


def get_status_color(status: str) -> str:
    """
    Get color for a given status
    
    Args:
        status: Status string
        
    Returns:
        Color hex code
    """
    colors = {
        'pending': '#ffc107',
        'validating': '#17a2b8',
        'mapping': '#17a2b8',
        'analyzed': '#007bff',
        'analyzing': '#007bff',
        'generating': '#9c27b0',
        'completed': '#28a745',
        'failed': '#dc3545'
    }
    return colors.get(status.lower(), '#6c757d')


def get_status_icon(status: str) -> str:
    """
    Get emoji icon for a given status
    
    Args:
        status: Status string
        
    Returns:
        Emoji icon
    """
    icons = {
        'pending': '⏳',
        'validating': '🔍',
        'mapping': '🗺️',
        'analyzing': '🔬',
        'generating': '📝',
        'completed': '✅',
        'failed': '❌'
    }
    return icons.get(status.lower(), '🔄')


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def parse_markdown_sections(markdown: str) -> Dict[str, str]:
    """
    Parse markdown content into sections
    
    Args:
        markdown: Markdown content
        
    Returns:
        Dictionary of section_name: content
    """
    sections = {}
    current_section = "header"
    current_content = []
    
    for line in markdown.split('\n'):
        if line.startswith('## '):
            # Save previous section
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            
            # Start new section
            current_section = line[3:].strip().lower().replace(' ', '_')
            current_content = []
        else:
            current_content.append(line)
    
    # Save last section
    if current_content:
        sections[current_section] = '\n'.join(current_content)
    
    return sections


def calculate_progress_percentage(current_stage: str) -> float:
    """
    Calculate approximate progress percentage based on stage
    
    Args:
        current_stage: Current workflow stage
        
    Returns:
        Progress percentage (0-100)
    """
    stage_progress = {
        'validation': 5,
        'validating': 10,
        'cloning': 20,
        'mapping': 30,
        'analyzing': 50,
        'building_ccg': 60,
        'generating': 75,
        'creating_markdown': 90,
        'done': 100,
        'completed': 100
    }
    
    return stage_progress.get(current_stage, 0)


def highlight_code_entities(text: str, entities: List[str]) -> str:
    """
    Highlight code entities in text
    
    Args:
        text: Text to process
        entities: List of entity names to highlight
        
    Returns:
        Text with highlighted entities
    """
    for entity in entities:
        pattern = re.compile(r'\b' + re.escape(entity) + r'\b')
        text = pattern.sub(f'**{entity}**', text)
    
    return text


def sort_sessions(sessions: List[Dict], sort_by: str = 'created_at', reverse: bool = True) -> List[Dict]:
    """
    Sort sessions by specified field
    
    Args:
        sessions: List of session dictionaries
        sort_by: Field to sort by
        reverse: Sort in reverse order
        
    Returns:
        Sorted list of sessions
    """
    return sorted(sessions, key=lambda x: x.get(sort_by, ''), reverse=reverse)


def filter_sessions(sessions: List[Dict], status: Optional[str] = None) -> List[Dict]:
    """
    Filter sessions by status
    
    Args:
        sessions: List of session dictionaries
        status: Status to filter by (None for all)
        
    Returns:
        Filtered list of sessions
    """
    if status is None:
        return sessions
    
    return [s for s in sessions if s.get('status') == status]


def get_language_color(language: str) -> str:
    """
    Get color for programming language
    
    Args:
        language: Language name
        
    Returns:
        Color hex code
    """
    colors = {
        'python': '#3776ab',
        'jac': '#9c27b0',
        'javascript': '#f7df1e',
        'typescript': '#3178c6',
        'java': '#b07219',
        'cpp': '#f34b7d',
        'c': '#555555',
        'rust': '#dea584',
        'go': '#00add8',
        'ruby': '#701516'
    }
    return colors.get(language.lower(), '#6c757d')


def create_download_filename(repo_name: str, format: str = 'md') -> str:
    """
    Create standardized download filename
    
    Args:
        repo_name: Repository name
        format: File format (md, pdf, html)
        
    Returns:
        Filename
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{repo_name}_docs_{timestamp}.{format}"


def is_url_accessible(url: str, timeout: int = 5) -> bool:
    """
    Check if URL is accessible
    
    Args:
        url: URL to check
        timeout: Request timeout in seconds
        
    Returns:
        True if accessible, False otherwise
    """
    try:
        import requests
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code == 200
    except:
        return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    
    return filename or 'unnamed'


def format_error_message(error: str) -> str:
    """
    Format error message for display
    
    Args:
        error: Raw error message
        
    Returns:
        Formatted error message
    """
    # Remove technical stack traces
    if '\n' in error:
        error = error.split('\n')[0]
    
    # Truncate very long errors
    error = truncate_text(error, 200)
    
    return error


def estimate_completion_time(progress: float, elapsed_seconds: int) -> Optional[str]:
    """
    Estimate time to completion based on progress
    
    Args:
        progress: Current progress (0-100)
        elapsed_seconds: Time elapsed so far
        
    Returns:
        Estimated time remaining as string, or None if can't estimate
    """
    if progress <= 0 or progress >= 100:
        return None
    
    # Calculate rate
    rate = progress / elapsed_seconds  # progress per second
    
    if rate <= 0:
        return None
    
    # Calculate remaining
    remaining_progress = 100 - progress
    remaining_seconds = int(remaining_progress / rate)
    
    return format_duration(remaining_seconds)


def get_complexity_label(complexity: int) -> tuple[str, str]:
    """
    Get label and color for complexity score
    
    Args:
        complexity: Complexity score
        
    Returns:
        Tuple of (label, color)
    """
    if complexity <= 5:
        return "Low", "#28a745"
    elif complexity <= 10:
        return "Medium", "#ffc107"
    else:
        return "High", "#dc3545"


def format_lines_of_code(lines: int) -> str:
    """
    Format lines of code with thousands separator
    
    Args:
        lines: Number of lines
        
    Returns:
        Formatted string
    """
    return f"{lines:,} lines"