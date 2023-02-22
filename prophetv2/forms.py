from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError  
from django.forms.fields import EmailField  
from django.forms.forms import Form  
from django.core.validators import FileExtensionValidator
from .models import StockOwned, StockSold, Profile
from django.forms.widgets import NumberInput


class SignUpForm(UserCreationForm): 
    class Meta: 
        model = User 
        fields = ('username', 'email', 'password1', 'password2')


class UsernameChangeForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    
    class Meta:
        model = User
        fields = ['username']

class EmailChangeForm(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['email']

class RiskControlChangeForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['risklevel']
        
        

    


#before = forms.ModelForm
class BuyStockForm(forms.ModelForm):
    units_buying = forms.DecimalField(min_value=0.1)
    total_price = forms.DecimalField()


    class Meta:
        model = StockOwned
        fields = ['stock', 'quantity', 'purchase_price', 'units_buying', 'total_price']
        widgets = {
             #'stock': forms.TextInput(attrs={'readonly': True}),
             'quantity': forms.TextInput(attrs={'readonly': True}),
             'purchase_price': forms.TextInput(attrs={'readonly': True}),
             'total_price': forms.TextInput(attrs={'readonly': True})
        }

    def clean_price(self):
        purchase_price = self.cleaned_data['purchase_price']
        if purchase_price[0] == '$':
            purchase_price = purchase_price[1:]
        return purchase_price

    def clean_total_price(self):
        total_price = self.cleaned_data['total_price']
        if isinstance(total_price, str) and total_price.startswith('$'):
            total_price = total_price.replace('$', '')
        return total_price

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['stock'].widget.attrs['disabled'] = True
    #     self.fields['quantity'].widget.attrs['disabled'] = True
    #     self.fields['purchase_price'].widget.attrs['disabled'] = True
    #     self.fields['total_price'].widget.attrs['disabled'] = True

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


class SellStockForm(forms.ModelForm):
    quantity = forms.DecimalField(label='Shares Owned', widget=forms.TextInput(attrs={'readonly': True, 'id': 'id_sell_quantity', 'label':'Stock Owned'}))
    sell_price = forms.DecimalField(widget=forms.TextInput(attrs={'readonly': True}))
    units_selling = forms.DecimalField(widget=forms.TextInput())
    total_price = forms.DecimalField(widget=forms.TextInput(attrs={'readonly': True, 'id': 'id_sell_total_price'}))
    
    class Meta:
        model = StockSold
        fields = ['stock_owned']
    
    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        units_selling = cleaned_data.get('units_selling')

        if units_selling is not None and quantity is not None and units_selling > quantity:
            raise forms.ValidationError('Units selling cannot be more than shares owned.')

        return cleaned_data

        