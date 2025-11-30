"""
Create a test data batch.

Usage:
    python manage.py create_batch --source yfinance --type company --data '[{"ticker":"AAPL","name":"Apple"}]'
"""

import json

from django.core.management.base import BaseCommand

from pipeline.services import pipeline_service


class Command(BaseCommand):
    help = 'Create a data batch for testing'
    
    def add_arguments(self, parser):
        parser.add_argument('--source', required=True, help='Data source name')
        parser.add_argument('--type', required=True, help='Data type: company/quote/earnings/news')
        parser.add_argument('--data', required=True, help='JSON array of records')
    
    def handle(self, *args, **options):
        source = options['source']
        data_type = options['type']
        
        try:
            raw_data = json.loads(options['data'])
        except json.JSONDecodeError as e:
            self.stderr.write(f"Invalid JSON: {e}")
            return
        
        batch = pipeline_service.create_batch(
            source=source,
            data_type=data_type,
            raw_data=raw_data,
        )
        
        self.stdout.write(self.style.SUCCESS(
            f"Created batch: {batch.batch_id} ({batch.record_count} records)"
        ))

