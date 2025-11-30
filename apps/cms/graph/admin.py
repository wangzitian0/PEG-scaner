"""
Django Admin for Neo4j Graph Nodes

Custom admin views for CRUD operations on Neo4j nodes.
Models are imported from libs/neo4j_models/ (SSOT).
"""

from django.contrib import admin, messages
from django.db import models
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from unfold.admin import ModelAdmin

from libs.neo4j_models import (
    Company,
    CrawlerTask,
    DailyQuote,
    DataBatch,
    DataSource,
    EarningsReport,
    NewsArticle,
    Sector,
)


# =============================================================================
# Proxy Models (Django Admin requires ORM models)
# =============================================================================

class CompanyProxy(models.Model):
    class Meta:
        managed = False
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        app_label = 'graph'


class DailyQuoteProxy(models.Model):
    class Meta:
        managed = False
        verbose_name = "Daily Quote"
        verbose_name_plural = "Daily Quotes"
        app_label = 'graph'


class EarningsReportProxy(models.Model):
    class Meta:
        managed = False
        verbose_name = "Earnings Report"
        verbose_name_plural = "Earnings Reports"
        app_label = 'graph'


class NewsArticleProxy(models.Model):
    class Meta:
        managed = False
        verbose_name = "News Article"
        verbose_name_plural = "News Articles"
        app_label = 'graph'


class DataSourceProxy(models.Model):
    class Meta:
        managed = False
        verbose_name = "Data Source"
        verbose_name_plural = "Data Sources"
        app_label = 'graph'


class SectorProxy(models.Model):
    class Meta:
        managed = False
        verbose_name = "Sector"
        verbose_name_plural = "Sectors"
        app_label = 'graph'


# =============================================================================
# Base Neo4j Admin
# =============================================================================

class Neo4jModelAdmin(ModelAdmin):
    """Base admin class for Neo4j nodes."""
    
    neo4j_model = None
    list_display_fields = []
    list_per_page = 50
    
    def get_urls(self):
        urls = super().get_urls()
        model_name = self.model._meta.model_name
        custom_urls = [
            path('', self.admin_site.admin_view(self.changelist_view_neo4j),
                 name=f'graph_{model_name}_changelist'),
        ]
        return custom_urls + urls
    
    def changelist_view_neo4j(self, request: HttpRequest):
        if not self.neo4j_model:
            messages.error(request, "No Neo4j model configured")
            return HttpResponseRedirect(reverse('admin:index'))
        
        page = int(request.GET.get('p', 0))
        try:
            start = page * self.list_per_page
            end = start + self.list_per_page
            nodes = list(self.neo4j_model.nodes.all()[start:end])
            total = len(self.neo4j_model.nodes)
        except Exception as e:
            messages.error(request, f"Neo4j error: {e}")
            nodes, total = [], 0
        
        context = {
            **self.admin_site.each_context(request),
            'title': f'{self.neo4j_model.__name__} List',
            'nodes': nodes,
            'fields': self.list_display_fields,
            'model_name': self.model._meta.model_name,
            'total_count': total,
            'page': page,
            'has_next': (page + 1) * self.list_per_page < total,
            'has_prev': page > 0,
        }
        return render(request, 'admin/graph/neo4j_changelist.html', context)


# =============================================================================
# Registered Admin Classes
# =============================================================================

@admin.register(CompanyProxy)
class CompanyAdmin(Neo4jModelAdmin):
    neo4j_model = Company
    list_display_fields = ['ticker', 'name', 'exchange', 'sector', 'industry']


@admin.register(DailyQuoteProxy)
class DailyQuoteAdmin(Neo4jModelAdmin):
    neo4j_model = DailyQuote
    list_display_fields = ['ticker', 'date', 'close', 'volume']


@admin.register(EarningsReportProxy)
class EarningsReportAdmin(Neo4jModelAdmin):
    neo4j_model = EarningsReport
    list_display_fields = ['ticker', 'fiscal_period', 'eps', 'revenue']


@admin.register(NewsArticleProxy)
class NewsArticleAdmin(Neo4jModelAdmin):
    neo4j_model = NewsArticle
    list_display_fields = ['title', 'source_name', 'published_at']


@admin.register(DataSourceProxy)
class DataSourceAdmin(Neo4jModelAdmin):
    neo4j_model = DataSource
    list_display_fields = ['name', 'source_type', 'is_active']


@admin.register(SectorProxy)
class SectorAdmin(Neo4jModelAdmin):
    neo4j_model = Sector
    list_display_fields = ['name', 'code']
