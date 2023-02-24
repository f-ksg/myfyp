from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import StockInfo, Stocks

class StockInfoResource(resources.ModelResource):
    #tradingName = fields.Field(column_name='tradingName', attribute='tradingName',widget=ForeignKeyWidget(TestStockInfo, 'tradingName'))
    class Meta:
        model = StockInfo
        import_id_fields = ['tradingName',]
        exclude = ('id',)
        fields = ('tradingName', 'stockCode', 'lastPrice', 'roe', 'marketcap','totalRev','pe','yieldPercent','sector','gtiScore','oneYearChange',)

class StockResource(resources.ModelResource):
    class Meta:
        model = Stocks
        import_id_fields = ['tradingName']
        exclude = ('id',)
        fields = ('name', 'ticker', 'risk_level', 'rise',)