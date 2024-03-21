
from multiprocessing import context
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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import joblib
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import io
from django.core.files.uploadedfile import InMemoryUploadedFile





diabetics_model = joblib.load('train/diabetes_prediction_model_svm.joblib')
heart_disease_model = pickle.load(open('train/heart-disease-prediction-knn-model.pkl','rb'))
nutrition_model= model = load_model('train/model.h5')  # Replace with the path to your model


def index(request):
    if request.user.is_authenticated and not request.user.is_superuser:
        User=UserDetails.objects.get(username=request.user)
        food=Food.objects.filter(goal=User.goal)
    else:
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
            if  request.user.is_authenticated and not request.user.is_superuser:
                User_=UserDetails.objects.get(username=request.user)
                foods = Food.objects.filter(goal=User_.goal).order_by('food_name')
            else:
                foods = Food.objects.all().order_by('food_name')
        else:
            if request.user.is_authenticated and not request.user.is_superuser:
                User_=UserDetails.objects.get(username=request.user)
                foods = Food.objects.filter(food_name__icontains=search_query,goal=User_.goal).order_by('food_name')
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
    categories=FoodCategory.objects.all().order_by('category_name')
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
        if goal=='Weight Loss':
            calories=TDEE*0.8
        elif goal=='Weight Maintain':
            calories=TDEE*1
        elif goal=='Weight Gain':
            calories=TDEE*1.2
        else:
            pass
        try:
            user=request.user
            UserDetails(username=user,age=age,height=height,weight=weight,gender=gender,BMR=BMR,BMI=BMI,daily_calories=calories,goal=goal).save()
            return redirect(index)
        except:
            return render(request,'details.html',{
                'message':'fill all fields'
            })
    return render(request,'details.html',{
        'categories':categories,
    })



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
    user=request.user
    details = UserDetails.objects.get(username=user)
    food = Food.objects.filter(goal=details.goal)
    
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
        if fbs>120:
            fbs_val=1
        else:
            fbs_val=0
        # Preprocess the input data
        input_data = np.array([[age,sex,cp,trestbps,chol,fbs_val,restecg,thalach,exang,oldpeak,slope,ca,thal]])
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

def article(request):
    all_articles = Article.objects.all()

    articles_per_page = 10
    paginator = Paginator(all_articles, articles_per_page)
    page_number = request.GET.get('page')

    try:
        articles_page = paginator.page(page_number)
    except PageNotAnInteger:
        articles_page = paginator.page(1)
    except EmptyPage:
        articles_page = paginator.page(paginator.num_pages)
    return render(request, 'articles.html', {'page_obj': articles_page})

def article_detail(request, article_id):
    article=Article.objects.get(id=article_id)
    other_articles = Article.objects.exclude(id=article_id)[:10]  # Exclude the current article and limit to 10
    return render(request, 'article_view.html', {'article': article, 'other_articles': other_articles})

def predict_image(request):

    if request.method == 'POST' and request.FILES.get('image'):
        # Load the trained model
        # Replace 'nutrition_model' with the actual name of your trained model variable
        
        # Handle the uploaded image
        uploaded_image = request.FILES['image']
        
        
            # Preprocess the image
        img = None
        if isinstance(uploaded_image, InMemoryUploadedFile):
                # If the uploaded image is in memory, convert it to bytes
            img_bytes = uploaded_image.read()
            img = image.load_img(io.BytesIO(img_bytes), target_size=(100, 100))
        else:
                # If the uploaded image is already a file, use its path
            img = image.load_img(uploaded_image, target_size=(100, 100))
            
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0  # Rescale pixel values to [0, 1]
        classes=['Iron Deficiency','No deficiency','Vitamin A Deficiency','Vitamin C Deficiency','Zinc Deficiency']
        prediction = nutrition_model.predict(img_array)
        predicted_class = np.argmax(prediction)
        result=classes[predicted_class]
        return JsonResponse({'message': result})


    else:
        # Handle GET requests or requests without an uploaded image
        return render(request, 'error_page.html')
