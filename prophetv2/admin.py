from django.contrib import admin
from .models import Profile#, TestStockInfo
from import_export.admin import ImportExportModelAdmin
from .models import StockInfo, Stocks, StockOwned
from .resources import StockInfoResource, StockResource

class TestStockInfoAdmin(ImportExportModelAdmin):
    resource_classes = [StockInfoResource]
    exclude = ['id',]
    list_display = ['tradingName', 'stockCode', 'lastPrice', 'roe', 'marketcap','totalRev','pe','yieldPercent','sector','gtiScore','oneYearChange',]


class TestStocks(ImportExportModelAdmin):
    resource_classes = [StockResource]
    exclude = ['id',]
    list_display = ['name', 'ticker', 'risk_level', 'rise',]

admin.site.register(StockInfo, TestStockInfoAdmin)
#  Register your models here.
admin.site.register(Profile)
admin.site.register(Stocks, TestStocks)
admin.site.register(StockOwned)
# admin.site.register(StockInfo)