# Generated by Django 4.1.6 on 2023-02-15 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prophetv2', '0015_stockinfo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockinfo',
            name='gtiScore',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='stockinfo',
            name='lastPrice',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='stockinfo',
            name='marketcap',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='stockinfo',
            name='oneYearChange',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='stockinfo',
            name='pe',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='stockinfo',
            name='roe',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='stockinfo',
            name='totalRev',
            field=models.FloatField(null=True),
        ),
    ]
