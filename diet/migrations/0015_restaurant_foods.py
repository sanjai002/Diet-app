# Generated by Django 4.1 on 2024-02-05 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diet', '0014_remove_restaurant_foods'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='foods',
            field=models.ManyToManyField(to='diet.food'),
        ),
    ]
