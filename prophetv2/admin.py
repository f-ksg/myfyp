from django.contrib import admin
from .models import Profile#, TestStockInfo
from import_export.admin import ImportExportModelAdmin
from .models import StockInfo, Stocks
from .resources import StockInfoResource

class TestStockInfoAdmin(ImportExportModelAdmin):
    resource_classes = [StockInfoResource]
    exclude = ['id',]
    list_display = ['tradingName', 'stockCode', 'lastPrice', 'roe', 'marketcap','totalRev','pe','yieldPercent','sector','gtiScore','oneYearChange',]
admin.site.register(StockInfo, TestStockInfoAdmin)
#  Register your models here.
admin.site.register(Profile)
admin.site.register(Stocks)
# admin.site.register(StockInfo)