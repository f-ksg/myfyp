# Generated by Django 4.1.6 on 2023-02-15 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prophetv2', '0017_delete_stockinfo'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tradingName', models.CharField(max_length=100)),
                ('stockCode', models.CharField(max_length=100)),
                ('lastPrice', models.FloatField(blank=True)),
                ('roe', models.FloatField(blank=True)),
                ('marketcap', models.FloatField(blank=True)),
                ('totalRev', models.FloatField(blank=True)),
                ('pe', models.FloatField(blank=True)),
                ('yieldPercent', models.FloatField()),
                ('sector', models.CharField(max_length=100)),
                ('gtiScore', models.FloatField(blank=True)),
                ('oneYearChange', models.FloatField(blank=True)),
            ],
        ),
    ]
