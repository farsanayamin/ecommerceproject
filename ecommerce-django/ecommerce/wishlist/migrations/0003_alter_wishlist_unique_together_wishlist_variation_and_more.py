# Generated by Django 4.2.4 on 2024-07-07 02:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_remove_size_code'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wishlist', '0002_wishlist_quantity_alter_wishlist_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='wishlist',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='wishlist',
            name='variation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.variation'),
        ),
        migrations.AlterUniqueTogether(
            name='wishlist',
            unique_together={('product', 'user', 'variation')},
        ),
    ]