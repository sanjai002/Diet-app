# Generated by Django 4.1 on 2024-02-05 12:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('diet', '0013_alter_food_image_restaurant'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='restaurant',
            name='foods',
        ),
    ]