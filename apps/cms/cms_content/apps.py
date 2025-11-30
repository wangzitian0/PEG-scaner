"""CMS Content app configuration."""

from django.apps import AppConfig


class CmsContentConfig(AppConfig):
    """Configuration for the CMS Content app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cms_content'
    verbose_name = 'CMS Content'

