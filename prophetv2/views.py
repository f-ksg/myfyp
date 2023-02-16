from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm  
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm
from .models import Profile, StockInfo
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
import mpld3
from gnews import GNews
from tablib import Dataset

ticker = ""

def landingpage(request):
    if request.method == 'POST':
        # print(request.POST)
        if 'login' in request.POST:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
        elif 'register' in request.POST:
            form = SignUpForm(request.POST) 
            # print(form)
            if form.is_valid(): 
                user = form.save()
                # user.refresh_from_db()
                # user.profile.accountbalance = 30000
                # user.save()
                # print('form is saved')
                
                return redirect('landingpage')
            # context = {'form': form}
            # return render(request, 'signup.html', context) 
    return render(request, 'landingpage.html')
    
@login_required
def history_page(request):
    return render(request, 'history.html')

@login_required
def purchase_page(request):
    currentChart = chart()
    currentTicker = yf.Ticker('D05.SI')
    history = currentTicker.history(period="1d")
    currentPrice = history["Close"][0]
    currentPrice = "${:,.2f}".format(currentPrice)
    currentPrice = {'currentPrice': currentPrice}
    currentChart.update(currentPrice)
    print(currentPrice)
    return render(request, 'purchase.html', currentChart)

@login_required    
def home_page(request):    
    currentChart = chart()
    currentChart.update(predictionchart())
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
    # fig = go.Figure(data=[go.Candlestick(x=data['Date'],
    #             open=data[stockCode+'.Open'],
    #             high=data[stockCode+'.High'],
    #             low=data[stockCode+'.Low'],
    #             close=data[stockCode+'.Close'])])
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
    fightml = {'chart': fig.to_html()}
    # if context:
    #     fightml.update(context)    
    return fightml
    


def predictionchart():
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
    context = {'predictionchart': fig.to_html()}
    return context

def getnews():
    google_news = GNews()
    google_news.country = 'Singapore'
    articles = google_news.get_news('DBS')
    return articles

@login_required
def settings_page(request):
    return render(request, 'settings.html')
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

def getStockPrice(stockCode):
    ticker = yf.Ticker(stockCode)
    history = ticker.history(period="1d")
    currentPrice = history["Close"][0]
    currentPrice = "${:,.2f}".format(currentPrice)
    currentPrice = {'currentPrice': currentPrice}
    #returns string value
    return currentPrice

def getStockPriceAjax(requests):
    ticker = yf.Ticker('O39.SI')
    history = ticker.history(period="1d")
    currentPrice = history["Close"][0]
    return HttpResponse(currentPrice)

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

def buypage(request):
    currentPrice = getStockPrice('O39.SI')
    return render(request, 'buy.html', currentPrice)

