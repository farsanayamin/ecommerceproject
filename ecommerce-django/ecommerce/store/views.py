from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct
from wishlist.models import Wishlist
from django.http import JsonResponse
from django.template.loader import render_to_string

# Create your views here.

def store(request, category_slug = None, brand_slug = None):
    brands = None
    categories = None
    products = None
    reviews = None
    items_per_page = 6

    if category_slug is not None:
        categories = get_object_or_404(Category, slug = category_slug)
        products = Product.objects.filter(category = categories, is_available = True).order_by('id')
        paginator = Paginator(products, items_per_page)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count
    elif brand_slug is not None:
        brands = get_object_or_404(Brand, slug = brand_slug)
        products = Product.objects.filter(brand =brands, is_available = True).order_by('id')
        paginator = Paginator(products, items_per_page)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.filter(is_available = True).order_by('id')
        paginator = Paginator(products, items_per_page)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    for product in products:
        reviews = ReviewRating.objects.filter(product = product, status = True)


    

    context = {
            'products':paged_products,
            'product_count':product_count,
            'reviews': reviews,
        }    
    return render(request, 'store/store.html', context)


# ============================================================= PRODUCT DETAIL ======================================================================================
def product_detail(request, brand_slug, product_slug):
    try:
        
        single_product = Product.objects.get(brand__slug = brand_slug, slug = product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request), product = single_product).exists()
         # Check if the product is in the wishlist
        in_wishlist = False
        
    
    except Exception as e:
        raise e
    
    if request.user.is_authenticated:
        try:
            in_wishlist = Wishlist.objects.filter(product=single_product, user=request.user).exists()
            orderproduct = OrderProduct.objects.filter(user = request.user, product= single_product, order__status = 'Delivered').exists()
        except OrderProduct.DoesNotExist:
            orderproduct = False
    else:
        orderproduct = False


    # Get reviews
    reviews = ReviewRating.objects.filter(product = single_product, status = True)
    product_gallery = Images.objects.filter(product = single_product) 
    colors = Variation.objects.filter(product = single_product).values('color__id', 'color__name', 'color__code','image_id').distinct()
    size = Variation.objects.filter(product = single_product).values('size__id', 'size__name','price', 'discounted_price', 'color__id')
   
    context = {
        'single_product':single_product,
        'in_cart' :in_cart,
        'orderproduct':orderproduct,
        'reviews' : reviews,
        'product_gallery' : product_gallery,
        'sizes':size,
        'colors':colors,
        'in_wishlist':in_wishlist
        # 'variant':variant,
        
    }
    return render(request, 'store/product_detail.html', context)



def submit_review(request, product_id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            # Fetch the product for which review is being submitted
            product = get_object_or_404(Product, id=product_id)
            
            # Extract review data from POST request
            rating = float(request.POST.get('rating'))
            subject = request.POST.get('subject')
            review_text = request.POST.get('review')
            
            # Create new review object
            new_review = ReviewRating(
                product=product,
                user=request.user,
                rating=rating,
                subject=subject,
                review=review_text
            )
            new_review.save()
            
            # Redirect to product detail page after review submission
            return JsonResponse({'success': True, 'message': 'Review submitted successfully!'})
        else:
            # Redirect to login page if user is not authenticated
            return JsonResponse({'success': False, 'message': 'You must be logged in to submit a review.'})
    else:
        # Redirect to product detail page if request method is not POST
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})


#========================================== SEARCH =================================================================================================================

def search(request):

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(
                Q(description__icontains = keyword) |
                Q(product_name__icontains = keyword) |
                Q(brand__brand_name__icontains = keyword) |
                Q(category__category_name__icontains = keyword)
            )
            product_count = products.count()

            context = {
                'products':products,
                'product_count' :product_count
            }
            return render(request, 'store/store.html', context)
        else:
            pass
    else:
        return redirect('store')

# =================================================  REVIEWS =========================================================================================================

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == "POST":
        try:
            reviews = ReviewRating.objects.get(user__id = request.user.id, product__id= product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']

                data.ip = request.META.get('REMOTE_ADDR')
                data.product.pk = product_id
                data.user = request.user
                data.save()
                messages.success(request, "Thank you! Your review has been submitted")
                return redirect(url)
            
# ============================================== BRAND LIST =======================================================================================================
def brand_list(request):
    brands = Brand.objects.all()
    context = {
        'brands' : brands
    }
    return render(request, 'store/brand_list.html', context)



# =================================================== CATEGORY LIST =================================================================================================
def category_list(request):
    categories = Category.objects.all()
    context = {
        'categories':categories
    }
    return render(request, 'store/category_list.html', context)



# ==================================================== FILTER DATA ===========================================================================================================


from django.db.models import F

def filter_data(request):
    colors = request.GET.getlist('color[]')
    categories = request.GET.getlist('category[]')
    brands = request.GET.getlist('brand[]')
    sizes = request.GET.getlist('size[]')
    minPrice = request.GET.get('minPrice', 0)
    maxPrice = request.GET.get('maxPrice', float('inf'))
    sort = request.GET.get('sort', '-id')  # Default sorting by newest first

    allProducts = Product.objects.all().distinct()

    # Apply filters
    if minPrice and maxPrice:
        allProducts = allProducts.filter(variation__price__gte=minPrice, variation__price__lte=maxPrice)

    if colors:
        allProducts = allProducts.filter(variation__color__in=colors).distinct()

    if sizes:
        allProducts = allProducts.filter(variation__size__in=sizes).distinct()

    if categories:
        allProducts = allProducts.filter(category__id__in=categories).distinct()

    if brands:
        allProducts = allProducts.filter(brand__id__in=brands).distinct()

    # Annotate if sorting by a related field like 'variation.price'
    if sort:
        if 'variation.price' in sort:
            allProducts = allProducts.annotate(variation_price=F('variation__price'))
            sort = sort.replace('variation.price', 'variation_price')
        
        # Apply the sorting after filtering
        allProducts = allProducts.order_by(sort)

    # Render the filtered and sorted products to HTML
    t = render_to_string('ajax/product-list.html', {'products': allProducts})
    return JsonResponse({'data': t})
