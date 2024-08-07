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
from django.shortcuts import render, redirect
from django.db.models import Q, Sum, Count
from django.utils.timezone import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.functions import TruncDate
import json
from django.utils import timezone
from django.http import HttpResponse
import csv
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
# Adjust the import to match your app structure
from django.http import HttpResponse
import csv
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
import csv
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q
import csv
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q
from django.utils import timezone
import csv
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import HttpResponse
import csv
from django.shortcuts import render
from django.db.models import Avg, Count, Sum
import json
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum, Q
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
import json
from django.core.serializers.json import DjangoJSONEncoder
import uuid
from datetime import datetime
import requests
from django.http import JsonResponse
from django.shortcuts import redirect
import csv
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta

from .signals import order_shipped_signal

from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse

from .signals import order_shipped_signal

def admindashboard(request):
    if not request.user.is_admin:
        return redirect('decorator')
    
    # Get start_date and end_date from GET parameters
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')


    # Default to last week if no dates are provided
    if not start_date_str or not end_date_str:
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=7)
    else:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    # Convert to timezone-aware datetimes
    start_date = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
    end_date = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))

    # Retrieve total sales for the given date range
    total_sales = Order.objects.filter(created_at__range=(start_date, end_date)).aggregate(total_sales=Sum('order_total'))['total_sales'] or 0

    # Retrieve total orders for the given date range
    total_orders = Order.objects.filter(created_at__range=(start_date, end_date)).count()

    # Retrieve average order value for the given date range
    avg_order_value = Order.objects.filter(created_at__range=(start_date, end_date)).aggregate(avg_order_value=Avg('order_total'))['avg_order_value'] or 0

    # Retrieve new customers count for the given date range
    new_customers = Order.objects.filter(created_at__range=(start_date, end_date), user__date_joined__range=(start_date, end_date)).count()

    # Retrieve total refunds amount and count for the given date range
    total_refunds = Order.objects.filter(created_at__range=(start_date, end_date), status='Cancelled').aggregate(total_refunds=Sum('order_total'))['total_refunds'] or 0
    refund_count = Order.objects.filter(created_at__range=(start_date, end_date), status='Cancelled').count()

    # Retrieve top selling products
    top_products = OrderProduct.objects.filter(order__created_at__range=(start_date, end_date)) \
        .values('product__product_name') \
        .annotate(total_quantity_sold=Sum('quantity')) \
        .order_by('-total_quantity_sold')[:5]
    top_products_data = [{'product_name': product['product__product_name'], 'total_quantity': product['total_quantity_sold']} for product in top_products]

    # Retrieve order status distribution
    order_statuses = ['Cancelled', 'Returned', 'Delivered', 'On the Way']
    order_status_data = Order.objects.filter(created_at__range=(start_date, end_date), status__in=order_statuses) \
        .values('status').annotate(count=Count('id'))
    order_status_data_list = [{'status': item['status'], 'count': item['count']} for item in order_status_data]

    # Retrieve sales data for the given date range
    sales_data = Order.objects.filter(created_at__range=(start_date, end_date)) \
        .values('created_at__date') \
        .annotate(total_revenue=Sum('order_total')) \
        .order_by('created_at__date')
    sales_data_list = [{'date': item['created_at__date'].strftime('%Y-%m-%d'), 'total_revenue': item['total_revenue']} for item in sales_data]

    # Prepare data for JSON serialization
    sales_data_json = json.dumps(sales_data_list)
    order_status_data_json = json.dumps(order_status_data_list)
    top_products_data_json = json.dumps(top_products_data)

    context = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'total_sales': total_sales,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'new_customers': new_customers,
        'total_refunds': total_refunds,
        'refund_count': refund_count,
        'top_products': top_products_data_json,
        'sales': sales_data_json,
        'order_status': order_status_data_json,
    }

    return render(request, 'admindashboard.html', context)


#..........................................
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

    today = timezone.localtime().date()
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

    # Make sure datetime objects are timezone-aware
    start_date = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
    end_date = timezone.make_aware(datetime.combine(end_date, datetime.min.time()))

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
@login_required(login_url='login')
def customers(request):
    if request.user.is_admin:
        items_per_page = 10
        accounts_with_profiles = Account.objects.filter(is_admin=False).select_related('userprofile').order_by('id')
        
        p = Paginator(accounts_with_profiles, items_per_page)
        page = request.GET.get('page')
        customers = p.get_page(page)
 
        context = {
            'customers': customers
        }
        return render(request, 'users/customers.html', context)
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
@login_required(login_url='login')
def categories(request):
    if request.user.is_admin:
        items_per_page = 15
        p = Paginator(Category.objects.all(), items_per_page)
        page = request.GET.get('page')
        categories = p.get_page(page)
        context = {
            'categories': categories
        }
        return render(request, 'categories/categories.html', context)
    else:
        return redirect('decorator')



# -----------------------------------------------------------------------------------------------------------

def edit_category(request, cat_id):
    if request.user.is_admin:
        cat = Category.objects.get(id=cat_id)
        
        if request.method == 'POST':
            form = CategoryForm(request.POST, request.FILES, instance=cat)

            if form.is_valid():
                form.save()
                return redirect('categories')

        form = CategoryForm(instance=cat)

        context = {
            "form": form
        }
        return render(request, 'categories/category_form.html', context)
    else:
        return redirect('decorator')

# ----------------------------------------------------------------------------------------------------------------

def delete_category(request, cat_id):
    if request.user.is_admin:
        cat = Category.objects.get(id=cat_id)
        cat.delete()
        return redirect('categories')
    else:
        return redirect('decorator')

def add_category(request):
    if request.user.is_admin:
        if request.method == 'POST':
            form = CategoryForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('categories')
        form = CategoryForm()
        context = {
            'form': form
        }
        return render(request, 'categories/category_form.html', context)
    else:
        return redirect('decorator')





# =================================================================================BRANDS=========================================
@login_required(login_url='login')
def brands(request):
    if request.user.is_admin:
        items_per_page = 15
        p = Paginator(Brand.objects.all(), items_per_page)
        page = request.GET.get('page')
        data = p.get_page(page)
        context = {
            'data': data
        }
        return render(request, 'brands/brands.html', context)
    else:
        return redirect('decorator')


# ------------------------------------------------------------------------------------------------------------------

def edit_brand(request, brand_id):
    if request.user.is_admin:
        brand = Brand.objects.get(id=brand_id)
        
        if request.method == 'POST':
            form = BrandForm(request.POST, request.FILES, instance=brand)

            if form.is_valid():
                form.save()
                return redirect('brands')

        form = BrandForm(instance=brand)

        context = {
            "form": form
        }
        return render(request, 'brands/brand_form.html', context)
    else:
        return redirect('decorator')

# -----------------------------------------------------------------------------------------------
def delete_brand(request, brand_id):
    if request.user.is_admin:
        brand = Brand.objects.get(id=brand_id)
        brand.delete()
        return redirect('brands')
    else:
        return redirect('decorator')

def add_brand(request):
    if request.user.is_admin:
        if request.method == 'POST':
            form = BrandForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('brands')
        form = BrandForm()
        context = {
            'form': form,
        }
        return render(request, 'brands/brand_form.html', context)
    else:
        return redirect('decorator')


# ===========================================================PRODUCTS==============================================
@login_required(login_url='login')
def products(request):
    if request.user.is_admin:
        items_per_page = 15
        p = Paginator(Product.objects.all(), items_per_page)
        page = request.GET.get('page')
        data = p.get_page(page)
        context = {
            "data": data
        }
        return render(request, 'products/products.html', context)
    else:
        return redirect('decorator')

# ------------------------------------------------------------------------------------------------------------------

@login_required(login_url='login')
def edit_product(request, product_id):
    if request.user.is_admin:
        product = Product.objects.get(pk=product_id)
        images = Images.objects.filter(product=product_id)
        image_form = ImageForm()
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES, instance=product)
            images = request.FILES.getlist('Images')

            if form.is_valid():
                for image in images:
                    Images.objects.create(
                        product=product,
                        image=image
                    )
                form.save()
                return redirect('products')

        form = ProductForm(instance=product)

        context = {
            'form': form,
            'image_form': image_form,
            'images': images
        }

        return render(request, 'products/product_form.html', context)
    else:
        return redirect('decorator')


def delete_image(request, image_id):
    if request.user.is_admin:
        image = Images.objects.get(id=image_id)
        product_id = image.product.pk
        url = reverse('edit_product', kwargs={'product_id': product_id})
        image.delete()
        return redirect(url)
    else:
        return redirect('decorator')

  


# --------------------------------------------------------------------------------------------------------

def delete_product(request, product_id):
    if request.user.is_admin:
        product = Product.objects.get(id=product_id)
        product.delete()
        return redirect('products')
    else:
        return redirect('decorator')

def add_product(request):
    if request.user.is_admin:
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
            images = request.FILES.getlist('Images')
            if form.is_valid():
                product = form.save()
                for image in images:
                    Images.objects.create(
                        product=product,
                        image=image
                    )
                return redirect('products')
        form = ProductForm()
        image_form = ImageForm()
        context = {
            'form': form,
            'image_form': image_form
        }
        return render(request, 'products/product_form.html', context)
    else:
        return redirect('decorator')



# =============================================PRODUCT VARIATIONS==================================
@login_required(login_url='login')
def variations(request):
    if request.user.is_admin:
        items_per_page = 15
        p = Paginator(Variation.objects.all(), items_per_page)
        page = request.GET.get('page')
        data = p.get_page(page)
        context = {
            "data": data
        }
        return render(request, 'product_variations/variations.html', context)
    else:
        return redirect('decorator')

def edit_variation(request, variation_id):
    if request.user.is_admin:
        variation = Variation.objects.get(id=variation_id)
        if request.method == 'POST':
            form = VariationForm(request.POST, instance=variation)
            if form.is_valid():
                form.save()
                return redirect('variations')

        form = VariationForm(instance=variation)
        context = {
            'form': form
        }
        return render(request, 'product_variations/variation_form.html', context)
    else:
        return redirect('decorator')


# ---------------------------------------------------------------------------------------

def delete_variation(request, variation_id):
    if request.user.is_admin:
        variation = Variation.objects.get(id=variation_id)
        variation.delete()
        return redirect('variations')
    else:
        return redirect('decorator')

def add_variation(request):
    if request.user.is_admin:
        if request.method == 'POST':
            form = VariationForm(request.POST)
            if form.is_valid():
                try:
                    form.save()
                    return redirect('variations')
                except:
                    messages.error(request, "Variation already Exists")
                    return redirect('add_variation')
        form = VariationForm()
        context = {
            'form': form
        }
        return render(request, 'product_variations/variation_form.html', context)
    else:
        return redirect('decorator')




# ============================================================================ SIZES ========================================================================================
@login_required(login_url='login')
def colors_size(request):
    if request.user.is_admin:
        sizes = Size.objects.all().order_by('name')
        colors = Color.objects.all().order_by('name')
        context = {
            'sizes': sizes,
            'colors': colors,
        }
        return render(request, "variation/colors_size.html", context)
    else:
        return redirect('decorator')

def add_size(request):
    if request.user.is_admin:
        if request.method == 'POST':
            form = SizeForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('colors_size')
        form = SizeForm()
        context = {
            "form": form
        }
        return render(request, "variation/size_form.html", context)
    else:
        return redirect('decorator')

def delete_size(request, size_id):
    if request.user.is_admin:
        size = Size.objects.get(id=size_id)
        size.delete()
        return redirect('colors_size')
    else:
        return redirect('decorator')

def add_color(request):
    if request.user.is_admin:
        if request.method == 'POST':
            form = ColorForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('colors_size')
        form = ColorForm()
        context = {
            'form': form
        }
        return render(request, 'variation/color_form.html', context)
    else:
        return redirect('decorator')

def delete_color(request, color_id):
    if request.user.is_admin:
        color = Color.objects.get(id=color_id)
        color.delete()
        return redirect('colors_size')
    else:
        return redirect('decorator')

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
    if request.user.is_admin:
        access_token = authenticate_paypal_client(request)
        if access_token is None:
            return JsonResponse({"error": "Failed to authenticate PayPal client"}, status=401)
        order = Order.objects.get(id=order_id)
        payment = order.payment
        if payment.payment_method == "PayPal":
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
            }
            request_id = str(uuid.uuid4())
            invoice_id = f"{order_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            headers['PayPal-Request-Id'] = request_id
            headers['Prefer'] = 'return=representation'
            data = {
                "amount": {
                    "value": f"{order.order_total}",
                    "currency_code": "USD"
                },
                "invoice_id": invoice_id,
                "note_to_payer": "Cancelled_Order"
            }
            response = requests.post(
                f'https://api-m.sandbox.paypal.com/v2/payments/captures/{payment.payment_id}/refund',
                headers=headers,
                json=data
            )
            if response.status_code == 201:
                refund_response = response.json()
                order.is_refunded = True
                order.save()
                user_wallet, created = wallet.objects.get_or_create(user=order.user)
                user_wallet.amount += float(refund_response['amount']['value'])
                user_wallet.save()
                return redirect('cancelled_orders')
            else:
                return JsonResponse({"error": "Failed to refund capture"}, status=response.status_code)
        elif payment.payment_method == "Wallet":
            user_wallet, created = wallet.objects.get_or_create(user=order.user)
            user_wallet.amount += order.order_total
            user_wallet.save()
            order.is_refunded = True
            order.save()
            return redirect('cancelled_orders')
        else:
            return JsonResponse({"error": "Unknown payment method"}, status=400)
    else:
        return redirect('decorator')



@login_required(login_url='login')
def orders(request):
    if request.user.is_admin:
        items_per_page = 15
        p = Paginator(Order.objects.all().order_by('-created_at'), items_per_page)
        page = request.GET.get('page')
        data = p.get_page(page)
        context = {
            'data': data
        }
        return render(request, 'orders/orders.html', context)
    else:
        return redirect('decorator')
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------


def ship_order(request, order_id):
    if request.user.is_admin:
        order = get_object_or_404(Order, id=order_id)
        if order.status == 'New':
            order.status = 'Shipped'
            order.save()
            order_shipped_signal.send(sender=ship_order, instance=order, request=request)
        return redirect('orders')
    else:
        return redirect('decorator')

def update_order_status(request, order_id):
    if request.user.is_admin:
        order = get_object_or_404(Order, id=order_id)
        if order.status == 'Shipped':
            order.status = 'On the Way'
        elif order.status == 'On the Way':
            order.status = 'Delivered'
        order.save()
        return redirect('orders')
    else:
        return redirect('decorator')

def mark_as_delivered(request, order_id):
    if request.user.is_admin:
        order = get_object_or_404(Order, id=order_id)
        if order.status == 'On the Way':
            order.status = 'Delivered'
            order.save()
        return redirect('orders')
    else:
        return redirect('decorator')


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Order detail view
@login_required(login_url='login')
def order_detail(request, order_id):
    if request.user.is_admin:
        order = get_object_or_404(Order, pk=order_id)
        products = OrderProduct.objects.filter(order=order)
        total_price = order.order_total
        if order.coupon:
            total_price -= order.coupon.discount_price
        subtotal = sum(product.quantity * product.variation.discounted_price for product in products)

        context = {
            'order': order,
            'products': products,
            'total_price': total_price,
            'subtotal': subtotal
        }
        return render(request, 'orders/order_detail.html', context)
    else:
        return redirect('decorator')

# New orders view
@login_required(login_url='login')
def new_orders(request):
    if request.user.is_admin:
        items_per_page = 20
        p = Paginator(Order.objects.filter(status='New'), items_per_page)
        page = request.GET.get('page')
        data = p.get_page(page)
        context = {
            'data': data
        }
        return render(request, 'orders/new_orders.html', context)
    else:
        return redirect('decorator')

# Cancelled orders view
@login_required(login_url='login')
def cancelled_orders(request):
    if request.user.is_admin:
        items_per_page = 15
        p = Paginator(Order.objects.filter(status__in=['Cancelled', 'Returned']).order_by('-created_at'), items_per_page)
        page = request.GET.get('page')
        data = p.get_page(page)
        context = {
            'data': data
        }
        return render(request, 'orders/cancelled_orders.html', context)
    else:
        return redirect('decorator')

# Restock view
@login_required(login_url='login')
def restock(request, order_id):
    if request.user.is_admin:
        order = get_object_or_404(Order, id=order_id)
        order_products = OrderProduct.objects.filter(order=order)

        for order_product in order_products:
            product = order_product.variation
            product.quantity += order_product.quantity
            product.save()

        order.restock = True
        order.save()

        return redirect('cancelled_orders')
    else:
        return redirect('decorator')

# Product offer views
@login_required(login_url='login')
def product_offer(request):
    if request.user.is_admin:
        items_per_page = 20
        p = Paginator(ProductOffer.objects.all().order_by('-id'), items_per_page)
        page = request.GET.get('page')
        data = p.get_page(page)
        context = {
            'data': data
        }
        return render(request, 'product_offer/product_offer.html', context)
    else:
        return redirect('decorator')

@login_required(login_url='login')
def add_product_offer(request):
    if request.user.is_admin:
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
        form = ProductOfferForm()
        context = {
            'form': form
        }
        return render(request, 'product_offer/product_offer_form.html', context)
    else:
        return redirect('decorator')
		
		
@login_required(login_url='login')
def edit_product_offer(request, product_offer_id):
    if request.user.is_admin:
        product_offer = get_object_or_404(ProductOffer, id=product_offer_id)
        if request.method == 'POST':
            form = ProductOfferForm(request.POST, instance=product_offer)
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
        form = ProductOfferForm(instance=product_offer)
        context = {
            'form': form
        }
        return render(request, 'product_offer/product_offer_form.html', context)
    else:
        return redirect('decorator')
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@login_required(login_url='login')
def delete_product_offer(request, product_offer_id):
    if request.user.is_admin:
        product_offer = get_object_or_404(ProductOffer, id=product_offer_id)
        product_offer.delete()
        return redirect('product_offer')
    else:
        return redirect('decorator')

# Category offer views
@login_required(login_url='login')
def category_offer(request):
    if request.user.is_admin:
        items_per_page = 20
        p = Paginator(CategoryOffer.objects.all().order_by('-id'), items_per_page)
        page = request.GET.get('page')
        data = p.get_page(page)
        context = {
            'data': data
        }
        return render(request, 'category_offer/category_offer.html', context)
    else:
        return redirect('decorator')

@login_required(login_url='login')
def add_category_offer(request):
    if request.user.is_admin:
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
        form = CategoryOfferForm()
        context = {
            'form': form
        }
        return render(request, 'category_offer/category_offer_form.html', context)
    else:
        return redirect('decorator')

@login_required(login_url='login')
def edit_category_offer(request, category_offer_id):
    if request.user.is_admin:
        category_offer = get_object_or_404(CategoryOffer, id=category_offer_id)
        if request.method == 'POST':
            form = CategoryOfferForm(request.POST, instance=category_offer)
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
        form = CategoryOfferForm(instance=category_offer)
        context = {
            'form': form
        }
        return render(request, 'category_offer/category_offer_form.html', context)
    else:
        return redirect('decorator')

@login_required(login_url='login')
def delete_category_offer(request, category_offer_id):
    if request.user.is_admin:
        category_offer = get_object_or_404(CategoryOffer, id=category_offer_id)
        category_offer.delete()
        return redirect('category_offer')
    else:
        return redirect('decorator')

# ===================================== COUPONS =============================================================================================================================================================================

# Coupon views
@login_required(login_url='login')
def coupons(request):
    if request.user.is_admin:
        data = Coupon.objects.all()
        context = {
            'data': data
        }
        return render(request, 'coupons/coupons.html', context)
    else:
        return redirect('decorator')

@login_required(login_url='login')
def add_coupon(request):
    if request.user.is_admin:
        if request.method == 'POST':
            form = CouponForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('coupons')
        form = CouponForm()
        context = {
            'form': form
        }
        return render(request, 'coupons/coupon_form.html', context)
    else:
        return redirect('decorator')

@login_required(login_url='login')
def edit_coupon(request, coupon_id):
    if request.user.is_admin:
        coupon = get_object_or_404(Coupon, id=coupon_id)
        if request.method == 'POST':
            form = CouponForm(request.POST, instance=coupon)
            if form.is_valid():
                form.save()
                return redirect('coupons')
        form = CouponForm(instance=coupon)
        context = {
            'form': form
        }
        return render(request, 'coupons/coupon_form.html', context)
    else:
        return redirect('decorator')

@login_required(login_url='login')
def delete_coupon(request, coupon_id):
    if request.user.is_admin:
        coupon = get_object_or_404(Coupon, id=coupon_id)
        coupon.delete()
        return redirect('coupons')
    else:
        return redirect('decorator')





# Admin dashboard view
@login_required(login_url='login')
def admindashboard(request):
    if request.user.is_admin:
        yesterday = datetime.now() - timedelta(days=1)
        today = datetime.now() + timedelta(days=1)
        start_date = request.GET.get('start_date', yesterday.strftime('%Y-%m-%d'))
        end_date = request.GET.get('end_date', today.strftime('%Y-%m-%d'))

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            start_date = datetime.strptime(yesterday.strftime('%Y-%m-%d'), '%Y-%m-%d')

        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
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
            'order_status': order_status_json,
            'total_refunds': total_refunds,
            'refund_count': refund_count,
            'start_date': start_date,
            'end_date': end_date
        }
        return render(request, 'admindashboard.html', context)
    else:
        return redirect('decorator')


@login_required(login_url='login')
def download_sales_report(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Order Number', 'Order Total', 'Order Date', 'User', 'Product Name', 'Quantity', 'Price'])

    period = request.GET.get('period', 'daily')
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')

    today = timezone.localtime().date()
    start_date, end_date = None, None

    # Determine the date range based on the period and provided dates
    if period == 'custom' and start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() + timedelta(days=1)
        except ValueError:
            # Fallback to default date range if parsing fails
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

    # Make sure datetime objects are timezone-aware
    start_date = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
    end_date = timezone.make_aware(datetime.combine(end_date, datetime.min.time()))

    # Filter orders based on the date range
    orders = Order.objects.filter(created_at__range=(start_date, end_date)).select_related('user')

    # Write order details to the CSV
    for order in orders:
        order_items = OrderProduct.objects.filter(order=order).select_related('product')
        for order_item in order_items:
            writer.writerow([
                order.order_number,
                order.order_total,
                order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                order.user.username,
                order_item.product.product_name,
                order_item.quantity,
                order_item.product_price,
            ])

    return response
