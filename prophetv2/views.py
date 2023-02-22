import time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.db.models import Avg
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm  
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import Template, Context
from django.template.loader import render_to_string
from .forms import EmailChangeForm, RiskControlChangeForm, SellStockForm, SignUpForm, BuyStockForm, UsernameChangeForm
from .models import Profile, StockInfo, Stocks, StockSold, StockOwned, StockOwned
from .resources import StockInfoResource
import yfinance as yf
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from datetime import date, datetime
import matplotlib.pyplot as plt
from prophet.plot import plot_plotly, plot_components_plotly
import plotly.offline
from prophet import Prophet
from dateutil.relativedelta import relativedelta
from gnews import GNews
from tablib import Dataset
import pprint, json, mpld3

firsttime = True

def landingpage(request):
    if request.method == 'POST':
        # print(request.POST)
        if 'login' in request.POST:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and user.profile.tutorialcompletion == True:
                #messages.success(request, 'Logging in!')
                login(request, user)
                return redirect('home')
            elif user is not None and user.profile.tutorialcompletion == False:
                login(request, user)
                return redirect ('/tutorial_1/')
            else:
                messages.error(request, 'Invalid username or password.')

        elif 'register' in request.POST:
            form = SignUpForm(request.POST)
            # print(form)
            if form.is_valid(): 
                user = form.save()
                messages.success(request, 'Account registered')
                return redirect('landingpage')
                
    return render(request, 'landingpage.html')
    
@login_required
def history_page(request):
    stock_owned = StockOwned.objects.filter(profile=request.user.profile)
    print(str(stock_owned))
    data = []
    for stock in stock_owned:
        total_sum = round(stock.quantity * stock.purchase_price, 2)
        data.append({
            'stock_name': stock.stock.name,
            'stock_ticker': stock.stock.ticker,
            'quantity': stock.quantity,
            'purchase_price': stock.purchase_price,
            'total_sum': total_sum,
            'purchased_at': stock.purchased_at
        })
    return render(request, 'history.html', {'data': data})
    

#purchasepage
@login_required
def purchase_page(request):
    global firsttime
    stockObj = Stocks.objects.all()
    stockOwnedObj = StockOwned.objects.all()
    profile = request.user.profile
    #stockPrice = get_stock_price(request)
    ticker = request.GET.get('ticker')
    form = BuyStockForm()
    sellform = SellStockForm()
    # sellform = SellStockForm(instance=StockSold.objects.get())
    

    #prediction chart
    if request.method == 'GET' and ticker is not None:
        print('---------------------------------------')
        print('im printing in if get')
        print('---------------------------------------')
        ticker = request.GET.get('ticker')
        currentChart = predictionchart(ticker)
        currentTicker = yf.Ticker(ticker)
        history = currentTicker.history(period="1d")
        currentPrice = history["Close"][0]
        currentPrice = "${:,.2f}".format(currentPrice)
        #if lastPrice is None, change history period to 7d
        #if historyperiod = 7d and lastprice is none -> show error
        context = {
            'stocks':stockObj,
            'stockowned':stockOwnedObj,
            'currentPrice':currentPrice,
            'form':form,
            'ticker': ticker,
            'sellform': sellform,
            'profile': profile
        }

        context.update(currentChart)
        return render(request, 'purchase.html', context)
    #default prediction chart - dbs05
    elif request.method == 'GET' and ticker is None:
        print('---------------------------------------')
        print('im printing in else -- else nothing')
        print('---------------------------------------')
        currentChart = predictionchart_default()
        currentTicker = yf.Ticker('D05.SI')
        history = currentTicker.history(period="1d")
        currentPrice = history["Close"][0]
        currentPrice = "${:,.2f}".format(currentPrice)
        #if lastPrice is None, change history period to 7d
        #if historyperiod = 7d and lastprice is none -> show error
        context = {
            'stocks':stockObj,
            'stockowned':stockOwnedObj,
            'currentPrice':currentPrice,
            'form':form,
            'sellform': sellform
        }
        context.update(currentChart)
        return render(request, 'purchase.html', context)
    #buy logic
    elif request.method == 'POST':
        print('hola amigo im in post method')
        stocks = Stocks.objects.all()
        stock_owned = StockOwned.objects.all()
        print('form is post')
        form = BuyStockForm(request.POST)
        #print(form)
        if 'buy' in request.POST:
            if form.is_valid():
                print('form is valid')
                # Get the stock object
                stock = Stocks.objects.get(pk=form.cleaned_data['stock'].id)
                # Get the current price of the stock
                current_price = form.cleaned_data['purchase_price']
                print(current_price)
                # Get the units buying
                units_buying = form.cleaned_data['units_buying']
                print(units_buying)
                # Calculate the total price
                total_price = form.cleaned_data['total_price']
                # Check if the user has enough balance
                profile = request.user.profile
                if profile.accountbalance < total_price:
                    messages.error(request, 'Account has insufficient balance')
                    return redirect('/purchase/')
                # Deduct the account balance
                profile.accountbalance -= total_price
                profile.save()
                # Add the stock to the user's stock owned
                stock_owned, created = StockOwned.objects.get_or_create(
                    profile=profile, 
                    stock=stock,
                    purchase_price = current_price
                    
                )

                # Increase the quantity of the stock owned
                stock_owned.quantity += units_buying
                stock_owned.save()
                print('success??')
                print(ticker)
                refreshurl = request.path_info
                refreshurl = refreshurl + '?ticker=' + ticker
                print (refreshurl)
                messages.success(request, f'Successfully purchased {units_buying} units of {stock.name}!')
                return HttpResponseRedirect(refreshurl)
            else:
                print('form is NOT valid')
                print(form.errors)
                form = BuyStockForm()
                refreshurl = request.path_info
                refreshurl = refreshurl + '?ticker=' + ticker
                messages.error(request, f'Purchase failed, please check form.')
                return HttpResponseRedirect(refreshurl)

        elif 'sell' in request.POST:
            sellform = SellStockForm(request.POST)
            profile = request.user.profile
            print('im in sell request.POST')
            if sellform.is_valid():
            #-----------------------------------------------------------------
                # Get the stock object
                stock_name = sellform.cleaned_data['stock_owned'].id
                print('Stock owned: ' + str(stock_name))
                print('-------------------------------------')
                # Get the current price of the stock
                current_price = sellform.cleaned_data['sell_price']
                print('selling price: ' + str(current_price))
                print('-------------------------------------')
                # Get the units selling
                units_selling = sellform.cleaned_data['units_selling']
                print('units selling: ' + str(units_selling))
                print('-------------------------------------')
                # Calculate the total price
                total_price = sellform.cleaned_data['total_price']
                print('total price: ' + str(total_price))
                print('-------------------------------------')
                # Get quantity
                quantity = sellform.cleaned_data['quantity']
                print('quantity: ' + str(quantity))
                print('-------------------------------------')
                # Check if the user has enough stocks to sell
                if quantity < units_selling:
                    messages.error(request, 'Not enough stocks to sell')
                    refreshurl = request.path_info
                    refreshurl = refreshurl + '?ticker=' + ticker
                    return HttpResponseRedirect(refreshurl)

                # Reduce the quantity of the stock owned
                stock_owned = get_object_or_404(StockOwned, pk=stock_name)
                print('-------------------------------------')
                print(stock_owned)
                print('-------------------------------------')
                print(stock_owned.quantity)
                print('-------------------------------------')
                # delete entire obj if qty is the same
                if units_selling == stock_owned.quantity:
                    stock_owned.delete()
                    profile.accountbalance += total_price
                    profile.save()
                    refreshurl = request.path_info
                    refreshurl = refreshurl + '?ticker=' + ticker
                    messages.success(request, f'Successfully sold all units of {stock_owned}!')
                    return HttpResponseRedirect(refreshurl)

                stock_owned.quantity -= units_selling
                stock_owned.save()
                
                # Update account balance after selling the stock
                profile.accountbalance += total_price
                profile.save()

                
                refreshurl = request.path_info
                refreshurl = refreshurl + '?ticker=' + ticker
                messages.success(request, f'Successfully sold {units_selling} units of {stock_owned}!')
                return HttpResponseRedirect(refreshurl)
            else:
                print(sellform.errors)
                sellform = SellStockForm()
                refreshurl = request.path_info
                refreshurl = refreshurl + '?ticker=' + ticker
                messages.error(request, f'Units selling cannot be more than shares owned.')
                return HttpResponseRedirect(refreshurl)
            #---------------------------------------------------
            # if sellform.is_valid():
            #     print('form is valid')
            #     print(sellform)
            #     #do logic here then .save
            # else:
            #     print(form.errors)
            #     #stock
            #     # purchase_price 
            #     # units_buying
            #     sellform = SellStockForm()
            #     refreshurl = request.path_info
            #     refreshurl = refreshurl + '?ticker=' + ticker
            #     messages.error(request, f'Selling failed')
            #     return HttpResponseRedirect(refreshurl)

    
    


    



@login_required    
def home_page(request):    
    currentChart = chart()
    currentChart.update(predictionchart_default())
    articles = getnews()
    currentChart.update({'articles':articles[:20]})
    return render(request, 'base.html', currentChart)

def chart():
    stockCode = 'D05.SI'
    data = yf.download(stockCode, start="2020-01-01", end=date.today()) #period ='30d', interval ='15m', rounding = True
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=data.index,
    open = data['Open'], 
    high=data['High'], 
    low=data['Low'], 
    close=data['Close'], 
    name = 'market data'))
    fig.update_layout(title = stockCode + ' share price', yaxis_title = 'Stock Price (SGD)')
    fig.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
    buttons=list([
    dict(count=15, label='15m', step="minute", stepmode="backward"),
    dict(count=45, label='45m', step="minute", stepmode="backward"),
    dict(count=1, label='1h', step="hour", stepmode="backward"),
    dict(count=6, label='6h', step="hour", stepmode="backward"),
    dict(step="all")
    ])
    )
    )

    chart_div = fig.to_html() 
    return {'chart_div': chart_div}


def get_chart_with_ticker(request):
    if request.method == 'GET' and 'ticker' in request.GET:
        ticker = request.GET.get('ticker') 
        print("---------------------------------")
        print(ticker)
        print(ticker)
        print(ticker)
        print("---------------------------------")
        if ticker is not None and isinstance(ticker, str):
            # print("---------------------------------")
            # print(ticker)
            # print("---------------------------------")
            data = yf.download(ticker, start="2020-01-01", end=date.today()) #  #period ='30d', interval ='15m', rounding = True
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=data.index,
            open = data['Open'], 
            high=data['High'], 
            low=data['Low'], 
            close=data['Close'], 
            name = 'market data'))
            fig.update_layout(title = ticker + ' share price', yaxis_title = 'Stock Price (SGD)')
            fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
            buttons=list([
            dict(count=15, label='15m', step="minute", stepmode="backward"),
            dict(count=45, label='45m', step="minute", stepmode="backward"),
            dict(count=1, label='1h', step="hour", stepmode="backward"),
            dict(count=6, label='6h', step="hour", stepmode="backward"),
            dict(step="all")
            ])
            )
            )
            chart_div = fig.to_html()
            context = {'chart_div': chart_div}
            return render(request, 'get_chart_with_ticker.html', context)
        else:
            return chart()

def predictionchart_default():
    three_yrs_ago = datetime.now() - relativedelta(years=10)
    ticker = "D05.SI"
    start_date = (datetime.now()-relativedelta(years=10)).date()
    current_date = datetime.now().date()
    df = yf.download(ticker, start=start_date, end=current_date)
    df.index = df.index.tz_localize(None)
    df = df.reset_index()
    input = pd.DataFrame(columns=['ds', 'y'])
    input[['ds', 'y']] = df[['Date', 'Adj Close']]
    m = Prophet(daily_seasonality=True)
    m.add_country_holidays(country_name='SG')
    m.fit(input)
    future = m.make_future_dataframe(periods=365)
    forecast = m.predict(future)
    forecast_renamed = forecast[["ds", "yhat"]]
    forecast_renamed = forecast_renamed.rename(columns={"ds": "Date","yhat": "Price"})
    forecast_renamed["Date"] = forecast_renamed["Date"].dt.date
    after = forecast_renamed[forecast_renamed['Date'] >= current_date]
    before = forecast_renamed[forecast_renamed['Date'] < current_date]

    #outputs
    #finding min and max of after
    min = after['Price'].min()
    max = after['Price'].max()

    #comparing first and last row of after
    rise = after['Price'].iloc[0] < after['Price'].iloc[-1]
    forecast_date = forecast_renamed["Date"]
    fig, ax = plt.subplots()
    ax.plot(forecast_date, forecast_renamed["Price"])

    # change colour of line
    mask = forecast_date >= current_date
    # ax.plot(forecast_date[mask], forecast_renamed["Price"][mask], line=dict(color='blue '))
    
    # ax = px.line(forecast_renamed, x='Date', y='Price')
    # fig.show()
    fig = px.line()
    fig.add_scatter(x=before['Date'], y=before['Price'], mode='lines', name='Past years data')
    fig.add_scatter(x=after['Date'], y=after['Price'], mode='lines', name='Future predicted data')
    fig.update_layout(title = ticker + ' share price', yaxis_title = 'Stock Price (SGD)')
    predictionchart = {'predictionchart': fig.to_html()}
    return predictionchart    


def predictionchart(ticker):
    three_yrs_ago = datetime.now() - relativedelta(years=10)
    # ticker = "D05.SI"
    start_date = (datetime.now()-relativedelta(years=10)).date()
    current_date = datetime.now().date()
    df = yf.download(ticker, start=start_date, end=current_date)
    df.index = df.index.tz_localize(None)
    df = df.reset_index()
    input = pd.DataFrame(columns=['ds', 'y'])
    input[['ds', 'y']] = df[['Date', 'Adj Close']]
    m = Prophet(daily_seasonality=True)
    m.add_country_holidays(country_name='SG')
    m.fit(input)
    future = m.make_future_dataframe(periods=365)
    forecast = m.predict(future)
    forecast_renamed = forecast[["ds", "yhat"]]
    forecast_renamed = forecast_renamed.rename(columns={"ds": "Date","yhat": "Price"})
    forecast_renamed["Date"] = forecast_renamed["Date"].dt.date
    after = forecast_renamed[forecast_renamed['Date'] >= current_date]
    before = forecast_renamed[forecast_renamed['Date'] < current_date]

    #outputs
    #finding min and max of after
    min = after['Price'].min()
    max = after['Price'].max()

    #comparing first and last row of after
    rise = after['Price'].iloc[0] < after['Price'].iloc[-1]
    forecast_date = forecast_renamed["Date"]
    fig, ax = plt.subplots()
    ax.plot(forecast_date, forecast_renamed["Price"])

    # change colour of line
    mask = forecast_date >= current_date
    # ax.plot(forecast_date[mask], forecast_renamed["Price"][mask], line=dict(color='blue '))
    
    # ax = px.line(forecast_renamed, x='Date', y='Price')
    # fig.show()
    fig = px.line()
    fig.add_scatter(x=before['Date'], y=before['Price'], mode='lines', name='Past years data')
    fig.add_scatter(x=after['Date'], y=after['Price'], mode='lines', name='Future predicted data')
    fig.update_layout(title = ticker + ' share price', yaxis_title = 'Stock Price (SGD)')
    predictionchart = {
        'predictionchart': fig.to_html()
        }
    return predictionchart

#get google news about articles
def getnews():
    google_news = GNews()
    google_news.country = 'Singapore'
    articles = google_news.get_news('DBS')
    return articles

@login_required
def settings_page(request):
    passwordchangeform = PasswordChangeForm(request)
    usernamechangeform = UsernameChangeForm(request.POST)
    emailchangeform = EmailChangeForm(request.POST)
    risklevelchangeform = RiskControlChangeForm(request.POST)
    print(usernamechangeform)
    context = {
        'passwordchangeform': passwordchangeform,
        'usernamechangeform': usernamechangeform,
        'emailchangeform': emailchangeform,
        'risklevelchangeform': risklevelchangeform
    }
    
    return render(request, 'settings.html', context)
@login_required
def tradingtips_page(request):
    return render(request, 'tradingtips.html')

def signup(request): 
    form = SignUpForm(request.POST) 
    if form.is_valid(): 
        form.save() 
        username = form.cleaned_data.get('username') 
        password = form.cleaned_data.get('password') 
        # user = authenticate(username=username, password=password) 
        # login(request, user) 
        return redirect('landingpage') 
    context = { 
        'form': form 
    } 
    return render(request, 'signup.html', context) 

def userlogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('landingpage')

def update_profile(request, user_id):
    user = User.objects.get(pk=user_id)
    user.profile.accountbalance = 30000
    user.save()

def simple_upload(request):
    if request.method == 'POST':
        person_resource = StockInfoResource()
        dataset = Dataset()
        new_persons = request.FILES['myfile']

        imported_data = dataset.load(new_persons.read().decode('utf-8-sig'), format ='csv')
        # print(imported_data)
        result = person_resource.import_data(dataset, dry_run=True, raise_errors=True)  # Test the data import
        
        if not result.has_errors():
            person_resource.import_data(dataset, dry_run=False)  # Actually import now

    return render(request, 'simple_upload.html')

#buy.html not in use
def buy_stock(request):
    stocks = Stocks.objects.all()
    stock_owned = StockOwned.objects.all()
    print('hey im here')
    if request.method == 'POST':
        print('form is post')
        form = BuyStockForm(request.POST)
        print(form)
        if form.is_valid():
            print('form is valid')
            # Get the stock object
            stock = Stocks.objects.get(pk=form.cleaned_data['stock'].id)
            # Get the current price of the stock
            current_price = form.cleaned_data['purchase_price']
            print(current_price)
            # Get the units buying
            units_buying = form.cleaned_data['quantity']
            print(units_buying)
            # Calculate the total price
            total_price = current_price * units_buying
            # Check if the user has enough balance
            profile = request.user.profile
            if profile.accountbalance < total_price:
                messages.error(request, 'Account has insufficient balance')
                return redirect('/purchase/')
            # Deduct the account balance
            profile.accountbalance -= total_price
            profile.save()
            # Add the stock to the user's stock owned
            stock_owned, created = StockOwned.objects.get_or_create(
                profile=profile, stock=stock,
                defaults={'purchase_price': current_price, 'quantity': 0}
            )
            # Increase the quantity of the stock owned
            stock_owned.quantity += units_buying
            stock_owned.save()
            messages.success(request, f'Successfully purchased {units_buying} units of {stock.name}!')
            return redirect('/purchase/')
    else:
        print('form is NOT valid')
        form = BuyStockForm()
    context = {
        'form': form,
        'stocks': stocks,
        'stock_owned': stock_owned
    }
    print('form is neither valid nor invalid...')
    return render(request, 'purchase.html', context)


def setrisklevels(request):
    # dictionaryobj to loop thru
    averages = StockInfo.objects.values('sector').annotate(avg_roe=Avg('roe'),avg_marketcap=Avg('marketcap'),avg_total_rev=Avg('totalRev'),avg_pe=Avg('pe'),avg_yield_percent=Avg('yieldPercent'),avg_gti_score=Avg('gtiScore')).order_by('sector').values('sector', 'avg_roe', 'avg_marketcap', 'avg_total_rev', 'avg_pe', 'avg_yield_percent', 'avg_gti_score')
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
            stock.risk_level = 0
            stock.save()
            continue
        # Check if sector has averages available
        sector_name = stock_info.sector
        if sector_name not in sector_avgs:
            stock.risk_level = 0
            stock.save()
            continue
        print(stock_info)
        sector_avg = sector_avgs[sector_name]
        risk_level = 0.0
        if stock_info.roe is None or stock_info.roe < sector_avg['roe']:
            risk_level += 0.5

        if stock_info.marketcap is None or stock_info.marketcap < sector_avg['marketcap']:
            risk_level += 0.5

        if stock_info.totalRev is None or stock_info.totalRev < sector_avg['total_rev']:
            risk_level += 0.5

        if stock_info.pe is None or stock_info.pe > sector_avg['pe']:
            risk_level += 0.5

        if stock_info.yieldPercent is None or stock_info.yieldPercent < sector_avg['yield_percent']:
            risk_level += 0.5

        if stock_info.gtiScore is None or stock_info.gtiScore > sector_avg['gti_score']:
            risk_level += 0.5
        
        print(stock_info.roe)
        print(stock_info.marketcap)
        print(stock_info.totalRev)
        print(stock_info.pe)
        print(stock_info.yieldPercent)
        print(stock_info.gtiScore)

        stock.risk_level = round(risk_level)
        stock.save()
    return render(request, 'setrisklevels.html')
    
def getStockPriceAjax(request):
    ticker = yf.Ticker('O39.SI')
    history = ticker.history(period="1d")
    currentPrice = history["Close"][0]
    return HttpResponse(currentPrice)

def getStockPrice(stockCode):
    ticker = yf.Ticker(stockCode)
    history = ticker.history(period="1d")
    currentPrice = history["Close"][0]
    currentPrice = "{:,.2f}".format(currentPrice)
    #currentPrice = {'currentPrice': currentPrice}
    #returns string value
    return currentPrice

def get_stock_price(request):
    if request.method == "POST":
        stock_ticker = request.POST.get("stock_ticker")
        current_price = getStockPrice(stock_ticker)
        return JsonResponse(str(current_price), safe=False)
    else:
        return JsonResponse("0", safe=False)

    

#get stock info in use for returning current price
def get_stock_info(request):
    if request.method == 'GET':
        ticker = request.GET.get('ticker')
        print("---------------------------------")
        print(ticker)
        print("---------------------------------")
        stockCode = yf.Ticker(ticker) #ticker
        history = stockCode.history(period="2d")
        test = stockCode.fast_info
        # print("---------------------------------")
        # print(test['lastPrice'])
        # print("---------------------------------")
        #print(stockCode.info)
        #gets lastPrice based off 1d close
        #WILL FAIL 
        # current_price = history["Close"][0]
        # current_price = "{:,.2f}".format(current_price)
        #another method to get last price
        current_price = test['lastPrice']
        # current_price = "{:, .2f}".format(current_price)
        return JsonResponse({'current_price': current_price})
        

def tutorial_1(request):
    return render(request, 'tutorial_1.html')
def tutorial_2(request):
    return render(request, 'tutorial_2.html')
def tutorial_3(request):
    return render(request, 'tutorial_3.html')
def tutorial_4(request):
    return render(request, 'tutorial_4.html')
def tutorial_5(request):
    return render(request, 'tutorial_5.html')
def tutorial_6(request):
    return render(request, 'tutorial_6.html')
def tutorial_7(request):
    profile = request.user.profile
    profile.tutorialcompletion = True
    profile.save()
    return render(request, 'tutorial_7.html')

def complete_tutorial(request):
    current_user = request.user
    user_profile = current_user.profile
    user_profile.tutorialcompletion = True
    user_profile.save()
    # Return a response
    return redirect(home_page)

def get_stock_quantity(request):
    stock_id = request.GET.get('stock_id')
    stock = get_object_or_404(StockOwned, id=stock_id)
    quantity = stock.quantity
    return JsonResponse({'quantity': quantity})

#get stock name, get ticker from stocks, return 
def get_stock_price_new(request):
    stock_name = request.GET.get('stockname')
    print(stock_name)
    stockname = get_object_or_404(Stocks, name=stock_name)
    print(stockname)
    stock_ticker = stockname.ticker + '.SI'
    print(stock_ticker)
    price = getStockPrice(stock_ticker)
    return JsonResponse({'price': price})