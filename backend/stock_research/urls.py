from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'stocks', views.StockViewSet)
router.register(r'klines', views.KLineDataViewSet)
router.register(r'company-info', views.CompanyInfoViewSet)
router.register(r'company-valuation', views.CompanyValuationViewSet)
router.register(r'financial-indicators', views.FinancialIndicatorsViewSet)
router.register(r'earning-data', views.EarningDataViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('peg-stocks/', views.PegStockListView.as_view(), name='peg-stock-list'),
    path('ping/', views.PingPongView.as_view(), name='ping'),
]
