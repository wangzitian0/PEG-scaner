"""
CMS Content App - Simple content management for the platform.

Provides:
- Content pages (static content, help docs)
- Announcements (system-wide notifications)

Stored in SQLite, not Neo4j (simple relational data).
"""

default_app_config = 'cms_content.apps.CmsContentConfig'

