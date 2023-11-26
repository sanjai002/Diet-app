
from django.db import IntegrityError
from django.shortcuts import render,redirect
from django.urls import path
from numpy import repeat
from django.http import HttpResponseRedirect,HttpResponse
from django.urls import reverse
from django.views.generic import ListView
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import F

# Create your views here.


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(foodview)
        else:
            return render(request,'login.html',
                          {
                              'message':'Wrong username or password'
                          })
    return render(request,'login.html',{
       
    })

def index(request):
    return render(request,'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']

        # Ensure password matches confirmation
        password = request.POST['password1']
        confirmation = request.POST['password2']
        if password != confirmation:
            return render(request, 'register.html', {
                'message': 'Passwords must match.',
            })
               # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            login(request, user)
            return redirect(details)
        except IntegrityError:
            return render(request, 'register.html', {
                'message': 'Username already taken.',
            })
    
    return render(request, 'register.html')        
                              

@login_required
def details(request):
    if request.method == 'POST':
        age=request.POST['age']
        gender=request.POST['gender']
        height=request.POST['height']
        weight=request.POST['weight']
        activity=request.POST['activity']
        goal=request.POST['goal']
        print("Age",age,"Gender",gender,"Height",height,"Weight",weight,"Activity",activity)
        calories=0
        if gender=='male':
            BMR=88.362 + (13.397 * float(weight)) + (4.799 * float(height)) - (5.677 * float(age))
        else:
            BMR=447.593 + (9.247*float(weight)) + (3.098*float(height)) -(4.330*float(age))
        TDEE=BMR*float(activity)
        if goal=='loss':
            calories=TDEE*0.8
        elif goal=='maintain':
            calories=TDEE*1
        elif goal=='gain':
            calories=TDEE*1.2
        else:
            pass
        try:
            user=request.user
            UserDetails(username=user,age=age,height=height,weight=weight,gender=gender,BMR=BMR,daily_calories=calories).save()
            return render(request,'login.html',{'calories':calories})
        except:
            return render(request,'details.html',{
                'message':'fill all fields'
            })
    return render(request,'details.html')


@login_required
def foodview(request):
    food = Food.objects.all()
    details = UserDetails.objects.get(username=request.user)
    
    try:
        food_log = FoodLog.objects.filter(username=request.user)
        user_food = food_log.values_list('food_consumed', flat=True)
        
        total_calories = sum(log.food_consumed.calories * log.quantity for log in food_log)
        
        context = {
            'foods': food,
            'user_food': user_food,
            'details': details,
            'consumed_calories': total_calories,
            'daily_calories': details.daily_calories,
        }
        
        if details.daily_calories != 0:
            consumed_percentage = "{:.2f}".format((total_calories / details.daily_calories) * 100)
            context['consumed_percentage'] = consumed_percentage

        return render(request, 'food_view.html', context)
    except:
        context = {
            'foods': food,
            'details': details,
        }
        return render(request, 'food_view.html', context)
 
@login_required
def logout_view(request):
    logout(request)
    return redirect(user_login)

@login_required
def add_food(request,food_id):
    food = Food.objects.get(id=food_id)
    user=request.user
    foodlog=FoodLog.objects.filter(username=user,food_consumed=food_id)
    if foodlog.exists():
        foodlog.update(quantity=F('quantity')+1)
        print('added')
    else:    
        FoodLog(username=user,food_consumed=food,quantity=1).save()
    return redirect(foodview)

@login_required  
def delete_food(request,food_id):
    user=request.user
    try:
        foodlog=FoodLog.objects.get(username=user,food_consumed=food_id)
        if foodlog.quantity==1:
            foodlog.delete()
        else:
            FoodLog.objects.filter(username=user,food_consumed=food_id).update(quantity=F('quantity')-1)
    except:
        return redirect(foodview)
    return redirect(foodview)


'''def register(request):
    return render(request,"register.html")'''