from .models import Brand,Variation, Product
from django.db.models import Min, Max

def brand_links(request):
    brands = Brand.objects.all()
    return dict(brand_links = brands)

def get_filters(request):
    cats = Product.objects.distinct().values('category__category_name', 'category__id')
    brands = Product.objects.distinct().values('brand__brand_name', 'brand__id')
    minMaxPrice = Variation.objects.aggregate(Min('price'), Max('price'))
    colors = Variation.objects.distinct().values('color__name', 'color__id', 'color__code')
    sizes = Variation.objects.distinct().values('size__name', 'size__id')

    context = {
        'cats':cats,
        'brands':brands,
        'colors': colors,
        'sizes': sizes,
        'minMaxPrice':minMaxPrice
    }

    return context