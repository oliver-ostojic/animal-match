# Generated by Django 5.0.7 on 2024-08-14 04:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matcher', '0002_rename_locationtobiomemapper_locationmapper_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='animal',
            name='lifespan',
            field=models.CharField(max_length=30),
        ),
    ]