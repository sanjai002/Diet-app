
from django.db import IntegrityError
from django.shortcuts import render,redirect
from django.urls import path,reverse
from numpy import repeat
from django.http import HttpResponseRedirect,HttpResponse
from django.urls import reverse
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt




def index(request):
    food=Food.objects.all()[:5]
    return render(request,"index.html",{
        'food':food
    })


def food_list(request):
    # Pagination code
    ''' paginator = Paginator(foods, 10)
    page = request.GET.get('page')
    try:
        food_list = paginator.page(page)
    except PageNotAnInteger:
        food_list = paginator.page(1)
    except EmptyPage:
        food_list = paginator.page(paginator.num_pages)'''


        

    return render(request, 'food_list.html')


def food_details_view(request,food_id):

    foods=Food.objects.get(id=food_id)
    restaurants=Restaurant.objects.filter(food=food_id)
    print(restaurants)

    return render(request,"food_details.html",
                 {'food' : foods,
                  'restaurants':restaurants,  },
                  )

def search_food(request):
    foods=[]
    if 'q' in request.GET:
        search_query=request.GET['q']
        if search_query=='all':
            foods = Food.objects.all().order_by('food_name')
        else:
            foods = Food.objects.filter(food_name__icontains=search_query).order_by('food_name')
            

    data = [{
                'id': food.id,
                'food_name': food.food_name,
                'calories': food.calories,
                'protein': food.protein,
                'carbohydrates': food.carbohydrates,
                'fat': food.fat,
                'allergies': food.allergies,
                'category': [category.category_name for category in food.category.all()],
                'image': food.image.url
            } for food in foods]
    print("data is" , data)
    return JsonResponse({'data': data}, safe=False)



def user_login(request):
    previous_page = request.GET.get('next', None)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if previous_page:
                return redirect(previous_page)
            else:
                return redirect(index)
        else:
            return render(request,'login.html',
                          {
                              'message':'Wrong username or password'
                          })
    return render(request,'login.html',{
       
    })

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
        print("Age",age,"Gender",gender,"Height",height,"Weight",weight,"Activity",activity,"goal",goal)
        if gender=='male':
            BMR=88.362 + (13.397 * float(weight)) + (4.799 * float(height)) - (5.677 * float(age))
        else:
            BMR=447.593 + (9.247*float(weight)) + (3.098*float(height)) -(4.330*float(age))
        TDEE=BMR*float(activity)
        if goal=='lose':
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
            return redirect(index)
        except:
            return render(request,'details.html',{
                'message':'fill all fields'
            })
    return render(request,'details.html')



@login_required
def logout_view(request):
    logout(request)
    return redirect(index)

@login_required
def add_food(request,food_id):
    referring_page = request.META.get('HTTP_REFERER')
    food = Food.objects.get(id=food_id)
    user=request.user
    foodlog=FoodLog.objects.filter(username=user,food_consumed=food_id)
    if foodlog.exists():
        foodlog.update(quantity=F('quantity')+1)
        print('added')
    else:    
        FoodLog(username=user,food_consumed=food,quantity=1).save()
    return redirect(referring_page)

@login_required  
def delete_food(request,food_id):
    referring_page = request.META.get('HTTP_REFERER')
    user=request.user
    try:
        foodlog=FoodLog.objects.get(username=user,food_consumed=food_id)
        if foodlog.quantity==1:
            foodlog.delete()
        else:
            FoodLog.objects.filter(username=user,food_consumed=food_id).update(quantity=F('quantity')-1)
    except:
        return redirect(referring_page)
    return redirect(referring_page)





def blood_list(request):

    if request.method=='POST':
        group=request.POST['group']
        location=request.POST['location']
        donors=Blood.objects.filter(blood_group = group,location__icontains
                                         =location).order_by('name')
           
    else:
        donors=Blood.objects.all().order_by('blood_group')
        
    return render(request,"blood_register.html",{
            'bg_list':donors,})





@csrf_exempt
def blood_register(request):
    if request.method=='POST':
        name_=request.POST['name']
        blood_group=request.POST['blood_group']
        location=request.POST['location']
        mobile=request.POST['mobile']
        details=Blood(name=name_,blood_group=blood_group,location=location,mobile=mobile)
        details.save()
        return redirect(blood_list)
    else:
        return HttpResponse("Error! Please Try Again.")


@login_required
def get_user_and_food_info(request):
    food = Food.objects.all()
    user=request.user
    details = UserDetails.objects.get(username=user)
    
    try:
        
        food_log = FoodLog.objects.filter(username=user)
        user_food = food_log.values_list('food_consumed', flat=True)
        
        total_calories = sum(log.food_consumed.calories * log.quantity for log in food_log)
        
        context = {
            'foods': food,
            'food_log':food_log,
            'user_food': user_food,
            'details': details,
            'consumed_calories': total_calories,
            'daily_calories': details.daily_calories,
        }
        
        if details.daily_calories != 0:
            consumed_percentage = "{:.2f}".format((total_calories / details.daily_calories) * 100)
            context['consumed_percentage'] = consumed_percentage

        return context
    except:
        context = {
            'foods': food,
            'details': details,
        }
        return context


@login_required
def food_consumption(request):
    context=get_user_and_food_info(request)
    return render(request, 'calorie_view.html', context)

@login_required
def foodview(request):
    context=get_user_and_food_info(request)
    return render(request, 'food_view.html', context)
