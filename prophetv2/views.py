import time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.db.models import Avg, F, FloatField, Sum, Q
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

firsttime = True

def landingpage(request):
    form = SignUpForm()
    context = {
        'form': form
    }
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
            messages.error(request, "Unsuccessful registration. Invalid information or password complexity is low")
    return render(request, 'landingpage.html', context)
    
@login_required
def history_page(request):
    stock_owned = StockOwned.objects.filter(profile=request.user.profile)
    stock_sold = StockSold.objects.filter(profile=request.user.profile)
    profile = request.user.profile
    portfolio_value = sum([own.quantity * own.purchase_price for own in stock_owned])
    portfolio_value += profile.accountbalance
    portfolio_value = str(portfolio_value)

    #print(str(stock_owned))
    print(portfolio_value)

    data = []
    for stock in stock_owned:
        total_sum = round(stock.quantity * stock.purchase_price, 2)
        data.append({
            'stock_name': stock.stock.name,
            'stock_ticker': stock.stock.ticker,
            'quantity': stock.quantity,
            'purchase_price': stock.purchase_price,
            'total_sum': total_sum,
            'purchased_at': stock.purchased_at,
        })



    for stocks in stock_sold:
        sell_total_sum = round(stocks.quantity * stocks.sell_price, 2)
        data.append({
            'sell_stock_name': stocks.stock.name,
            'sell_stock_ticker': stocks.stock.ticker,
            'sell_quantity': stocks.quantity,
            'sell_sold_price': stocks.sell_price,
            'sell_total_sum': sell_total_sum,
            'sell_sold_date': stocks.sold_at
        })

    #data.append({'portfolio_value': portfolio_value})

    context = {
        'data': data,
        'portfolio_value':portfolio_value
    }
    
    return render(request, 'history.html', context)
    

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
    
    if profile.risk_level == 1:
        filter_criteria = Q(risk_level=1)
    elif profile.risk_level == 2:
        filter_criteria = Q(risk_level=1) | Q(risk_level=2)
    else:
        filter_criteria = Q(risk_level=1) | Q(risk_level=2) | Q(risk_level=3)

# Query the stocks based on the filter criteria
    stocks = Stocks.objects.filter(filter_criteria)


    #prediction chart
    if request.method == 'GET' and ticker is not None:
        print('---------------------------------------')
        print('im printing in if get')
        print('---------------------------------------')
        
        ticker = request.GET.get('ticker')
        ticker_no_suffix = ticker.replace(".SI","")
        #stock_owned = StockOwned.objects.filter(profile=profile, stock__ticker = ticker_no_suffix).first()
        #print(stock_owned)
        quantity = StockOwned.objects.filter(profile=profile, stock__ticker=ticker_no_suffix).aggregate(Sum('quantity'))['quantity__sum'] or 0
        print(quantity)
        currentChart = predictionchart(ticker)
        currentTicker = yf.Ticker(ticker)
        history = currentTicker.history(period="5d")
        try:
            currentPrice = history["Close"][0]
            currentPrice = "${:,.2f}".format(currentPrice)
        except IndexError as e:
            history = currentTicker.history(period="5d")
            test = currentTicker.fast_info
            currentPrice = test['lastPrice']
            currentPrice = "${:,.2f}".format(currentPrice)
        recommendation = get_recommendation(request, ticker)
        print('---------------------------------------')
        print(recommendation)
        print('---------------------------------------')
        #if lastPrice is None, change history period to 7d
        #if historyperiod = 7d and lastprice is none -> show error
        context = {
            'stocks':stocks,
            'stockowned':stockOwnedObj,
            'currentPrice':currentPrice,
            'form':form,
            'ticker': ticker,
            'sellform': sellform,
            'profile': profile,
            'recommendation': recommendation,
            'quantity': quantity
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
        history = currentTicker.history(period="5d")
        currentPrice = history["Close"][0]
        currentPrice = "${:,.2f}".format(currentPrice)
        
        #if lastPrice is None, change history period to 7d
        #if historyperiod = 7d and lastprice is none -> show error
        context = {
            'stocks':stocks,
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
        stock_sold = StockSold.objects.all()
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
                print('Stock name: ' + str(stock_name))
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
                print('Currently own: ' + str(quantity))
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
                print(stock_owned.stock)
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

                
                stock_sold, created = StockSold.objects.get_or_create(
                profile=profile, stock=stock_owned.stock, sell_price=current_price,
                defaults={'stock_owned': stock_owned, 'quantity': 0})

                stock_sold.stock_owned = stock_owned   
                stock_sold.quantity=units_selling
                #here
                stock_sold.save()

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
    ticker = request.GET.get('ticker')

    if request.method == 'POST' and ticker is not None:   
        ticker = request.GET.get('ticker')
        print('TICKER AFTER RECEIVE ----------------------------')
        print(request.method)
        print(ticker)
        if ticker is None:
            ticker = 'D05.SI'
        print('THEREEEEEEEEEE ----------------------------')
        print(ticker)
        print('THEREEEEEEEEEE ----------------------------')
        currentChart = {}
        tempchart = predictionchart(ticker)
        currentChart.update(tempchart)
        articles = getnews(ticker)
        #top 5 owned based on profile (top_5_stocks)
        #example 'top_5_stocks': ['Sembcorp Marine', 'UOL', 'CapLand IntCom T', 'DBS', 'OCBC Bank']
        top5owned = get_top_5_owned_stocks(request)
        currentChart.update(top5owned)
        #----top 5 owned based on profile end --------
        #top 5 based on ALL stocks (top_5_current_stocks)
        top5all = get_top_5_current_stocks(request)
        
        # print('####################################')
        #print(top5all)
        # print('####################################')
        # currentChart.update(top5all)
        #-----top 5 based on all stocks end--------------
        currentChart.update(top5all)

        top5type = request.GET.get('top_5_type')
        print(top5type)
        if top5type is None:
            top5type = 'profile'
        top_5_type = {'top_5_type' : top5type}

        currentChart.update(top_5_type)

        currentChart.update({'articles':articles[:20]})
        #print(currentChart)
        return render(request, 'base.html', currentChart)
    
    else:
        print(request.method)
        print('------default type here-------------------------')
        ticker = request.GET.get('ticker')
        print('TICKER AFTER RECEIVE ----------------------------')
        print(ticker)
        if ticker is None:
            ticker = 'D05.SI'
        print('TICKER AFTER IF ----------------------------')
        print(ticker)
        currentChart = {}
        tempchart = predictionchart(ticker)
        currentChart.update(tempchart)
        articles = getnews(ticker)
        #top 5 owned based on profile (top_5_stocks)
        #example 'top_5_stocks': ['Sembcorp Marine', 'UOL', 'CapLand IntCom T', 'DBS', 'OCBC Bank']
        top5owned = get_top_5_owned_stocks(request)
        currentChart.update(top5owned)
        #----top 5 owned based on profile end --------
        #top 5 based on ALL stocks (top_5_current_stocks)
        top5all = get_top_5_current_stocks(request)
        
        # print('####################################')
        #print(top5all)
        # print('####################################')
        # currentChart.update(top5all)
        #-----top 5 based on all stocks end--------------
        currentChart.update(top5all)

        top5type = request.GET.get('top_5_type')
        print(top5type)
        if top5type is None:
            top5type = 'profile'
        top_5_type = {'top_5_type' : top5type}

        currentChart.update(top_5_type)

        currentChart.update({'articles':articles[:20]})
        #print(currentChart)
        return render(request, 'base.html', currentChart)
    
    #return render(request, 'base.html', currentChart)

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
    #ticker = request.GET.get('ticker')
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

def predictionchart_ajax(request):
    ticker = request.GET.get('ticker')
    print(ticker)
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
    fig = px.line()
    fig.add_scatter(x=before['Date'], y=before['Price'], mode='lines', name='Past years data')
    fig.add_scatter(x=after['Date'], y=after['Price'], mode='lines', name='Future predicted data')
    fig.update_layout(title = ticker + ' share price', yaxis_title = 'Stock Price (SGD)')
    predictionchart = {
        'predictionchart': fig.to_html()
        }
    #print(predictionchart)
    try:
        predictionchart
    except AttributeError as e:
        print('perdiction chart error')
    return JsonResponse({
        'predictionchart': fig.to_html()
    })
    #return render(request, 'predictionchart_ajax.html', predictionchart)
    
        

#get google news about articles
def getnews(ticker):
    google_news = GNews()
    #google_news.country = 'Singapore'
    newstring = 'SGX:' + ticker
    newstring = newstring.replace(".SI", "")
    print(newstring)
    articles = google_news.get_news(newstring)
    return articles


@login_required
def settings_page(request):
    passwordchangeform = PasswordChangeForm(user=request.user)
    usernamechangeform = UsernameChangeForm()
    emailchangeform = EmailChangeForm()
    risklevelchangeform = RiskControlChangeForm()
    profile = request.user.profile

    context = {
        'passwordchangeform': passwordchangeform,
        'usernamechangeform': usernamechangeform,
        'emailchangeform': emailchangeform,
        'risklevelchangeform': risklevelchangeform,
        'profile':profile
    }

    if request.method == 'POST':
        print('----------------------------------')
        print(request.POST)
        print('----------------------------------')
        if 'username1' in request.POST:
            usernamechangeform = UsernameChangeForm(request.POST, instance=request.user)
            if usernamechangeform.is_valid():
                usernamechangeform.save()
                messages.success(request, f'Successfully changed username!')
                return redirect('/settings/')
            else:
                messages.error(request, f'Failed to change username')
                usernamechangeform = UsernameChangeForm(instance=request.user)

        elif 'email1' in request.POST:
            emailchangeform = EmailChangeForm(request.POST, instance = request.user)
            if emailchangeform.is_valid():
                emailchangeform.save()
                messages.success(request, f'Successfully changed email!')
                return redirect('/settings/')
            else:
                emailchangeform = EmailChangeForm(user=request.user)
                messages.error(request, f'Failed to change email')

        elif 'password1' in request.POST:
            passwordchangeform = PasswordChangeForm(request.POST, instance =request.user)
            if passwordchangeform.is_valid():
                passwordchangeform.save()
                messages.success(request, f'Successfully changed password!')
                return redirect('/settings/')
            else:
                passwordchangeform = PasswordChangeForm(user=request.user)
                messages.error(request, f'Failed to change password')

        elif 'risk' in request.POST:
            # print('--------------hey----------------')
            # print(request.POST)
            # print('------------hey-----------------')
            risklevelchangeform = RiskControlChangeForm(request.POST, instance = profile)
            if risklevelchangeform.is_valid():
                # print('----------------------------------')
                # print('---------form valid --------------')
                # print('----------------------------------')
                risklevelchangeform.save()
                messages.success(request, f'Successfully changed risk level!')
                return redirect('/settings/')
            else:
                # print('----------------------------------')
                # print('formis invalid')
                # print('----------------------------------')
                risklevelchangeform = RiskControlChangeForm(instance=profile)
                messages.error(request, f'Failed to change risk level')

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

    for stock in Stocks.objects.all():
        # Check if the risk level is 0
        if stock.risk_level == 0:
            print(stock.name)
            # If it is, delete the object
            stock.delete()
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
        history = stockCode.history(period="5d")
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
    return JsonResponse({'price': price,
                         'stock_ticker':stock_ticker})



def create_stocks_from_stock_info(request):
    stock_infos = StockInfo.objects.all()
    for stock_info in stock_infos:
        stock, created = Stocks.objects.get_or_create(
            name=stock_info.tradingName,
            ticker=stock_info.stockCode,
            defaults={'risk_level': 1}
        )
        if created:
            print(f'Stocks object created: {stock}')
        else:
            print(f'Stocks object already exists: {stock}')
    return redirect('home')

def generate_rise(request):
    errorstocks = []
    errorlocalize = []
    errorindex = []
    for stock in Stocks.objects.all():
        print('-------------------------')
        print(stock.name)
        print(stock.ticker)
        print('-------------------------')
        ticker = stock.ticker
        start_date = (datetime.now()-relativedelta(years=10)).date()
        current_date = datetime.now().date()
        df = yf.download(ticker+'.SI', start=start_date, end=current_date)
        try:
            df.index = df.index.tz_localize(None)
            df = df.reset_index()
        except AttributeError as e:
            print('error in index.tz_localize')
            errorlocalize.append(stock.name)
            continue
        
        input = pd.DataFrame(columns=['ds', 'y'])
        input[['ds', 'y']] = df[['Date', 'Adj Close']]
        m = Prophet(daily_seasonality=True)
        m.add_country_holidays(country_name='SG')
        try:
            m.fit(input)
        except ValueError as e:
            print('an error value error')
            errorstocks.append(stock.name)
            continue
        future = m.make_future_dataframe(periods=365)
        forecast = m.predict(future)
        forecast_renamed = forecast[["ds", "yhat"]]
        forecast_renamed = forecast_renamed.rename(columns={"ds": "Date","yhat": "Price"})
        forecast_renamed["Date"] = forecast_renamed["Date"].dt.date
        after = forecast_renamed[forecast_renamed['Date'] >= current_date]
        before = forecast_renamed[forecast_renamed['Date'] < current_date]

        #comparing first and last row of after
        try:
            rise = after['Price'].iloc[0] < after['Price'].iloc[-1]
        except IndexError as e:
            print('an error indexing price')
            errorindex.append(stock.name)
            continue

        #print(stock.name)
        print(rise)
        print('-------------------------')

        stock.rise = rise
        stock.save()


    print('Rise has been calculated for all stocks')
    print('-------------------------')
    print('error in fit')
    print(errorstocks)
    print('-------------------------')
    print('#########################')
    print('error in localize')
    print(errorlocalize)
    print('#########################')
    print('*************************')
    print('error in index')
    print(errorindex)
    print('*************************')

    return render(request, 'generate_rise.html')

def delete_stocks(request):
    # Define the list of names to delete
    delete_names = ['Cromwell Reit SGD', '8Telecom', 'Camsing Hc', 'Inch Kenneth', 'Lonza', 'Murata Yen1k', 'Sanli Env', 'Tosei', 'Universal Res', 'KrisEnergy', 'RHT HealthTrust', 'Magnus Energy', 'Maruwa Yen1k', 'Nomura Yen1k']

    # Loop through each stock object with a name in the delete_names list
    for stock in Stocks.objects.filter(name__in=delete_names):
        # Delete the stock object
        print(stock)
        stock.delete()

    # Redirect to the homepage
    return redirect('home')

def get_top_5_owned_stocks(request):
    # Get the profile of the current user
    profile = Profile.objects.get(user=request.user)

    # Get a queryset of all StockOwned objects for the current user's profile
    stock_owned = StockOwned.objects.filter(profile=profile)

    # Create a dictionary to store each stock name and its corresponding one year change value
    stocks_dict = {}

    # Loop through each stock owned
    for stock in stock_owned:
        # Get the corresponding Stocks object
        try:
            stocks_obj = StockInfo.objects.get(tradingName=stock.stock.name)
            # print('----------------------------------------')
            # print(stock.stock.name)
            # print('----------------------------------------')
        except Stocks.DoesNotExist:
            continue

        # Add the stock name and its one year change to the dictionary
        stocks_dict[stock.stock.name] = stocks_obj.oneYearChange
        # print('----------------------------------------')
        # print(stocks_dict)
        # print('----------------------------------------')

    #delete key if value is none
    for key, value in list(stocks_dict.items()):
        if value is None:
            del stocks_dict[key]

    
    sorted_data = sorted(stocks_dict.items(), key=lambda x: x[1], reverse=True)
    top_5_stocks = [x[0] for x in sorted_data[:5]]
    # print('----------------------------------------')
    # print(top_5_stocks)
    # print('----------------------------------------')

    # Get the top 5 stocks by one year change
    # top_5_stocks = dict(sorted(stocks_dict.items(), key=lambda item: item[1], reverse=True)[:5])
    # print('----------------------------------------')
    # print(top_5_stocks)
    # print('----------------------------------------')
    return {'top_5_stocks': top_5_stocks}
    #return render(request, 'top_5_owned.html', {'top_5_stocks': top_5_stocks})
    #return JsonResponse(top_5_stocks)



def get_top_5_current_stocks(request):
    # Get a queryset of all StockInfo objects
    stock_info = StockInfo.objects.all()

    # Create a dictionary to store each stock name and its corresponding one year change value
    stocks_dict = {}

    # Loop through each stock
    for info in stock_info:
        if info.oneYearChange is not None:
            # Add the stock name and its one year change to the dictionary
            stocks_dict[info.tradingName] = info.oneYearChange

    # Get the top 5 stocks by one year change
    top_5_current_stocks = dict(sorted(stocks_dict.items(), key=lambda item: item[1], reverse=True)[:5])
    # print('----------------------------------------')
    # print(top_5_current_stocks)
    # print('----------------------------------------')

    #print(list(top_5_current_stocks.keys()))
    return {'top_5_current_stocks': list(top_5_current_stocks.keys())}



def get_recommendation(request, ticker):
    ticker_no_suffix = ticker.replace(".SI", "")
    profile = Profile.objects.get(user=request.user)

    stock_info = Stocks.objects.filter(ticker=ticker_no_suffix).first()
    stock_owned = StockOwned.objects.filter(profile = profile, stock__ticker=ticker_no_suffix).first()
    
    if stock_owned and stock_info.rise:
        return 'Hold'
    elif stock_owned and not stock_info.rise:
        return 'Sell'
    elif not stock_owned and stock_info.rise:
        return 'Buy'
    else:
        return 'NA'