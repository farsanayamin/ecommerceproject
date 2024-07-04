from django.db import models
from category.models import Category
from django.urls import reverse
from accounts.models import Account
from django.db.models import Avg, Count
from django.utils.text import slugify
from decimal import Decimal
from django.utils.safestring import mark_safe


from offers.models import ProductOffer

# Create your models here.

# Brand
class Brand(models.Model):
    brand_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    image = models.ImageField(upload_to='photos/brands')


    def save(self, *args, **kwargs):
        # Generate the slug based on the name if it doesn't exist
        if not self.slug:
            self.slug = slugify(self.brand_name)

        super(Brand, self).save(*args, **kwargs)

    def get_url(self):
        return reverse('products_by_brand', args=[self.slug])

    def __str__(self) -> str:
        return self.brand_name



class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(max_length=500, blank=True)
    image = models.ImageField(upload_to='photos/products', null=False)
    is_available = models.BooleanField(default=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    offer = models.ForeignKey(ProductOffer, on_delete=models.CASCADE, null=True, blank=True)
    create_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now=True)



   


    def save(self, *args, **kwargs):
        # Generate the slug based on the name if it doesn't exist
        if not self.slug:
            self.slug = slugify(self.product_name)
        super(Product, self).save(*args, **kwargs)


    def get_url(self):
        return reverse('product_detail', args=[self.brand.slug, self.slug])

    def __str__(self) -> str:
        return self.product_name
    

    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average = Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])

        return avg 

    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count = Count('rating'))
        count = 0

        if reviews['count'] is not None:
            count = float(reviews['count'])

        return count 
    
    def image_tag(self):
        if self.image.url is not None:
            return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))
        else:
            return ""


# Images
class Images(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    title = models.CharField(max_length=50,blank=True)
    image = models.ImageField(blank=True, upload_to='images/')

    def __str__(self):
        return self.title


# Color
class Color(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self) -> str:
        return self.name
    
    def color_tag(self):
        if self.code is not None:
            return mark_safe('<p style="background-color:{}">Color </p>'.format(self.code))
        else:
            return ""


# Size
class Size(models.Model):
    name = models.CharField(max_length=20, unique=True)
    def __str__(self):
        return self.name





class Variation(models.Model):
    slug = models.SlugField(null=True, blank=True, max_length=200, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, blank=True, null=True)
    size = models.ForeignKey(Size, on_delete=models.CASCADE, blank=True, null=True)
    image_id  = models.IntegerField(blank=True, null=True, default=0)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0) # type: ignore
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)
    discounted_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True) # type: ignore

    def calculate_discounted_price(self):
        discounted_price = self.price        
        if self.product.category.offer:
            offer = self.product.category.offer
            if offer.offer_type == 'PERCENT':
                discounted_price = self.price - (self.price * (self.product.category.offer.discount_rate / 100))
            elif offer.offer_type == 'FIXED':
                discounted_price = self.price - self.product.category.offer.discount_rate
        elif self.product.offer:
            offer = self.product.offer
            if offer.offer_type == 'PERCENT':
                discounted_price = self.price - (self.price * (self.product.offer.discount_rate / 100))
            elif offer.offer_type == 'FIXED':
                discounted_price = self.price - self.product.offer.discount_rate
        
        return Decimal(discounted_price)



    def save(self, *args, **kwargs):
        self.slug = slugify(self.product.product_name + str(self.color) + str(self.size))
        
        if self.price < 0:
            self.price = 1
        
        if self.quantity < 0:
            self.quantity = 1

        self.discounted_price = self.calculate_discounted_price()
        super(Variation, self).save(*args, **kwargs)


    def __str__(self) -> str:
        return str(self.product) + str(self.color) + str(self.size) 
    

    def image(self):
        img = Images.objects.get(id=self.image_id)
        if img.pk is not None:
             varimage=img.image.url
        else:
            varimage=""
        return varimage
    
    def image_tag(self):
        img = Images.objects.get(id=self.image_id)
        if img.id is not None:
             return mark_safe('<img src="{}" height="50"/>'.format(img.image.url))
        else:
            return ""

    



class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject =models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    def __str__(self) -> str:
        return self.subject
    


