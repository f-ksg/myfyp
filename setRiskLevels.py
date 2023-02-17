from django.db.models import Avg
from prophetv2.models import StockInfo, Stocks

# dictionaryobj to loop thru
averages = StockInfo.objects.values('sector').annotate(
    avg_roe=Avg('roe'),
    avg_marketcap=Avg('marketcap'),
    avg_total_rev=Avg('totalRev'),
    avg_pe=Avg('pe'),
    avg_yield_percent=Avg('yieldPercent'),
    avg_gti_score=Avg('gtiScore')
).order_by('sector').values('sector', 'avg_roe', 'avg_marketcap', 'avg_total_rev', 'avg_pe', 'avg_yield_percent', 'avg_gti_score')

# dictionary to hold sector's averages
sector_avgs = {}
for sector in averages:
    sector_name = sector['sector']
    sector_avgs[sector_name] = {
        'roe': sector['avg_roe'],
        'marketcap': sector['avg_marketcap'],
        'total_rev': sector['avg_total_rev'],
        'pe': sector['avg_pe'],
        'yield_percent': sector['avg_yield_percent'],
        'gti_score': sector['avg_gti_score'],
    }

# Loop over all stocks and calculate their risk levels
for stock in Stocks.objects.all():
    stock_info = StockInfo.objects.filter(stockCode=stock.ticker).first()
    if stock_info is None:
        # StockInfo not found, set risk level to None
        stock.risk_level = None
        stock.save()
        continue
    # Check if sector has averages available
    sector_name = stock_info.sector
    if sector_name not in sector_avgs:
        stock.risk_level = None
        stock.save()
        continue
    sector_avg = sector_avgs[sector_name]
    risk_level = 0.0
    if stock_info.roe < sector_avg['roe']:
        risk_level += 0.5
    if stock_info.marketcap < sector_avg['marketcap']:
        risk_level += 0.5
    if stock_info.totalRev < sector_avg['total_rev']:
        risk_level += 0.5
    if stock_info.pe > sector_avg['pe']:
        risk_level += 0.5
    if stock_info.yieldPercent < sector_avg['yield_percent']:
        risk_level += 0.5
    if stock_info.gtiScore > sector_avg['gti_score']:
        risk_level += 0.5
    stock.risk_level = round(risk_level)
    stock.save()

