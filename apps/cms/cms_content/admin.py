"""
Admin configuration for CMS Content models.

Uses django-unfold for modern admin UI.
"""

from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Announcement, ContentPage


@admin.register(ContentPage)
class ContentPageAdmin(ModelAdmin):
    """Admin for ContentPage model."""
    
    list_display = ['title', 'slug', 'is_published', 'updated_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'slug', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'published_at']
    
    fieldsets = [
        (None, {
            'fields': ['title', 'slug', 'content', 'is_published'],
        }),
        ('SEO', {
            'fields': ['meta_title', 'meta_description'],
            'classes': ['collapse'],
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at', 'published_at'],
            'classes': ['collapse'],
        }),
    ]


@admin.register(Announcement)
class AnnouncementAdmin(ModelAdmin):
    """Admin for Announcement model."""
    
    list_display = ['title', 'level', 'is_active', 'start_date', 'end_date']
    list_filter = ['level', 'is_active', 'start_date']
    search_fields = ['title', 'message']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        (None, {
            'fields': ['title', 'message', 'level'],
        }),
        ('Display Settings', {
            'fields': ['is_active', 'is_dismissible', 'show_on_pages'],
        }),
        ('Scheduling', {
            'fields': ['start_date', 'end_date'],
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse'],
        }),
    ]

