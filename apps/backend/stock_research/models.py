from django.conf import settings
from django.db import models

class CompanyInfo(models.Model):
    symbol = models.CharField(max_length=10, primary_key=True, help_text="Stock ticker symbol")
    description = models.TextField(blank=True, null=True, help_text="Brief company description")
    sector = models.CharField(max_length=255, blank=True, null=True, help_text="Industry sector")
    industry = models.CharField(max_length=255, blank=True, null=True, help_text="Specific industry")

    def __str__(self):
        return self.symbol

class CompanyValuation(models.Model):
    company = models.OneToOneField(CompanyInfo, on_delete=models.CASCADE, related_name='valuation')
    ps_ratio = models.FloatField(blank=True, null=True, help_text="Price-to-Sales Ratio")
    pe_ratio = models.FloatField(blank=True, null=True, help_text="Price-to-Earnings Ratio")
    pb_ratio = models.FloatField(blank=True, null=True, help_text="Price-to-Book Ratio")

    def __str__(self):
        return f"{self.company.symbol} Valuation"

class FinancialIndicators(models.Model):
    company = models.OneToOneField(CompanyInfo, on_delete=models.CASCADE, related_name='indicators')
    eps = models.FloatField(blank=True, null=True, help_text="Earnings Per Share")
    fcf = models.FloatField(blank=True, null=True, help_text="Free Cash Flow")
    current_ratio = models.FloatField(blank=True, null=True, help_text="Current Ratio")
    roe = models.FloatField(blank=True, null=True, help_text="Return on Equity")

    def __str__(self):
        return f"{self.company.symbol} Indicators"

class EarningData(models.Model):
    company = models.ForeignKey(CompanyInfo, on_delete=models.CASCADE, related_name='earnings')
    fiscal_date_end = models.DateField(help_text="Fiscal period end date")
    reported_eps = models.FloatField(blank=True, null=True, help_text="Reported EPS")
    estimated_eps = models.FloatField(blank=True, null=True, help_text="Estimated EPS")

    class Meta:
        unique_together = ('company', 'fiscal_date_end')

    def __str__(self):
        return f"{self.company.symbol} Earning for {self.fiscal_date_end}"

class Stock(models.Model):
    symbol = models.CharField(max_length=10, primary_key=True, help_text="Stock ticker symbol")
    name = models.CharField(max_length=255, blank=True, null=True, help_text="Full company name")
    exchange = models.CharField(max_length=50, blank=True, null=True, help_text="Exchange where the stock is traded")
    currency = models.CharField(max_length=10, blank=True, null=True, help_text="Currency of the stock")
    company_info = models.OneToOneField(CompanyInfo, on_delete=models.CASCADE, related_name='stock', blank=True, null=True)

    def __str__(self):
        return self.symbol

class KLineData(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='k_lines')
    timestamp = models.DateTimeField(help_text="Unix timestamp of the data point")
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.BigIntegerField()

    class Meta:
        unique_together = ('stock', 'timestamp')

    def __str__(self):
        return f"{self.stock.symbol} K-line at {self.timestamp}"


class TrackingRecord(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = f"{settings.DB_TABLE_PREFIX}tracking"
        ordering = ['-created_at']
        verbose_name = 'Tracking Record'
        verbose_name_plural = 'Tracking Records'

    def __str__(self):
        return f"TrackingRecord(id={self.pk}, created_at={self.created_at})"
