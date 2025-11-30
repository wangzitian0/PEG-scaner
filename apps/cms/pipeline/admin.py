"""
Pipeline Admin - Django models with FSM state machine.
"""

from django.contrib import admin
from django.contrib import messages
from django_fsm import can_proceed
from unfold.admin import ModelAdmin

from .models import DataBatchRecord, CrawlerTaskRecord


@admin.register(DataBatchRecord)
class DataBatchAdmin(ModelAdmin):
    """Admin for DataBatchRecord with FSM transitions."""
    
    list_display = ['batch_id', 'source', 'data_type', 'record_count', 'error_count', 'status', 'created_at']
    list_filter = ['status', 'source', 'data_type', 'created_at']
    search_fields = ['batch_id', 'source']
    readonly_fields = ['batch_id', 'neo4j_uid', 'created_at', 'updated_at', 'reviewed_at']
    
    actions = ['action_start_cleaning', 'action_submit_review', 'action_approve', 'action_commit']
    
    @admin.action(description="Start Cleaning")
    def action_start_cleaning(self, request, queryset):
        for batch in queryset:
            if can_proceed(batch.start_cleaning):
                batch.start_cleaning()
                batch.save()
                messages.success(request, f"Started cleaning: {batch.batch_id}")
            else:
                messages.warning(request, f"Cannot start cleaning: {batch.batch_id} (status={batch.status})")
    
    @admin.action(description="Submit for Review")
    def action_submit_review(self, request, queryset):
        for batch in queryset:
            if can_proceed(batch.submit_for_review):
                batch.submit_for_review()
                batch.save()
                messages.success(request, f"Submitted for review: {batch.batch_id}")
    
    @admin.action(description="Approve")
    def action_approve(self, request, queryset):
        for batch in queryset:
            if can_proceed(batch.approve):
                batch.approve(reviewer=request.user, note="Bulk approved")
                batch.save()
                messages.success(request, f"Approved: {batch.batch_id}")
    
    @admin.action(description="Commit to Neo4j")
    def action_commit(self, request, queryset):
        for batch in queryset:
            if can_proceed(batch.commit):
                batch.commit()
                batch.save()
                messages.success(request, f"Committed: {batch.batch_id}")


@admin.register(CrawlerTaskRecord)
class CrawlerTaskAdmin(ModelAdmin):
    """Admin for CrawlerTaskRecord."""
    
    list_display = ['name', 'source_type', 'status', 'is_active', 'last_run_at']
    list_filter = ['status', 'source_type', 'is_active']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at', 'last_run_at']
