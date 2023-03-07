# Generated by Django 4.1.6 on 2023-02-24 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prophetv2', '0034_stocksold_unique_stock_sold_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='stocksold',
            name='unique_stock_sold_null',
        ),
        migrations.AddConstraint(
            model_name='stocksold',
            constraint=models.UniqueConstraint(condition=models.Q(('sold_at', None)), fields=('profile', 'stock'), name='unique_stock_sold_null'),
        ),
    ]