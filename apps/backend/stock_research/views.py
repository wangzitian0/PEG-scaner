import logging
import time
from datetime import datetime, time as datetime_time

from django.db import DatabaseError
from django.db.models import Prefetch
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from libs.neo4j_db import fetch_stock_document
from stock_research.generated import ping_pb2, single_stock_page_pb2, stock_pb2
from .models import (
    Stock,
    KLineData,
    CompanyInfo,
    CompanyValuation,
    FinancialIndicators,
    EarningData,
    TrackingRecord,
)
from .serializers import (
    StockSerializer,
    KLineDataSerializer,
    CompanyInfoSerializer,
    CompanyValuationSerializer,
    FinancialIndicatorsSerializer,
    EarningDataSerializer,
    PegStockSerializer,
)


class PingPongView(APIView):
    """Simple health endpoint so infra tests can verify backend availability."""

    def get(self, request, format=None):
        self._record_tracking()
        payload = ping_pb2.PingResponse(
            message="pong",
            agent="pegscanner-backend",
            timestamp_ms=int(time.time() * 1000),
        )
        return HttpResponse(
            payload.SerializeToString(),
            content_type="application/x-protobuf",
        )

    @staticmethod
    def _record_tracking():
        try:

            record = TrackingRecord.objects.create()
            TrackingRecord.objects.filter(pk=record.pk).exists()
        except DatabaseError as exc:
            logging.getLogger(__name__).error('Failed to record tracking entry: %s', exc)


class SingleStockPageView(APIView):
    """Returns the protobuf payload for the single stock page."""

    MAX_KLINES = 30

    def get(self, request, format=None):
        symbol = request.query_params.get('symbol')
        if not symbol:
            return Response(
                {'detail': 'symbol query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        normalized_symbol = symbol.strip().upper()
        stock = (
            Stock.objects.select_related(
                'company_info',
                'company_info__valuation',
                'company_info__indicators',
            )
            .prefetch_related(
                Prefetch(
                    'company_info__earnings',
                    queryset=EarningData.objects.order_by('-fiscal_date_end')[:4],
                    to_attr='prefetched_earnings',
                ),
                Prefetch(
                    'k_lines',
                    queryset=KLineData.objects.order_by('-timestamp')[: self.MAX_KLINES],
                    to_attr='prefetched_k_lines',
                ),
            )
            .filter(symbol__iexact=normalized_symbol)
            .first()
        )

        if not stock:
            return Response(
                {'detail': f'Stock {normalized_symbol} not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        response_payload = single_stock_page_pb2.SingleStockPageResponse()
        response_payload.stock.CopyFrom(self._serialize_stock(stock))
        response_payload.daily_kline.extend(
            self._serialize_kline(entry)
            for entry in getattr(stock, 'prefetched_k_lines', [])
        )
        self._apply_neo4j_payload(response_payload, normalized_symbol)

        return HttpResponse(
            response_payload.SerializeToString(),
            content_type='application/x-protobuf',
        )

    def _serialize_stock(self, stock_model: Stock) -> stock_pb2.Stock:
        stock_message = stock_pb2.Stock(
            symbol=stock_model.symbol,
            name=stock_model.name or '',
            exchange=stock_model.exchange or '',
            currency=stock_model.currency or '',
        )
        company_info_model = stock_model.company_info
        if company_info_model:
            stock_message.company_info.CopyFrom(
                self._serialize_company_info(company_info_model)
            )
        return stock_message

    def _serialize_company_info(self, company_info: CompanyInfo) -> stock_pb2.CompanyInfo:
        info_message = stock_pb2.CompanyInfo(
            symbol=company_info.symbol,
            description=company_info.description or '',
            sector=company_info.sector or '',
            industry=company_info.industry or '',
        )

        valuation_model = self._safe_get_related(company_info, 'valuation')
        if valuation_model:
            info_message.valuation.CopyFrom(
                stock_pb2.CompanyValuation(
                    ps_ratio=valuation_model.ps_ratio or 0.0,
                    pe_ratio=valuation_model.pe_ratio or 0.0,
                    pb_ratio=valuation_model.pb_ratio or 0.0,
                )
            )

        indicators_model = self._safe_get_related(company_info, 'indicators')
        if indicators_model:
            info_message.indicators.CopyFrom(
                stock_pb2.FinancialIndicators(
                    eps=indicators_model.eps or 0.0,
                    fcf=indicators_model.fcf or 0.0,
                    current_ratio=indicators_model.current_ratio or 0.0,
                    roe=indicators_model.roe or 0.0,
                )
            )

        earnings = getattr(
            company_info,
            'prefetched_earnings',
            list(company_info.earnings.all()),
        )
        for earning in earnings:
            info_message.earnings.add(
                fiscal_date_end=self._date_to_epoch_seconds(earning.fiscal_date_end),
                reported_eps=earning.reported_eps or 0.0,
                estimated_eps=earning.estimated_eps or 0.0,
            )
        return info_message

    def _serialize_kline(self, kline: KLineData) -> stock_pb2.KLineData:
        return stock_pb2.KLineData(
            timestamp=self._datetime_to_epoch_seconds(kline.timestamp),
            open=kline.open,
            high=kline.high,
            low=kline.low,
            close=kline.close,
            volume=kline.volume,
        )

    @staticmethod
    def _datetime_to_epoch_seconds(value):
        if timezone.is_naive(value):
            value = timezone.make_aware(value, timezone.utc)
        return int(value.timestamp())

    @staticmethod
    def _date_to_epoch_seconds(value):
        dt = datetime.combine(value, datetime_time.min, tzinfo=timezone.utc)
        return int(dt.timestamp())

    @staticmethod
    def _safe_get_related(instance, attr_name):
        try:
            return getattr(instance, attr_name)
        except (CompanyValuation.DoesNotExist, FinancialIndicators.DoesNotExist):
            return None

    def _apply_neo4j_payload(self, response_payload, symbol: str):
        payload = fetch_stock_document(symbol)
        if not payload:
            return

        stock_data = payload.get('stock') or {}
        if stock_data:
            stock_message = response_payload.stock
            stock_message.name = stock_data.get('name') or stock_message.name
            company_info = self._ensure_company_info(stock_message, symbol)
            company_info.description = stock_data.get('description') or company_info.description
            company_info.sector = stock_data.get('sector') or company_info.sector
            company_info.industry = stock_data.get('industry') or company_info.industry

        kline_data = payload.get('daily_kline') or []
        if kline_data:
            response_payload.ClearField('daily_kline')
            for row in kline_data:
                response_payload.daily_kline.add(
                    timestamp=int(row.get('timestamp', 0)),
                    open=float(row.get('open', 0.0)),
                    high=float(row.get('high', 0.0)),
                    low=float(row.get('low', 0.0)),
                    close=float(row.get('close', 0.0)),
                    volume=int(row.get('volume', 0)),
                )

        news_items = payload.get('news') or []
        if news_items:
            response_payload.ClearField('news')
            for item in news_items:
                news = response_payload.news.add()
                news.title = item.get('title', '')
                news.url = item.get('url', '')
                news.source = item.get('source', '')
                news.published_at = int(item.get('published_at', 0))

    def _ensure_company_info(self, stock_message: stock_pb2.Stock, symbol: str):
        if not stock_message.HasField('company_info'):
            stock_message.company_info.symbol = symbol
        return stock_message.company_info

class PegStockListView(APIView):
    def get(self, request, format=None):
        stocks = Stock.objects.all()
        data = []
        for stock in stocks:
            # Get P/E ratio
            pe_ratio = None
            try:
                pe_ratio = stock.company_info.valuation.pe_ratio
            except CompanyInfo.DoesNotExist:
                pass
            except CompanyValuation.DoesNotExist:
                pass

            # Calculate earnings growth
            earnings_growth = None
            try:
                earnings = stock.company_info.earnings.order_by('-fiscal_date_end')
                if earnings.count() >= 2:
                    latest_eps = earnings[0].reported_eps
                    previous_eps = earnings[1].reported_eps
                    if latest_eps is not None and previous_eps is not None and previous_eps > 0:
                        # Simple YoY growth
                        earnings_growth = (latest_eps - previous_eps) / previous_eps
            except CompanyInfo.DoesNotExist:
                pass

            if pe_ratio is not None and earnings_growth is not None:
                data.append({
                    'symbol': stock.symbol,
                    'name': stock.name,
                    'pe_ratio': pe_ratio,
                    'earnings_growth': earnings_growth,
                })

        serializer = PegStockSerializer(data, many=True)
        return Response(serializer.data)


class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

class KLineDataViewSet(viewsets.ModelViewSet):
    queryset = KLineData.objects.all()
    serializer_class = KLineDataSerializer

class CompanyInfoViewSet(viewsets.ModelViewSet):
    queryset = CompanyInfo.objects.all()
    serializer_class = CompanyInfoSerializer

class CompanyValuationViewSet(viewsets.ModelViewSet):
    queryset = CompanyValuation.objects.all()
    serializer_class = CompanyValuationSerializer

class FinancialIndicatorsViewSet(viewsets.ModelViewSet):
    queryset = FinancialIndicators.objects.all()
    serializer_class = FinancialIndicatorsSerializer

class EarningDataViewSet(viewsets.ModelViewSet):
    queryset = EarningData.objects.all()
    serializer_class = EarningDataSerializer
