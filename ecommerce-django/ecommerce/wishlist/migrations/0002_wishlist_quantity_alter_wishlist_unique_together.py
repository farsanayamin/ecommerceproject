# Generated by Django 4.2.4 on 2024-07-05 10:49

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0011_remove_size_code'),
        ('wishlist', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='wishlist',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterUniqueTogether(
            name='wishlist',
            unique_together={('product', 'user')},
        ),
    ]
