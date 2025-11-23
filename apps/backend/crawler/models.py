from django.db import models
from django.utils import timezone


class CrawlerJob(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_RUNNING = 'running'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_RUNNING, 'Running'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
    ]

    name = models.CharField(max_length=255, help_text='Human readable job name')
    symbol = models.CharField(max_length=16, help_text='Stock symbol (e.g. AAPL)')
    target_url = models.URLField(blank=True, null=True, help_text='Entry point for the crawler')
    schedule_cron = models.CharField(
        max_length=64,
        blank=True,
        help_text='Cron expression used by the scheduler (optional)',
    )
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    is_active = models.BooleanField(default=True)
    last_run_at = models.DateTimeField(blank=True, null=True)
    last_error = models.TextField(blank=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Crawler Job'
        verbose_name_plural = 'Crawler Jobs'

    def mark_running(self):
        self.status = self.STATUS_RUNNING
        self.last_run_at = timezone.now()
        self.save(update_fields=['status', 'last_run_at', 'updated_at'])

    def mark_completed(self):
        self.status = self.STATUS_COMPLETED
        self.last_run_at = timezone.now()
        self.last_error = ''
        self.save(update_fields=['status', 'last_run_at', 'last_error', 'updated_at'])

    def mark_failed(self, error_message: str):
        self.status = self.STATUS_FAILED
        self.last_run_at = timezone.now()
        self.last_error = error_message[:2000]
        self.save(update_fields=['status', 'last_run_at', 'last_error', 'updated_at'])

    def __str__(self):
        return f'{self.symbol} - {self.name}'
