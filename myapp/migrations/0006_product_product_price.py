# Generated by Django 4.0.5 on 2022-06-19 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_alter_product_product_detail_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_price',
            field=models.CharField(default='', max_length=100),
        ),
    ]
