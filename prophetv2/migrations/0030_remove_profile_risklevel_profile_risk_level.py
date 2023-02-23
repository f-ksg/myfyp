# Generated by Django 4.1.6 on 2023-02-22 23:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prophetv2', '0029_profile_risklevel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='risklevel',
        ),
        migrations.AddField(
            model_name='profile',
            name='risk_level',
            field=models.IntegerField(choices=[(1, 'Low'), (2, 'Moderate'), (3, 'Medium'), (4, 'High'), (5, 'Very High')], default=3),
        ),
    ]