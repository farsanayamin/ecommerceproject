from datetime import datetime, timedelta
from email import message
import uuid
from django.contrib import messages
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from accounts.models import Account
from .forms import *
from store.models import *
from orders.models import Order
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.http import HttpResponse,JsonResponse
from orders.models import *
from offers.models import *
from coupon.models import Coupon
import calendar
from django.db.models.functions import ExtractMonth
from django.db.models import Sum, Q, F
import csv
from django.db.models.functions import TruncDate
import json
from django.core.serializers.json import DjangoJSONEncoder
import requests
from django.db.models.functions import TruncDay,TruncMonth,TruncWeek,TruncYear
from django.db.models import Sum


from django.utils import timezone


def download_sales_report(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

    writer = csv.writer(response)

    # Write header row
    writer.writerow(['Order Number', 'Order Total', 'Order Date', 'User', 'Product Name', 'Quantity', 'Price'])

    # Get all orders within the date range
    start_date_str = request.GET['start_date']
    end_date_str = request.GET['end_date']
    
    try:
        start_date = datetime.strptime(start_date_str, '%B %d, %Y, midnight').date()
    except ValueError:
        start_date = timezone.now().date() - timedelta(days=1)
    
    try:
        end_date = (datetime.strptime(end_date_str, '%B %d, %Y, midnight').date() + timedelta(days=1))
    except ValueError:
        end_date = timezone.now().date() + timedelta(days=1)
    
    orders = Order.objects.filter(created_at__range=(start_date, end_date))

    # Loop through orders
    for order in orders:
        # Get related OrderItems for the current order
        order_items = OrderProduct.objects.filter(order=order)

        # Loop through OrderItems and write rows
        for order_item in order_items:
            writer.writerow([
                order.order_number,
                order.order_total,
                order.created_at.strftime('%Y-%m-%d %H:%M:%S'), 
                order.user.username,  # Assuming 'user' is a ForeignKey in Order model
                order_item.product.product_name,  # Assuming 'product' is a ForeignKey in OrderProduct model
                order_item.quantity,
                order_item.product_price,
            ])

    return response

def admindashboard(request):
    return render(request, 'admindashboard.html')

def decorator(request):
    return render(request, 'decorator.html')
#:::::::::::::::::::::::::::::::::::::::::::::::::::::

@login_required(login_url='login')
def useradmin(request):
    if not request.user.is_admin:
        return redirect('decorator')

    period = request.GET.get('period', 'daily')
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')

    today = datetime.now().date()
    start_date, end_date = None, None

    if period == 'custom' and start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() + timedelta(days=1)
        except ValueError:
            start_date, end_date = today - timedelta(days=1), today + timedelta(days=1)
    else:
        if period == 'weekly':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=7)
        elif period == 'monthly':
            start_date = today.replace(day=1)
            next_month = start_date.replace(day=28) + timedelta(days=4)
            end_date = next_month - timedelta(days=next_month.day - 1)
        elif period == 'yearly':
            start_date = today.replace(month=1, day=1)
            end_date = start_date.replace(year=start_date.year + 1)
        else:  # daily
            start_date = today
            end_date = start_date + timedelta(days=1)

    orders = Order.objects.filter(Q(created_at__gte=start_date) & Q(created_at__lte=end_date))

    if period == 'daily':
        sales = orders.annotate(date=TruncDay('created_at')).values('date').annotate(total_revenue=Sum('order_total'))
    elif period == 'weekly':
        sales = orders.annotate(date=TruncWeek('created_at')).values('date').annotate(total_revenue=Sum('order_total'))
    elif period == 'monthly':
        sales = orders.annotate(date=TruncMonth('created_at')).values('date').annotate(total_revenue=Sum('order_total'))
    elif period == 'yearly':
        sales = orders.annotate(date=TruncYear('created_at')).values('date').annotate(total_revenue=Sum('order_total'))
    else:  # custom
        sales = orders.annotate(date=TruncDay('created_at')).values('date').annotate(total_revenue=Sum('order_total'))

    sales_list = [{'date': sale['date'].strftime('%Y-%m-%d'), 'total_revenue': sale['total_revenue']} for sale in sales]
    sales_json = json.dumps(sales_list, cls=DjangoJSONEncoder)

    context = {
        'orders': orders,
        'sales': sales_json,
        'start_date': start_date.strftime('%Y-%m-%d') if start_date else '',
        'end_date': end_date.strftime('%Y-%m-%d') if end_date else '',
        'period': period,
    }

    return render(request, 'index.html', context)
#=====================================================CUSTOMERS=================================================================

def customers(request):
    items_per_page = 10
    if request.user.is_admin:
        accounts_with_profiles = Account.objects.filter(is_admin=False).select_related('userprofile').order_by('id')
        
        p = Paginator(accounts_with_profiles, items_per_page)
        page = request.GET.get('page')
        customers = p.get_page(page)
 
        context = {
            'customers':customers
        }
        return render(request,'users/customers.html', context)
    else:
        return redirect('decorator')
   #----------------------------------------------------------------------------------------------------------- 

def block_user(request,user_id):
    if request.user.is_admin:
        user = Account.objects.get(id = user_id)
        user.is_active = False
        user.is_blocked = True
        user.save()
        return redirect('customers')
    else:
        return redirect('decorator')
    
# -------------------------------------------------------------------------------------------------------------------


def unblock_user(request,user_id):
    if request.user.is_admin:
        user = Account.objects.get(id = user_id)
        user.is_active = True
        user.is_blocked = False
        user.save()
        return redirect('customers')
    else:
        return redirect('decorator')
    

# =====================================================================Admins====================================================


def admin_list(request):
    items_per_page = 10
    if request.user.is_admin:
        p = Paginator(Account.objects.filter(is_admin = True).order_by('id'), items_per_page)
        page = request.GET.get('page')
        admins = p.get_page(page)        
        context = {
            'admins':admins
        }
        return render(request,'users/admin_list.html', context)
    else:
        return redirect('decorator')
    
    # ---------------------------------------------------------------------------------

def delete_admin(request,user_id):
    if request.user.is_admin:
        user = Account.objects.get(id = user_id)
        user.delete()
        return redirect('admin_list')
    else:
        return redirect('decorator')    
    
# ------------------------------------------------------------------------------------------------

def create_admin(request):
    if request.user.is_admin:
        if request.method == 'POST':
            form  = AdminForm(request.POST)
            if form.is_valid():
                admin = form.save(commit=False)
                admin.is_admin = True
                admin.is_staff = True
                admin.is_active = True
                admin.is_superadmin =True
                admin.is_blocked = False
                admin.save()
                return redirect('admin_list')
        form = AdminForm()
        context = {
            "form":form,
        }
        return render(request, 'users/create_admin.html', context)
    else:
        return redirect('decorator')
    

# =================================================CATEGORIES===========================================================
def categories(request):
    items_per_page = 15
    p = Paginator(Category.objects.all(), items_per_page)
    page = request.GET.get('page')
    categories = p.get_page(page)
    context = {
        'categories':categories
    }
    return render(request,'categories/categories.html',context)

# -----------------------------------------------------------------------------------------------------------

def edit_category(request,cat_id):
    cat = Category.objects.get(id=cat_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance = cat)

        if form.is_valid():
            form.save()
            return redirect('categories')
    
    
    form = CategoryForm(instance=cat)

    context = {
        "form":form
    }
    return render(request, 'categories/category_form.html', context )

# ----------------------------------------------------------------------------------------------------------------

def delete_category(request, cat_id):
    cat = Category.objects.get(id=cat_id)
    cat.delete()
    return redirect('categories')

# -----------------------------------------------------------------------------------------------------------------

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('categories')
    form  = CategoryForm()
    context = {
        'form': form
    }
    return render(request,'categories/category_form.html', context)





# =================================================================================BRANDS=========================================
def brands(request):
    items_per_page = 15
    p = Paginator(Brand.objects.all(), items_per_page)
    page = request.GET.get('page')
    data = p.get_page(page)
    context = {
        'data':data
    }
    return render(request, 'brands/brands.html', context)


# ------------------------------------------------------------------------------------------------------------------

def edit_brand(request,brand_id):
    brand = Brand.objects.get(id=brand_id)
    
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES, instance = brand)

        if form.is_valid():
            form.save()
            return redirect('brands')
    
    
    form = BrandForm(instance=brand)

    context = {
        "form":form
    }
    return render(request, 'brands/brand_form.html', context )

# -----------------------------------------------------------------------------------------------
def delete_brand(request,brand_id):
    brand = Brand.objects.get(id=brand_id)
    brand.delete()
    return redirect('brands')

# ------------------------------------------------------------------------------------------------------

def add_brand(request):
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('brands')
    form = BrandForm()
    context = {
        'form':form,
    }
    return render(request, 'brands/brand_form.html', context)


# ===========================================================PRODUCTS==============================================
def products(request):
    items_per_page = 15
    p = Paginator(Product.objects.all(), items_per_page)
    page = request.GET.get('page')
    data = p.get_page(page)
    context={
        "data": data
    }
    return render(request, 'products/products.html', context)

# ------------------------------------------------------------------------------------------------------------------

def edit_product(request, product_id):

    product = Product.objects.get(pk = product_id)
    images = Images.objects.filter(product = product_id)
    image_form = ImageForm()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance = product)
        images = request.FILES.getlist('Images')

        if form.is_valid():
            for image in images:
                pic = Images.objects.create(
                    product = product,
                    image = image
                )
            form.save()
            
            return redirect('products')

    form = ProductForm(instance = product)

    context = {
        'form':form,
        'image_form':image_form,
        'images':images
    }

    return render(request, 'products/product_form.html',context)


def delete_image(request, image_id):
    image = Images.objects.get(id = image_id)
    product_id = image.product.pk

    url = reverse('edit_product', kwargs={'product_id': product_id})

    image.delete()

    return redirect(url)
  


# --------------------------------------------------------------------------------------------------------

def delete_product(request,product_id):
    product = Product.objects.get(id = product_id)
    product.delete()
    return redirect('products')

# -----------------------------------------------------------------------------------
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        images = request.FILES.getlist('Images')
        if form.is_valid():
            product = form.save()
            for image in images:
                pic = Images.objects.create(
                    product = product,
                    image = image
                )
            return redirect('products')
    form  = ProductForm()
    image_form = ImageForm()
    context = {
        'form':form,
        'image_form':image_form
    }
    return render(request,'products/product_form.html',context)



# =============================================PRODUCT VARIATIONS==================================
def variations(request):
    items_per_page = 15
    p = Paginator(Variation.objects.all(), items_per_page)
    page = request.GET.get('page')
    data = p.get_page(page)
    context={
        "data": data
    }
    
    return render(request,'product_variations/variations.html', context)


# -------------------------------------------------------------------------------------------------

def edit_variation(request, variation_id):
    variation = Variation.objects.get(id = variation_id)

    if request.method == 'POST':
        form = VariationForm(request.POST, instance = variation)

        if form.is_valid():
             
            form.save()
           
            return redirect('variations')

    form = VariationForm(instance=variation)

    context = {
        'form':form
    }

    return render(request, 'product_variations/variation_form.html', context)


# ---------------------------------------------------------------------------------------

def delete_variation(request, variation_id):
    variation = Variation.objects.get(id = variation_id)
    variation.delete()
    return redirect('variations')


# ---------------------------------------------------------------------------------------


def add_variation(request):

    if request.method == 'POST':
        form = VariationForm(request.POST)

        if form.is_valid():
            try:
                form.save()
                return redirect('variations')
            except:
                messages.error(request, "Variation already Exists")
                return redirect('add_varition')
    
    form = VariationForm()

    context = {
        'form': form
    }

    return render(request,'product_variations/variation_form.html', context)




# ============================================================================ SIZES ========================================================================================
def colors_size(request):
    sizes = Size.objects.all().order_by('name')
    colors = Color.objects.all().order_by('name')
    context = {
        'sizes': sizes,
        'colors': colors,
    }
    return render(request, "variation/colors&size.html",context)

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def add_size(request):
    if request.method == 'POST':
        form = SizeForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('colors_size')
        
    form = SizeForm()
    context = {
        "form":form
    }
    return render(request, "variation/size_form.html", context)


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def delete_size(request, size_id):
    size = Size.objects.get(id = size_id)
    size.delete()
    return redirect('colors_size')


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def add_color(request):
    if request.method == 'POST':
        form = ColorForm(request.POST)

        if form.is_valid():
            form.save()
        return redirect('colors_size')
    form = ColorForm()
    context = {
        'form':form
    }
    return render(request,'variation/color_form.html',context)

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def delete_color(request, color_id):
    color = Color.objects.get(id = color_id)
    color.delete()
    return redirect('colors_size')

def authenticate_paypal_client(request):
   # Define the URL for the OAuth 2.0 token endpoint
   url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"

   # Define the headers for the request
   headers = {
       "Accept": "application/json",
       "Accept-Language": "en_US",
   }

   # Define the body for the request
   data = {
       "grant_type": "client_credentials",
   }

   # Define the authentication credentials
   auth = (
       
       "AZ6r1mtec08dDVwbJ_Yc-M9drAV3T50vVfkoMZPI5iaQxn8lcbT06QIaqYnk2HExwEXAjmziGjl-wk9p",
       "EPL9dU0uqxsQMGdaCrc3S_u3LrxdFFejnlOUIPvt6x-EjGFqC82DBdSjOP4RqU8fJf9eoskYTpARlkMh",
   )

  

   # Send the request to the OAuth 2.0 token endpoint
   response = requests.post(url, headers=headers, data=data, auth=auth)

   # If the request was successful, the response will contain an access token
   if response.status_code == 200:
       access_token = response.json()["access_token"]
       return access_token
   else:
       return None



def refund_payment(request, order_id):
 # Authenticate the PayPal client
 access_token = authenticate_paypal_client(request)
 if access_token is None:
    return JsonResponse({"error": "Failed to authenticate PayPal client"}, status=401)

 # Get the order
 order = Order.objects.get(id=order_id)

 # Get the payment ID from the order
 payment_id = order.payment.payment_id

 # Get the authorization
 headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {access_token}',
 }

 request_id = str(uuid.uuid4())

 invoice_id = f"{order_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

 # Issue a refund
 headers['PayPal-Request-Id'] = request_id

 headers['Prefer'] = 'return=representation'
 data = f'{{ "amount": {{ "value": "{order.order_total}", "currency_code": "USD" }}, "invoice_id": "{invoice_id}", "note_to_payer": "Cancelled_Order" }}'
 response = requests.post(f'https://api-m.sandbox.paypal.com/v2/payments/captures/{payment_id}/refund', headers=headers, data=data)
 print(response.json())

 if response.status_code == 201:
    order.is_refunded = True
    order.save()
    return redirect('cancelled_orders')
 else:
    return JsonResponse({"error": "Failed to refund capture"}, status=response.status_code)


def orders(request):
    items_per_page = 15
    p = Paginator(Order.objects.all().order_by('-created_at'), items_per_page)
    page = request.GET.get('page')
    data = p.get_page(page)

    context = {
        'data':data
    }
    return render(request,'orders/orders.html', context)

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------

from .signals import order_shipped_signal

def ship(request, order_id):
  order = Order.objects.get(id = order_id)

  order.status = 'Shipped'
  order.save()
  order_shipped_signal.send(sender=ship, instance=order, request=request)

  return redirect('orders')

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

def order_detail(request, order_id):

    order = Order.objects.get(pk = order_id)
    products = OrderProduct.objects.filter(order = order)
    print(products)
    total_price = order.order_total
    if order.coupon:
        total_price -= order.coupon.discount_price
    subtotal = 0
    for product in products:
        subtotal += product.quantity * product.variation.discounted_price # type: ignore


    context = {
        'order': order,
        'products': products,
        'total_price': total_price,
        'subtotal':subtotal
    }
    return render(request, 'orders/order_detail.html', context)

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def new_orders(request):
    items_per_page = 20
    p = Paginator(Order.objects.filter(status = 'New'), items_per_page)
    page = request.GET.get('page')
    data = p.get_page(page)    
    context = {
        'data': data
    }
    return render(request, 'orders/new_orders.html', context)

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def cancelled_orders(request):
    items_per_page = 15
    p = Paginator(Order.objects.filter(status = 'Cancelled').order_by('-created_at'), items_per_page)
    page = request.GET.get('page')
    data = p.get_page(page)

    context = {
        'data':data
    }
    return render(request, 'orders/cancelled_orders.html', context)

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def restock(request, order_id):
    order = Order.objects.get(id = order_id)
    order_products = OrderProduct.objects.filter(order = order)

    for order_product in order_products:
        product = order_product.variation
        product.quantity += order_product.quantity #type: ignore

        product.save() #type: ignore

    order.restock = True
    order.save()

    return redirect('cancelled_orders')




# =========================================================================== PRODUCT OFFER ==========================================================================================

def product_offer(request):
    items_per_page = 20
    p = Paginator(ProductOffer.objects.all().order_by('-id'), items_per_page)
    page = request.GET.get('page')
    data = p.get_page(page)  
    context = {
        'data': data
    }
    return render(request, 'product_offer/product_offer.html', context)


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def add_product_offer(request):
    if request.method == 'POST':
        form = ProductOfferForm(request.POST)

        if form.is_valid():
            discount = form.cleaned_data['discount_rate']
            order_type = form.cleaned_data['offer_type']
            if discount < 0:
                messages.error(request, "The discount rate should not be negative")
                return redirect('add_product_offer')
            if order_type == 'PERCENT' and discount > 80:
                messages.error(request, "The discount percentage should be less than or equal to 80")
                return redirect('add_product_offer')
            form.save()
            return redirect('product_offer')
    form  = ProductOfferForm()

    context = {
        'form':form
    }

    return render(request, 'product_offer/product_offer_form.html', context)



# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def edit_product_offer(request, product_offer_id):
    productOffer = ProductOffer.objects.get(id = product_offer_id)
    if request.method == 'POST':
        form = ProductOfferForm(request.POST, instance=productOffer)

        if form.is_valid():
            discount = form.cleaned_data['discount_rate']
            order_type = form.cleaned_data['offer_type']
            url = reverse('edit_product_offer', kwargs={'product_offer_id': product_offer_id})
            if discount < 0:
                messages.error(request, "The discount rate should not be negative")
                return redirect(url)
            if order_type == 'PERCENT' and discount > 80:
                messages.error(request, "The discount percentage should be less than or equal to 80")
                return redirect(url)
            form.save()
            return redirect('product_offer')
    form = ProductOfferForm(instance=productOffer)
    context = {
        'form':form
    }

    return render(request, 'product_offer/product_offer_form.html', context)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def delete_product_offer(request, product_offer_id):
    product_offer = ProductOffer.objects.get(id = product_offer_id)
    product_offer.delete()
    return redirect('product_offer')

# ===================================================== CATEGORY OFFER ===============================================================================================================

def category_offer(request):
    items_per_page = 20
    p = Paginator(CategoryOffer.objects.all().order_by('-id'), items_per_page)
    page = request.GET.get('page')
    data = p.get_page(page)  
    context = {
        'data': data
    }
    return render(request, 'category_offer/category_offer.html', context)


# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def add_category_offer(request):
    if request.method == 'POST':
        form = CategoryOfferForm(request.POST)

        if form.is_valid():
            discount = form.cleaned_data['discount_rate']
            order_type = form.cleaned_data['offer_type']
            if discount < 0:
                messages.error(request, "The discount rate should not be negative")
                return redirect('add_category_offer')
            if order_type == 'PERCENT' and discount > 80:
                messages.error(request, "The discount percentage should be less than or equal to 80")
                return redirect('add_category_offer')
            form.save()
            return redirect('category_offer')
    form  = CategoryOfferForm()

    context = {
        'form':form
    }

    return render(request, 'category_offer/category_offer_form.html', context)


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def edit_category_offer(request, category_offer_id):
    catOffer = CategoryOffer.objects.get(id = category_offer_id)
    if request.method == 'POST':
        form = CategoryOfferForm(request.POST, instance=catOffer)

        if form.is_valid():
            discount = form.cleaned_data['discount_rate']
            order_type = form.cleaned_data['offer_type']
            url = reverse('edit_category_offer', kwargs={'category_offer_id': category_offer_id})
            if discount < 0:
                messages.error(request, "The discount rate should not be negative")
                return redirect(url)
            if order_type == 'PERCENT' and discount > 80:
                messages.error(request, "The discount percentage should be less than or equal to 80")
                return redirect(url)
            form.save()
            return redirect('category_offer')
    form = CategoryOfferForm(instance=catOffer)
    context = {
        'form':form
    }

    return render(request, 'category_offer/category_offer_form.html', context)

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def delete_category_offer(request, category_offer_id):
    catOffer =  CategoryOffer.objects.get(id = category_offer_id)

    catOffer.delete()
    return redirect('category_offer')


# ===================================== COUPONS =============================================================================================================================================================================

def coupons(request):
    data = Coupon.objects.all()
    context = {
        'data':data
    }
    return render(request, 'coupons/coupons.html', context)



# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def add_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('coupons')
    form = CouponForm()

    context = {
        'form':form
    }

    return render(request, 'coupons/coupon_form.html',context)

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def edit_coupon(request, coupon_id):
    coupon = Coupon.objects.get(id = coupon_id)

    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            return redirect('coupons')
    form = CouponForm(instance=coupon)
    context = {
        'form':form
    }
    return render(request, 'coupons/coupon_form.html', context)

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def delete_coupon(request, coupon_id):
    coupon = Coupon.objects.get(id = coupon_id)
    coupon.delete()

    return redirect('coupons')


from django.shortcuts import render, redirect
from django.db.models import Q, Sum, Count
from django.utils.timezone import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.functions import TruncDate

import json

@login_required(login_url='login')
def admindashboard(request):
    if request.user.is_admin:
        yesterday = datetime.now() - timedelta(days=1) 
        today = datetime.now() + timedelta(days=1)
        start_date = request.GET.get('start_date', yesterday.strftime('%Y-%m-%d'))
        end_date = request.GET.get('end_date', today.strftime('%Y-%m-%d'))
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        except:
            start_date = datetime.strptime(yesterday.strftime('%Y-%m-%d'), '%Y-%m-%d')
        
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except:
            end_date = datetime.strptime(today.strftime('%Y-%m-%d'), '%Y-%m-%d')
        
        end_date = end_date + timedelta(days=1)

        # Get orders within date range
        orders = Order.objects.filter(Q(created_at__gte=start_date) & Q(created_at__lte=end_date))
        
        # Calculate total sales and order count
        total_sales = orders.aggregate(total_revenue=Sum('order_total'))['total_revenue'] or 0
        total_orders = orders.count()

        # Calculate average order value
        avg_order_value = total_sales / total_orders if total_orders > 0 else 0

        # Get sales by day
        sales = orders.annotate(date=TruncDate('created_at')).values('date').annotate(total_revenue=Sum('order_total'))
        sales_list = [{'date': sale['date'].strftime('%Y-%m-%d'), 'total_revenue': sale['total_revenue']} for sale in sales]
        sales_json = json.dumps(sales_list, cls=DjangoJSONEncoder)

        # New customers
        new_customers = Account.objects.filter(date_joined__range=(start_date, end_date)).count()

        # Top selling products
        #top_products = OrderProduct.objects.filter(order__in=orders).values('product__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]
        #top_products = OrderProduct.objects.filter(order__in=orders).values('product__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]

        # Order status distribution
        order_statuses = orders.values('status').annotate(count=Count('id')).order_by('status')
        order_status_list = [{'status': status['status'], 'count': status['count']} for status in order_statuses]
        order_status_json = json.dumps(order_status_list, cls=DjangoJSONEncoder)

        # Refunded orders
        refunded_orders = orders.filter(is_refunded=True)
        total_refunds = refunded_orders.aggregate(total_refund=Sum('order_total'))['total_refund'] or 0
        refund_count = refunded_orders.count()

        context = {
            'orders': orders,
            'sales': sales_json,
            'total_sales': total_sales,
            'total_orders': total_orders,
            'avg_order_value': avg_order_value,
            'new_customers': new_customers,
            #'top_products': top_products,
            'order_status': order_status_json,
            'total_refunds': total_refunds,
            'refund_count': refund_count,
            'start_date': start_date,
            'end_date': end_date
        }
        return render(request, 'admindashboard.html', context)
    else:
        return redirect('decorator')
