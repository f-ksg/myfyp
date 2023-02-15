from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import StockInfo

class StockInfoResource(resources.ModelResource):
    #tradingName = fields.Field(column_name='tradingName', attribute='tradingName',widget=ForeignKeyWidget(TestStockInfo, 'tradingName'))
    class Meta:
        model = StockInfo
        import_id_fields = ['tradingName',]
        exclude = ('id',)
        fields = ('tradingName', 'stockCode', 'lastPrice', 'roe', 'marketcap','totalRev','pe','yieldPercent','sector','gtiScore','oneYearChange',)
