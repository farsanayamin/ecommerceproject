from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from offers.models import CategoryOffer

# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    cat_image = models.ImageField(upload_to="photos/categories", blank=True,)
    offer = models.ForeignKey(CategoryOffer, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        # Generate the slug based on the name if it doesn't exist
        if not self.slug:
            self.slug = slugify(self.category_name)

        super(Category, self).save(*args, **kwargs)



    def get_url(self):
        return reverse('products_by_category', args=[self.slug])


    def __str__(self) -> str:
        return self.category_name
    