from django.contrib import admin

from .models import CrawlerJob


@admin.register(CrawlerJob)
class CrawlerJobAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'status', 'is_active', 'last_run_at')
    list_filter = ('status', 'is_active')
    search_fields = ('name', 'symbol', 'target_url')
    readonly_fields = ('created_at', 'updated_at', 'last_run_at', 'last_error')
    ordering = ('-updated_at',)
