from django import forms
from .models import *
from django.contrib.auth.models import User

class register(forms.ModelForm):
    class Meta:
        model=User
        fields=('username','email','password')

class details(forms.ModelForm):
    class Meta:
        model = UserDetails
        exclude = ('username')
