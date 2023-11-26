from django.contrib import admin
from .models import User,Food,FoodCategory,UserDetails

# Register your models here.
admin.site.register(User)
admin.site.register(Food)
admin.site.register(FoodCategory)
admin.site.register(UserDetails)