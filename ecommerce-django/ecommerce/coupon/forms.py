from django import forms
from .models import *

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code']

        widgets = {
            'code':forms.TextInput(attrs={'class':'form-control'})
        }