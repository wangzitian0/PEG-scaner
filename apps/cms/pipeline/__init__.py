"""
Pipeline App - Data workflow management.

Workflow: Crawl → Clean → Review → Commit

- CrawlerTask: Job definitions
- DataBatch: Data batches with status tracking
- Whitelist validation from libs/schema/whitelist/
"""

default_app_config = 'pipeline.apps.PipelineConfig'

