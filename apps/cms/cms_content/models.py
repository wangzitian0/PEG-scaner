"""
CMS Content Models - Django ORM models for content management.

These are stored in SQLite, providing simple CMS functionality.
"""

from django.db import models
from django.utils import timezone


class ContentPage(models.Model):
    """
    Static content pages (help docs, about, etc.).
    """
    
    slug = models.SlugField(unique=True, help_text="URL-friendly identifier")
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Markdown or HTML content")
    
    # Metadata
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Content Page"
        verbose_name_plural = "Content Pages"
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class Announcement(models.Model):
    """
    System-wide announcements and notifications.
    """
    
    LEVEL_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('success', 'Success'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='info')
    
    # Display settings
    is_active = models.BooleanField(default=True)
    is_dismissible = models.BooleanField(default=True)
    show_on_pages = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated list of page paths, or empty for all pages"
    )
    
    # Scheduling
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = "Announcement"
        verbose_name_plural = "Announcements"
    
    def __str__(self):
        return f"[{self.level}] {self.title}"
    
    @property
    def is_visible(self) -> bool:
        """Check if announcement should be displayed now."""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        return True

