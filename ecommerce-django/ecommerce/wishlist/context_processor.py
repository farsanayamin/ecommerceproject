from .models import Wishlist

def wishlist_count(request):
    unique_items_count = 0  # Default to 0 for non-authenticated users
    if request.user.is_authenticated:
        unique_items_count = Wishlist.objects.filter(user=request.user).count()
    
    return {
        'unique_items_count': unique_items_count
    }
