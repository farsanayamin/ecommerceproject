from django.shortcuts import render,redirect
from store.models import Product
from django.http import JsonResponse

from .models import *
# Create your views here.

def my_wishlist(request):
    wishlist = Wishlist.objects.filter(user = request.user)
    context = {
        "wishlist":wishlist,
    }
    return render(request, 'wishlist/wishlist.html', context)


def add_to_wishlist(request, product_id):
    product = Product.objects.get(id = product_id)
    
    cw = Wishlist.objects.filter(product=product, user = request.user).count()

    if not cw:
        wishlist = Wishlist.objects.create(
            product = product,
            user = request.user
        )
        data = {
            'bool': True
        }
    else:
        data = {
            'bool': False
        }
    url = request.META.get('HTTP_REFERER')

    return redirect(url)
