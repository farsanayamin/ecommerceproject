# Generated by Django 4.2.4 on 2024-07-09 10:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0011_remove_size_code'),
        ('orders', '0008_wallet'),
    ]

    operations = [
        migrations.RenameField(
            model_name='wallet',
            old_name='user_id',
            new_name='user',
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.BigIntegerField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.order')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('variation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.variation')),
            ],
        ),
    ]