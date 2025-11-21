from rest_framework import serializers
from .models import Stock, KLineData, CompanyInfo, CompanyValuation, FinancialIndicators, EarningData

class CompanyValuationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyValuation
        fields = '__all__'

class FinancialIndicatorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialIndicators
        fields = '__all__'

class EarningDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EarningData
        fields = '__all__'

class CompanyInfoSerializer(serializers.ModelSerializer):
    valuation = CompanyValuationSerializer(read_only=True)
    indicators = FinancialIndicatorsSerializer(read_only=True)
    earnings = EarningDataSerializer(many=True, read_only=True)

    class Meta:
        model = CompanyInfo
        fields = '__all__'

class KLineDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = KLineData
        fields = '__all__'

class StockSerializer(serializers.ModelSerializer):
    company_info = CompanyInfoSerializer(read_only=True)
    k_lines = KLineDataSerializer(many=True, read_only=True)

    class Meta:
        model = Stock
        fields = '__all__'
