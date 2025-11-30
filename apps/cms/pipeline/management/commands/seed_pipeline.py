"""
Seed sample data for pipeline testing.

Usage:
    python manage.py seed_pipeline
"""

from django.core.management.base import BaseCommand

from libs.neo4j_models import CrawlerTask, DataSource


SAMPLE_SOURCES = [
    {'name': 'yfinance', 'source_type': 'api', 'base_url': 'https://finance.yahoo.com'},
    {'name': 'sec_edgar', 'source_type': 'crawler', 'base_url': 'https://www.sec.gov'},
]

SAMPLE_TASKS = [
    {'name': 'SP500 Daily Quotes', 'source_type': 'yfinance', 'status': 'pending'},
    {'name': 'SEC Quarterly Filings', 'source_type': 'sec_edgar', 'status': 'pending'},
]


class Command(BaseCommand):
    help = 'Seed sample pipeline data'
    
    def handle(self, *args, **options):
        self.stdout.write('Seeding pipeline data...')
        
        # Data sources
        for src in SAMPLE_SOURCES:
            try:
                DataSource.nodes.get(name=src['name'])
                self.stdout.write(f"  ✓ DataSource exists: {src['name']}")
            except DataSource.DoesNotExist:
                ds = DataSource(**src)
                ds.save()
                self.stdout.write(f"  ✓ Created DataSource: {src['name']}")
        
        # Crawler tasks
        for task in SAMPLE_TASKS:
            try:
                existing = CrawlerTask.nodes.filter(name=task['name']).first()
                if existing:
                    self.stdout.write(f"  ✓ CrawlerTask exists: {task['name']}")
                    continue
            except:
                pass
            
            ct = CrawlerTask(**task)
            ct.save()
            self.stdout.write(f"  ✓ Created CrawlerTask: {task['name']}")
        
        self.stdout.write(self.style.SUCCESS('Done!'))

