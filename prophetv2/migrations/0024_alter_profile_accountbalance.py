# Generated by Django 4.1.6 on 2023-02-21 00:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prophetv2', '0023_alter_stockowned_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='accountbalance',
            field=models.DecimalField(decimal_places=3, max_digits=10),
        ),
    ]