from dataclasses import fields
from django import forms
from accounts.models import Account
from store.models import *
from category.models import Category
from multiupload.fields import MultiImageField
from offers.models import *
from coupon.models import Coupon

class AdminForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : 'Enter Password',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : 'Confirm Password'
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']


    
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = "Enter First Name"
        self.fields['last_name'].widget.attrs['placeholder'] = "Enter Last Name"
        self.fields['phone_number'].widget.attrs['placeholder'] = "Enter Phone Number"
        self.fields['email'].widget.attrs['placeholder'] = "Enter Email Address"
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = "form-control"

    
    def clean(self):
        cleaned_data = super(AdminForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "Password Does Not Match!"
            )
    





class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ['category_name','cat_image','offer']

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = "form-control"





class BrandForm(forms.ModelForm):

    class Meta:
        model = Brand
        fields = ['brand_name', 'image']
    
    def __init__(self, *args, **kwargs):
        super(BrandForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = "form-control"




class VariationForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = ('product','color','size','image_id','quantity','price','is_active')

    def __init__(self, *args, **kwargs):
        super(VariationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = "form-control"
    

class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = ('product_name','description','image','is_available','brand','category', 'offer', 'is_featured')
    
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = "form-control"



class ImageForm(forms.ModelForm):
    Images = MultiImageField(min_num=0, max_num=100, max_file_size=1024*1024*5)
    

    class Meta:
        model = Images
        exclude = ['image', 'product','title']






class ProductOfferForm(forms.ModelForm):
    class Meta:
        model = ProductOffer
        fields = ['offer_name', 'offer_type', 'discount_rate']


class CategoryOfferForm(forms.ModelForm):
    class Meta:
        model = CategoryOffer
        fields = ['offer_name', 'offer_type', 'discount_rate']





class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_price', 'minimum_amount']



class DateRangeForm(forms.Form):
   start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
   end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))


class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['name', 'code']

    def __init__(self, *args, **kwargs):
        super(ColorForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = "form-control"




class SizeForm(forms.ModelForm):
    class Meta:
        model = Size
        fields = ['name']
    
    def __init__(self, *args, **kwargs):
        super(SizeForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = "form-control"
