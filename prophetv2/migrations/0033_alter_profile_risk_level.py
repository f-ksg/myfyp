# Generated by Django 4.1.6 on 2023-02-24 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prophetv2', '0032_stocks_rise'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='risk_level',
            field=models.IntegerField(choices=[(1, 'Lv.1 Low'), (2, 'Lv.2 Moderate'), (3, 'Lv.3 High')], default=1),
        ),
    ]