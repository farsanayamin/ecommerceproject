from django.shortcuts import render, redirect, get_object_or_404
from store.models import *
from .models import *
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required 
from django.http import HttpResponse, JsonResponse
from wishlist.models import Wishlist
from addressbook.forms import UserAddressForm
from addressbook.models import UserAddressBook
from django.contrib import messages
from coupon.forms import CouponForm
from django.template.loader import render_to_string


# Create your views here.

def _cart_id(request):
    cart = request.session.session_key

    if not cart:
        cart = request.session.create()
    
    return cart


from django.http import JsonResponse

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect


def add_cart(request, product_id):
    current_user = request.user
    product = get_object_or_404(Product, id=product_id)
    size = request.GET['size']
    color = request.GET['color']
    variation = get_object_or_404(Variation, product=product, color_id=color, size_id=size)
    
    max_quantity_per_person = 3  # Set the max quantity per person for the same item
    
    if current_user.is_authenticated:
        # Remove from wishlist if exists
        Wishlist.objects.filter(user=current_user, product=product).delete()

        # Calculate the unique items count in the wishlist after deletion
        unique_items_count = Wishlist.objects.filter(user=current_user).count()

        # Get or create a cart for the session
        cart, created = Cart.objects.get_or_create(cart_id=_cart_id(request))

        # Check if the item already exists in the cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            variation=variation,
            defaults={'quantity': 1, 'user': current_user, 'product': product}
        )

        if not created:  # Item already in cart
            if cart_item.quantity + 1 > max_quantity_per_person:
                return JsonResponse({'error': f"Cannot add more than {max_quantity_per_person} of the same item."})
            cart_item.quantity += 1
            cart_item.save()

        # Return JSON response for AJAX handling
        return JsonResponse({
            'success': True,
            'quantity': cart_item.quantity,
            'unique_items_count': unique_items_count
        })

    else:
        # Handle for guest users (non-authenticated)
        cart, created = Cart.objects.get_or_create(cart_id=_cart_id(request))

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            variation=variation,
            defaults={'quantity': 1, 'product': product}
        )

        if not created:  # Item already in cart
            if cart_item.quantity + 1 > max_quantity_per_person:
                return JsonResponse({'error': f"Cannot add more than {max_quantity_per_person} of the same item."})
            cart_item.quantity += 1
            cart_item.save()

        # For non-authenticated users, you might want to handle wishlist count separately or skip this part

        # Just for consistency, let's redirect to referrer and set the cookie
        url = request.META.get('HTTP_REFERER', '/')
        response = redirect(url)
        response.set_cookie('unique_items_count', 0)  # Or some default value if not calculating for guests
        return response




def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product = product, user = request.user, id = cart_item_id)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_item = CartItem.objects.get(product = product, cart = cart, id = cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')





def remove_cart_item(request, product_id,cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product = product, user = request.user,id = cart_item_id)
    else:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_item = CartItem.objects.get(product = product, cart = cart, id = cart_item_id)
    cart_item.delete()
    return redirect('cart')




def cart(request, total=0, quantity = 0 , cart_items = None):
  
    tax_rate = 2
    tax = 0
    grand_total =0
    discount = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user)
        else:
            cart = Cart.objects.get(cart_id  = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart)
        for cart_item in cart_items:
            total += (cart_item.variation.discounted_price * cart_item .quantity)
            quantity += cart_item.quantity
        
        tax = (tax_rate * total)/100    
        grand_total = total + tax - discount
    except ObjectDoesNotExist:
        pass

    context = {
        'total':total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' :tax,
        'grand_total':grand_total,
       
    }
        
    return render(request, "carts/cart.html", context)

'''
@login_required(login_url='login')
def checkout(request, total=0, quantity = 0 , cart_items = None):
    coupon_used = False
    discount_price = 0
    coupon = CouponForm(request.GET)
    print('COOPEN',coupon)
    coupon_obj = None
    code = None
    if coupon.is_valid():
        code = coupon.cleaned_data['code']
        try:
            coupon_obj = Coupon.objects.get(code = code)
            discount_price = coupon_obj.discount_price
            coupon_used = True
        except Coupon.DoesNotExist:
            messages.error(request, "Coupon doesn't exist")
    coupon_form = CouponForm()

    

    try:
        tax_rate = 2
        tax = 0
        grand_total =0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user, is_active = True)
        else:
            cart = Cart.objects.get(cart_id  = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active = True)
        
        for cart_item in cart_items:
            total += (cart_item.variation.discounted_price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (tax_rate * total)/100         
        grand_total = total + tax 

        if coupon_obj is not None:
            
            if grand_total > coupon_obj.minimum_amount:
                grand_total -= coupon_obj.discount_price
                print(grand_total)
            else:
                coupon_used = False
                messages.warning(request, 'You should purchase more than $'+ str(coupon_obj.minimum_amount) +' to use this coupon')
            
    except ObjectDoesNotExist:
        pass

    try:
        address = UserAddressBook.objects.get(user=request.user, status = True)
        form = UserAddressForm(instance = address)
    except:
        form = UserAddressForm()



    try:    
        addresses = UserAddressBook.objects.filter(user=request.user)
    except UserAddressBook.DoesNotExist:
        addresses = None
    

  
    context = {
        'total':total,
        'quantitiy' : quantity,
        'cart_items' : cart_items,
        'tax' :tax,
        'grand_total':grand_total,
        'form':form,
        'addresses': addresses,
        'coupon_form':coupon_form,
        'coupon_used':coupon_used,
        'code' :code,
        'discount':discount_price
    }

    return render(request, 'carts/checkout.html', context)


'''

@login_required(login_url='login')
def checkout(request, total=0, quantity = 0 , cart_items = None):
    coupon_used = False
    discount_price = 0
    coupon = CouponForm(request.GET)
    coupon_obj = None
    code = None
    if coupon.is_valid():
        code = coupon.cleaned_data['code']
        try:
            coupon_obj = Coupon.objects.get(code = code)
            discount_price = coupon_obj.discount_price
            print(f"Coupon '{code}' applied with discount: {discount_price}")
            coupon_used = True
        except Coupon.DoesNotExist:
            messages.error(request, "Coupon doesn't exist")
    coupon_form = CouponForm()

    

    try:
        tax_rate = 2
        tax = 0
        grand_total =0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user, is_active = True)
        else:
            cart = Cart.objects.get(cart_id  = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active = True)
        
        for cart_item in cart_items:
            total += (cart_item.variation.discounted_price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (tax_rate * total)/100         
        grand_total = total + tax 

        if coupon_obj is not None:
            
            if grand_total > coupon_obj.minimum_amount:
                grand_total -= coupon_obj.discount_price
                print(grand_total)
            else:
                coupon_used = False
                messages.warning(request, 'You should purchase more than $'+ str(coupon_obj.minimum_amount) +' to use this coupon')
            
    except ObjectDoesNotExist:
        pass

    try:
        address = UserAddressBook.objects.get(user=request.user, status = True)
        form = UserAddressForm(instance = address)
    except:
        form = UserAddressForm()



    try:    
        addresses = UserAddressBook.objects.filter(user=request.user)
    except UserAddressBook.DoesNotExist:
        addresses = None
    

  
    context = {
        'total':total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' :tax,
        'grand_total':grand_total,
        'form':form,
        'addresses': addresses,
        'coupon_form':coupon_form,
        'coupon_used':coupon_used,
        'code' :code,
        'discount':discount_price
    }

    return render(request, 'carts/checkout.html', context)



def remove_coupon(request):
    if request.method == 'POST':
        # Logic to remove the coupon
        request.session.pop('coupon_code', None) 
        
        return redirect('checkout')



def update_cart(request):
    cart_item_id = request.POST.get('cart_item_id')
    new_quantity = request.POST.get('new_quantity')

    # Update the cart item's quantity

    cart_item = CartItem.objects.get(id=cart_item_id)
    if int(new_quantity) < cart_item.variation.quantity:
        cart_item.quantity = int(new_quantity)
    else:
        cart_item.quantity = cart_item.variation.quantity
    cart_item.save()
    total = 0
    quantity = 0
    tax_rate = 2
    tax = 0
    grand_total =0
    discount = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user, is_active = True)
        else:
            cart = Cart.objects.get(cart_id  = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active = True)
        for cart_item in cart_items:
            total += (cart_item.variation.price * cart_item .quantity)
            quantity += cart_item.quantity
            try:        
                discount = cart_item.cart.coupon.discount_price
                coupon_used = True
                coupon = cart_item.cart.coupon
            except:
                pass
        tax = (tax_rate * total)/100    
        grand_total = total + tax - discount
    except ObjectDoesNotExist:
        pass

    context = {
        'total':total,
        'quantitiy' : quantity,
        'cart_items' : cart_items,
        'tax' :tax,
        'grand_total':grand_total,
       
    }
    t = render_to_string('ajax/cart-quantity.html',context)
    return JsonResponse({'data': t})
   