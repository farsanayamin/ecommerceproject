# Generated by Django 4.2.4 on 2023-11-16 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('offer_name', models.CharField(max_length=100)),
                ('offer_type', models.CharField(choices=[('PERCENT', 'Percentage Discount'), ('FIXED', 'Fixed Amount Discount')], max_length=10)),
                ('discount_rate', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='ProductOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('offer_name', models.CharField(max_length=100)),
                ('offer_type', models.CharField(choices=[('PERCENT', 'Percentage Discount'), ('FIXED', 'Fixed Amount Discount')], max_length=10)),
                ('discount_rate', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
            ],
        ),
    ]
