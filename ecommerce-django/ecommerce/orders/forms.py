from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'address_line_1', 'address_line_2','country', 'state', 'city', 'pincode', 'order_note']





class RefundForm(forms.Form):
    order_id = forms.CharField(max_length=100, required=True)
    amount = forms.IntegerField(min_value=1, required=True)
