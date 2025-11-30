"""
Pipeline Models - Django ORM with FSM state machine.

Uses django-fsm for workflow state management.
Neo4j models remain in libs/neo4j_models/ for graph operations.
"""

from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition


class DataBatchRecord(models.Model):
    """
    Django model for tracking data batch workflow state.
    
    Uses django-fsm for state transitions.
    Actual data stored in Neo4j DataBatch node.
    """
    
    # Link to Neo4j
    batch_id = models.CharField(max_length=100, unique=True, db_index=True)
    neo4j_uid = models.CharField(max_length=100, blank=True)
    
    # Metadata
    source = models.CharField(max_length=50)
    data_type = models.CharField(max_length=50)
    record_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    
    # FSM State
    status = FSMField(default='raw', protected=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, 
        null=True, related_name='created_batches'
    )
    
    # Review
    reviewer = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviewed_batches'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Data Batch'
        verbose_name_plural = 'Data Batches'
    
    def __str__(self):
        return f"{self.batch_id} ({self.status})"
    
    # ==========================================================================
    # FSM Transitions
    # ==========================================================================
    
    @transition(field=status, source='raw', target='cleaning')
    def start_cleaning(self):
        """Start cleaning process."""
        pass
    
    @transition(field=status, source='cleaning', target='clean')
    def finish_cleaning(self, error_count: int = 0):
        """Finish cleaning, record errors."""
        self.error_count = error_count
    
    @transition(field=status, source='clean', target='reviewing')
    def submit_for_review(self):
        """Submit for review."""
        pass
    
    @transition(field=status, source='reviewing', target='approved')
    def approve(self, reviewer, note: str = ''):
        """Approve batch."""
        self.reviewer = reviewer
        self.reviewed_at = timezone.now()
        self.review_note = note
    
    @transition(field=status, source='reviewing', target='rejected')
    def reject(self, reviewer, note: str):
        """Reject batch."""
        self.reviewer = reviewer
        self.reviewed_at = timezone.now()
        self.review_note = note
    
    @transition(field=status, source='rejected', target='cleaning')
    def retry_cleaning(self):
        """Retry cleaning after rejection."""
        self.error_count = 0
    
    @transition(field=status, source='approved', target='committed')
    def commit(self):
        """Commit to Neo4j."""
        pass


class CrawlerTaskRecord(models.Model):
    """
    Django model for crawler task management.
    """
    
    name = models.CharField(max_length=200)
    source_type = models.CharField(max_length=50)
    target_symbols = models.JSONField(default=list, blank=True)
    schedule_cron = models.CharField(max_length=100, blank=True)
    
    # Status
    status = FSMField(default='pending', protected=True)
    is_active = models.BooleanField(default=True)
    
    # Execution
    last_run_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Crawler Task'
        verbose_name_plural = 'Crawler Tasks'
    
    def __str__(self):
        return f"{self.name} ({self.status})"
    
    # FSM Transitions
    
    @transition(field=status, source='pending', target='running')
    def start(self):
        self.last_run_at = timezone.now()
    
    @transition(field=status, source='running', target='completed')
    def complete(self):
        self.last_error = ''
    
    @transition(field=status, source='running', target='failed')
    def fail(self, error: str):
        self.last_error = error[:1000]
    
    @transition(field=status, source=['completed', 'failed'], target='pending')
    def reset(self):
        pass

