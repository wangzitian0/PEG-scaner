"""NewsArticle field whitelist."""

from typing import Any, Dict, List, Tuple

# Required fields
REQUIRED = ['article_id', 'title']

# Validated fields
VALIDATED = ['published_at', 'source_name']

NEWS_WHITELIST = {
    'required': REQUIRED,
    'validated': VALIDATED,
}


def validate_news(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate news article data against whitelist.
    
    Returns:
        (is_valid, error_messages)
    """
    errors = []
    
    # Required: article_id
    article_id = data.get('article_id')
    if not article_id:
        errors.append("article_id is required")
    
    # Required: title (non-empty)
    title = data.get('title')
    if not title or not str(title).strip():
        errors.append("title is required and must be non-empty")
    
    return len(errors) == 0, errors

