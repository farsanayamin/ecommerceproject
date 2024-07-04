from django.db import models
from accounts.models import Account

# Create your models here.
class UserAddressBook(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50, unique=True)
    address_line_2 = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    pincode = models.CharField(max_length=20, null=True, blank=True)
    order_note = models.CharField(max_length=100, blank=True)
    status = models.BooleanField(default=False)

    