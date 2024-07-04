from django.contrib import admin
from .models import *
import admin_thumbnails
# Register your models here.



# Brand
class BrandAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('brand_name',)}
    list_display = ('brand_name', 'slug')

admin.site.register(Brand, BrandAdmin)



@admin_thumbnails.thumbnail('image')
class ProductImageInline(admin.TabularInline):
    model = Images
    readonly_fields = ('id',)
    extra = 1



class ProductVariantsInline(admin.TabularInline):
    model = Variation
    readonly_fields = ('image_tag',)
    extra = 1
    show_change_link = True



@admin_thumbnails.thumbnail('image')
class ImagesAdmin(admin.ModelAdmin):
    list_display = ['image','title','image_thumbnail', 'id']

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'brand', 'modified_date', 'is_available')
    list_filter = ['category']
    readonly_fields = ('image_tag',)
    inlines = [ProductImageInline,ProductVariantsInline]

    prepopulated_fields = {'slug' : ('product_name',)}
admin.site.register(Product, ProductAdmin)




class ColorAdmin(admin.ModelAdmin):
    list_display = ['name','code','color_tag']

class SizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'id']


class VariantsAdmin(admin.ModelAdmin):
    list_display = ['title','product','color','size','price','quantity','image_tag']

admin.site.register(ReviewRating)

admin.site.register(Images,ImagesAdmin)
admin.site.register(Color,ColorAdmin)
admin.site.register(Size,SizeAdmin)
