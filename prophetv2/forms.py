from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError  
from django.forms.fields import EmailField  
from django.forms.forms import Form  
from django.core.validators import FileExtensionValidator
from .models import StockOwned, StockSold


class SignUpForm(UserCreationForm): 
    class Meta: 
        model = User 
        fields = ('username', 'email', 'password1', 'password2')


class BuyStockForm(forms.ModelForm):
    units_buying = forms.FloatField(min_value=0)
    total_price = forms.FloatField(disabled=True)

    class Meta:
        model = StockOwned
        fields = ['stock', 'quantity', 'purchase_price', 'units_buying', 'total_price']
        widgets = {
            'stock': forms.TextInput(attrs={'readonly': True}),
            'quantity': forms.TextInput(attrs={'readonly': True}),
            'purchase_price': forms.TextInput(attrs={'readonly': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stock'].widget.attrs['disabled'] = True
        self.fields['quantity'].widget.attrs['disabled'] = True
        self.fields['purchase_price'].widget.attrs['disabled'] = True

    def clean_units_buying(self):
        units_buying = self.cleaned_data['units_buying']
        if units_buying <= 0:
            raise forms.ValidationError("Units buying should be greater than 0.")
        return units_buying

    def clean(self):
        cleaned_data = super().clean()
        stock = cleaned_data.get('stock')
        purchase_price = cleaned_data.get('purchase_price')
        units_buying = cleaned_data.get('units_buying')

        if stock and purchase_price and units_buying:
            total_price = round(purchase_price * units_buying, 2)
            cleaned_data['total_price'] = total_price

        return cleaned_data

    def save(self, commit=True):
        stock_owned = super().save(commit=False)
        stock_owned.quantity = self.cleaned_data['units_buying']
        stock_owned.purchase_price = self.cleaned_data['purchase_price']
        if commit:
            stock_owned.save()
        return stock_owned






class SellForm(forms.ModelForm):
    class Meta:
        model = StockSold
        fields = ['stock', 'quantity', 'sell_price']
