# Generated by Django 4.1 on 2024-02-05 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diet', '0015_restaurant_foods'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurant',
            name='foods',
            field=models.ManyToManyField(related_name='restaurants', to='diet.food'),
        ),
    ]