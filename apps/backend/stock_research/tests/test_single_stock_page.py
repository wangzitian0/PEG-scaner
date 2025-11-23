import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from stock_research.generated import single_stock_page_pb2
from stock_research.models import (
    CompanyInfo,
    CompanyValuation,
    FinancialIndicators,
    EarningData,
    Stock,
    KLineData,
)


class SingleStockPageViewTests(TestCase):
    def setUp(self):
        company = CompanyInfo.objects.create(
            symbol='AAPL',
            description='Apple Inc.',
            sector='Technology',
            industry='Consumer Electronics',
        )
        CompanyValuation.objects.create(
            company=company,
            ps_ratio=7.5,
            pe_ratio=28.2,
            pb_ratio=40.1,
        )
        FinancialIndicators.objects.create(
            company=company,
            eps=6.12,
            fcf=90.0,
            current_ratio=1.1,
            roe=0.55,
        )
        EarningData.objects.create(
            company=company,
            fiscal_date_end=datetime.date(2024, 12, 31),
            reported_eps=6.12,
            estimated_eps=6.0,
        )
        self.stock = Stock.objects.create(
            symbol='AAPL',
            name='Apple Inc.',
            exchange='NASDAQ',
            currency='USD',
            company_info=company,
        )
        now = timezone.now()
        KLineData.objects.create(
            stock=self.stock,
            timestamp=now - datetime.timedelta(days=2),
            open=100.0,
            high=110.0,
            low=95.0,
            close=108.0,
            volume=1_000_000,
        )
        KLineData.objects.create(
            stock=self.stock,
            timestamp=now - datetime.timedelta(days=1),
            open=108.0,
            high=115.0,
            low=105.0,
            close=112.0,
            volume=1_500_000,
        )

    def test_returns_protobuf_payload(self):
        url = reverse('single-stock-page')
        response = self.client.get(url, {'symbol': 'AAPL'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/x-protobuf')

        payload = single_stock_page_pb2.SingleStockPageResponse()
        payload.ParseFromString(response.content)

        self.assertEqual(payload.stock.symbol, 'AAPL')
        self.assertEqual(payload.stock.company_info.sector, 'Technology')
        self.assertEqual(len(payload.daily_kline), 2)

    def test_missing_symbol_returns_400(self):
        url = reverse('single-stock-page')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertIn('symbol', response.json()['detail'])

    def test_unknown_symbol_returns_404(self):
        url = reverse('single-stock-page')
        response = self.client.get(url, {'symbol': 'TSLA'})

        self.assertEqual(response.status_code, 404)
