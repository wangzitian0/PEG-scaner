import logging

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from crawler.models import CrawlerJob
from crawler.tasks import build_sample_payload, fetch_yfinance_payload
from libs.neo4j_db import upsert_stock_document

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Runs a crawler job and writes the results into Neo4j (demo implementation).'

    def add_arguments(self, parser):
        parser.add_argument('--job-id', type=int, help='Primary key of the crawler job to run')
        parser.add_argument('--symbol', type=str, help='Fallback symbol if job lookup fails')

    def handle(self, *args, **options):
        job = self._get_job(options)
        if not job:
            raise CommandError('Could not resolve crawler job (specify --job-id or --symbol)')

        self.stdout.write(self.style.NOTICE(f'Running crawler job for {job.symbol} ({job.name})'))
        job.mark_running()
        payload = fetch_yfinance_payload(job.symbol) or build_sample_payload(
            job.symbol, metadata=job.metadata or {}
        )
        success = upsert_stock_document(payload)

        if not success:
            error = 'Neo4j is not configured or unreachable'
            job.mark_failed(error)
            raise CommandError(error)

        job.mark_completed()
        self.stdout.write(self.style.SUCCESS(f'Neo4j updated for {job.symbol} at {timezone.now()}'))

    def _get_job(self, options):
        job_id = options.get('job_id')
        symbol = options.get('symbol')

        if job_id:
            try:
                return CrawlerJob.objects.get(pk=job_id)
            except CrawlerJob.DoesNotExist:
                raise CommandError(f'CrawlerJob {job_id} does not exist')

        if symbol:
            job = CrawlerJob.objects.filter(symbol__iexact=symbol).first()
            if job:
                return job
            return CrawlerJob.objects.create(
                name=f'Auto-created job for {symbol.upper()}',
                symbol=symbol.upper(),
                status=CrawlerJob.STATUS_PENDING,
                is_active=True,
            )
        return None
