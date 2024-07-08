from django.db import models
from accounts.models import Account
from store.models import Product,Variation
# Create your models here.
class Wishlist(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # New field to track quantity
    variation = models.ForeignKey(Variation, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ('product', 'user', 'variation')

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name} ({self.variation})"
