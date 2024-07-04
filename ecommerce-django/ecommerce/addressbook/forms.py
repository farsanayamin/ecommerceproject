from django import forms
from .models import *

class  UserAddressForm(forms.ModelForm):
    
    class Meta:
        model = UserAddressBook
        fields = (
            'first_name','last_name','phone','email','address_line_1','address_line_2','country','state','city','pincode','order_note'
        )

    def __init__(self, *args, **kwargs):
        super(UserAddressForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = "form-control"