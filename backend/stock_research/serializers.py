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

class PegStockSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=10)
    name = serializers.CharField(max_length=255)
    pe_ratio = serializers.FloatField()
    earnings_growth = serializers.FloatField()
    peg_ratio = serializers.SerializerMethodField()

    def get_peg_ratio(self, obj):
        if obj.get('pe_ratio') is not None and obj.get('earnings_growth') is not None:
            if obj['earnings_growth'] > 0:
                return obj['pe_ratio'] / (obj['earnings_growth'] * 100) # Assuming growth is a percentage
        return None
