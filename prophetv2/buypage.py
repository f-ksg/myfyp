# views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Stocks, StocksOwned
from .forms import StockForm

def stock_price():
    # Function to calculate stock price
    return 123.45

def my_view(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            stock_name = form.cleaned_data['stockName']
            stock_code = form.cleaned_data['stockCode']
            quantity = form.cleaned_data['quantity']
            stock_price = form.cleaned_data['stockPrice']

            # Calculate the total price
            total_price = quantity * stock_price

            # Check if the account balance is sufficient
            profile = request.user.profile
            if profile.accountBalance < total_price:
                messages.error(request, 'Account has insufficient balance')
                return redirect('purchase_page') # replace with URL name of your purchase page

            # Create a new StocksOwned object and save it to the database
            stock = Stocks.objects.get(ticker=stock_code)
            owned_stock = StocksOwned(owner=profile, stock=stock, quantity=quantity, price=stock_price, total_price=total_price)
            owned_stock.save()

            return redirect('success_page') # replace with URL name of your success page
    else:
        stock = Stocks.objects.get(pk=1)
        stock_price_value = stock_price()
        initial_data = {'stockName': stock.name, 'stockCode': stock.ticker, 'stockPrice': stock_price_value}
        form = StockForm(initial=initial_data)
    return render(request, 'my_template.html', {'form': form})
