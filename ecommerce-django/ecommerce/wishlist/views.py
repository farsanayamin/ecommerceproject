from django.shortcuts import render,redirect
from store.models import Product,Variation
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import *
# Create your views here.


from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from .models import Wishlist

from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from .models import Wishlist, Product




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
'''
def remove_from_wishlist(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        wishlist = Wishlist.objects.filter(user=request.user)
        if wishlist.exists():
            wishlist.products.remove(product)
    # Redirect back to the product detail page or referer page
    return redirect(request.META.get('HTTP_REFERER', '/'))
'''


from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from .models import Wishlist

def remove_from_wishlist(request, product_id, variation_id=None):
    if request.user.is_authenticated:
        # Get the specific wishlist entry for the user, product, and optional variation
        filters = {'user': request.user, 'product_id': product_id}
        if variation_id:
            filters['variation_id'] = variation_id
        
        wishlist_item = get_object_or_404(Wishlist, **filters)
        
        if request.method == 'POST':
            wishlist_item.delete()
            return redirect('my_wishlist')  # Replace with the name of your wishlist page URL
        
        return JsonResponse({'message': 'Invalid request method.'}, status=405)
    
    return redirect('login')  # Redirect to login if the user is not authenticated
