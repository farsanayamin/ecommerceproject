# Generated by Django 4.2.4 on 2023-11-27 17:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_alter_variation_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='size',
            name='code',
        ),
    ]
