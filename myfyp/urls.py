"""myfyp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from prophetv2 import views
from prophetv2.models import Stocks

urlpatterns = [
    path('', views.landingpage, name = 'landingpage'),
    path('admin/', admin.site.urls),
    path('homepage/', views.home_page, name = 'home'),
    path('history/', views.history_page, name = 'history'),
    path('purchase/', views.purchase_page, name ='purchase'),
    path('chart/', views.chart, name = 'chart'),
    path('predictionchart/', views.predictionchart, name = 'predictionchart'),
    path('settings/', views.settings_page, name = 'settings'),
    path('tradingtips/', views.tradingtips_page, name ='tradingtips'),
    path('signup/', views.signup, name="signup"),
    path('logout/', views.logout_view, name="logout"),
    path('upload/', views.simple_upload, name = 'upload'),
    path('getStockPriceAjax/', views.getStockPriceAjax, name = "getStockPriceAjax"),
    path('buy/', views.buy_stock, name = 'buy'),
    path('setrisklevels/', views.setrisklevels, name='setrisklevels'),
    path("get-stock-price/", views.get_stock_price, name="get_stock_price"),
    path('get_stock_info/', views.get_stock_info, name='get_stock_info'),
    path('get_chart_with_ticker/', views.get_chart_with_ticker, name ="get_chart_with_ticker"),
    path('tutorial_1/', views.tutorial_1, name= 'tutorial_1'),
    path('tutorial_2/', views.tutorial_2, name= 'tutorial_2'),
    path('tutorial_3/', views.tutorial_3, name= 'tutorial_3'),
    path('tutorial_4/', views.tutorial_4, name= 'tutorial_4'),
    path('tutorial_5/', views.tutorial_5, name= 'tutorial_5'),
    path('tutorial_6/', views.tutorial_6, name= 'tutorial_6'),
    path('tutorial_7/', views.tutorial_7, name= 'tutorial_7')
]
# 