# Generated by Django 4.1.6 on 2023-02-23 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prophetv2', '0031_alter_profile_risk_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='stocks',
            name='rise',
            field=models.BooleanField(default=True),
        ),
    ]
