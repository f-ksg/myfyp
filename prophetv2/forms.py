from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError  
from django.forms.fields import EmailField  
from django.forms.forms import Form  
from django.core.validators import FileExtensionValidator
  	
class SignUpForm(UserCreationForm): 
    class Meta: 
        model = User 
        fields = ('username', 'email', 'password1', 'password2')

class BuyForm(forms.Form):
    class Meta:
        model = User
        currentPrice = forms.FloatField()
        unitsOwned = forms.FloatField()
        unitsBuying = forms.FloatField()
        totalPrice = forms.FloatField()