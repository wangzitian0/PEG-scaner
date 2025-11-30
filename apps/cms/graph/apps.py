"""Graph app configuration."""

from django.apps import AppConfig


class GraphConfig(AppConfig):
    """Configuration for the Graph app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'graph'
    verbose_name = 'Stock Knowledge Graph'
    
    def ready(self):
        """Initialize neo4j connection when app is ready."""
        from django.conf import settings
        from neomodel import config as neo_config
        
        # Set up neomodel connection
        neo_config.DATABASE_URL = settings.NEOMODEL_NEO4J_BOLT_URL

