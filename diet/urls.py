from django.urls import path

from . import views


urlpatterns=[
    path('',views.index,name='index'),
    path('register',views.register,name="register"),
    path('login',views.user_login,name='login'),
    path('details',views.details,name='details'),
    path('food/food_view',views.foodview,name='food'),
    path('food/add_food/<int:food_id>',views.add_food,name='add_food'),
    path('food/delete_food/<int:food_id>',views.delete_food,name='delete_food'),
    path('logout_view',views.logout_view,name='logout_view')

]