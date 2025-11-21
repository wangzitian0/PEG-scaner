import time

from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from stock_research.generated import ping_pb2
from .models import (
    Stock,
    KLineData,
    CompanyInfo,
    CompanyValuation,
    FinancialIndicators,
    EarningData,
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
        payload = ping_pb2.PingResponse(
            message="pong",
            agent="pegscanner-backend",
            timestamp_ms=int(time.time() * 1000),
        )
        return HttpResponse(
            payload.SerializeToString(),
            content_type="application/x-protobuf",
        )

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
