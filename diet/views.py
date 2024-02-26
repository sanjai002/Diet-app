
from django.db import IntegrityError
from django.shortcuts import render,redirect
from django.urls import path,reverse
import numpy as np
from django.http import HttpResponseRedirect,HttpResponse
from django.urls import reverse
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import joblib
import pickle


diabetics_model = joblib.load('train/diabetes_prediction_model_svm.joblib')
heart_disease_model = pickle.load(open('train/heart-disease-prediction-knn-model.pkl','rb'))
def index(request):
    food=Food.objects.all()
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



from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.urls import reverse

def user_login(request):
    next_page = request.GET.get('next')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print(next_page)
        if user is not None:
            login(request, user)            
            if next_page :
                return redirect(next_page)
            else:
                return redirect(reverse('index'))  # Redirect to index if 'next' is not valid
        else:
            return render(request, 'login.html', {'message': 'Wrong username or password','next': next_page})
    else:
        # Display login page
        return render(request, 'login.html', {'next': next_page})



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
        BMI=float((int(weight)/(((int(height))/100)**2)))
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
            UserDetails(username=user,age=age,height=height,weight=weight,gender=gender,BMR=BMR,BMI=BMI,daily_calories=calories).save()
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

@login_required
def disease_prediction(request):
    user=request.user
    details = UserDetails.objects.get(username=user)
    
    # Get the form data and
    return render(request,'disease_prediction.html',{
        'UserDetails':details,
    })
@login_required
def diabetes_detection(request):
    details=UserDetails.objects.filter(username=request.user).first()
    if request.method == 'POST':
        pregnancies = float(request.POST.get('pregnancies'))
        glucose = float(request.POST.get('glucose'))
        blood_pressure = float(request.POST.get('blood_pressure'))
        skin_thickness = float(request.POST.get('skin_thickness'))
        insulin = float(request.POST.get('insulin'))
        bmi = float(details.BMI)
        diabetes_pedigree_function = float(request.POST.get('diabetes_pedigree_function'))
        age=int(details.age)
        

        prediction = diabetics_model.predict(np.array([[pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, diabetes_pedigree_function, age]]))
        
        # Predict probability
        if prediction[0] == 1:
            prediction_result = "Diabetes detected"
            prediction_proba = diabetics_model.predict_proba(np.array([[pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, diabetes_pedigree_function, age]]))
            percentage_chance_diabetes = prediction_proba[0][1] * 100  # probability of class 1 (diabetes)
        else:
            prediction_result = "No Diabetes detected"
            percentage_chance_diabetes = 0  # probability of class 0 (not diabetes)
        
        # Get the percentage chance of diabetes
        return JsonResponse({
            'message': prediction_result, 
            'chance_diabetes': f'{percentage_chance_diabetes:.2f}%'
        })
    
@login_required   
def predict_heart_disease(request):
    details=UserDetails.objects.filter(username=request.user).first()
    if request.method == 'POST':
        age = int(details.age)
        sex = 1 if details.gender == 'male' else 0
        cp = int(request.POST.get('cp'))
        trestbps = int(request.POST.get('trestbps'))
        chol = int(request.POST.get('chol'))
        fbs = int(request.POST.get('fbs'))
        restecg = int(request.POST.get('restecg'))
        thalach = int(request.POST.get('thalach'))
        exang = int(request.POST.get('exang'))
        oldpeak = float(request.POST.get('oldpeak'))
        slope = int(request.POST.get('slope'))
        ca = int(request.POST.get('ca'))
        thal = int(request.POST.get('thal'))

        # Preprocess the input data
        input_data = np.array([[age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,ca,thal]])
        print(input_data)
        # Make prediction
        prediction = heart_disease_model.predict(input_data)
# 
        # Return the prediction result
        if prediction == 1:
            prediction_result = "Heart disease detected"
            prediction_proba = heart_disease_model.predict_proba(input_data)[0]
            percentage_chance = prediction_proba[1] * 100  # probability of class 1 (heart disease)
        else:
            prediction_result = "No heart disease detected"
            prediction_proba = heart_disease_model.predict_proba(input_data)[0]
            percentage_chance = 0  # probability of class 1 (heart disease)

        # Return the prediction result and the probability of heart disease
        return JsonResponse({
            'message': prediction_result, 
            'chance_heart_disease': f'{percentage_chance:.2f}%'
        })
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)