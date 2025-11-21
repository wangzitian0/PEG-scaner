from rest_framework import viewsets
from .models import Stock, KLineData, CompanyInfo, CompanyValuation, FinancialIndicators, EarningData
from .serializers import StockSerializer, KLineDataSerializer, CompanyInfoSerializer, CompanyValuationSerializer, FinancialIndicatorsSerializer, EarningDataSerializer

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
