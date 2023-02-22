# Generated by Django 4.1.6 on 2023-02-21 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prophetv2', '0025_alter_profile_accountbalance'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='stockowned',
            constraint=models.UniqueConstraint(fields=('profile', 'stock', 'purchase_price'), name='unique_stock_owned'),
        ),
        migrations.AddConstraint(
            model_name='stockowned',
            constraint=models.UniqueConstraint(condition=models.Q(('purchased_at', None)), fields=('profile', 'stock'), name='unique_stock_owned_null'),
        ),
    ]
