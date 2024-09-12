from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from .models import Users, UserProfile
from .forms import UserRegistrationForm
from .serializers import UserSerializer, UserProfileSerializer
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from shoppify.forms import UserRegistrationForm
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.db import connection
from django.http import JsonResponse
from django.template.loader import render_to_string



# Remove these lines as they are not necessary and might cause issues
# import sys
# import importlib
# from shoppify.forms import UserRegistrationForm


# Rest of your code follows...
# Potential issues:
# 1. Some imports are repeated (e.g., Response, render)
# 2. Unused imports (e.g., HttpResponse, JsonResponse, serializers, generics)
# 3. Missing import for 'redirect' function used in user_login view
# Create your views here.
class UsersProfile:
    # 1. list all
    def get(self, request, *args, **kwargs):
        '''
        List all the todo items for given requested user
        '''
        todos = Users.objects.filter(user = request.user.id)
        serializer = UserSerializer(todos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # 2. create 
    def post(self, request, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''
        data = {
            'task': request.data.get('task'),
            'completed': request.data.get('completed'),
            'user': request.user.id
        }
        serializer = UserSerializer(data=data)
        if serializer.is_valid():  # Add validation check
            serializer.save()  # Save the serializer if valid
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])

def user_login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            return render(request, 'login.html', {
                'error': 'Please provide both username and password'
            })
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home page after login
        else:
            return render(request, 'login.html', {
                'error': 'Invalid username or password'
            })
        #Potential issues:
# 1. Using request.POST instead of request.data (for DRF views)
# 2. Mixing DRF decorators with Django render responses
# 3. 'redirect' is used but not imported
# 4. Inconsistent return types (redirect vs render)
def login_page(request):
    return HttpResponse ("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-12 col-md-9 col-lg-7 col-xl-6">
                <div class="card" style="border-radius: 15px;">
                    <div class="card-body p-5">
                        <h2 class="text-uppercase text-center mb-5">Login</h2>
                        {% if messages %}
                            {% for message in messages %}
                                <div class="alert alert-{{ message.tags }}">
                                    {{ message }}
                                </div>
                            {% endfor %}
                        {% endif %}
                        <form method="post" action="{% url 'login' %}">
                            {% csrf_token %}
                            <div class="form-outline mb-4">
                                <input type="text" id="username" class="form-control form-control-lg" name="username" required />
                                <label class="form-label" for="username">Your Username</label>
                            </div>
                            <div class="form-outline mb-4">
                                <input type="password" id="password" class="form-control form-control-lg" name="password" required />
                                <label class="form-label" for="password">Password</label>
                            </div>
                            <div class="d-flex justify-content-center">
                                <button type="submit" class="btn btn-success btn-block btn-lg gradient-custom-4 text-white">Login</button>
                            </div>
                            <p class="text-center text-muted mt-5 mb-0">Don't have an account? <a href="{% url 'register' %}" class="fw-bold text-body"><u>Register here</u></a></p>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    """)

@csrf_exempt    
 #CSRF (Cross-Site Request Forgery) protection is handled for the view it decorates. 
# This means that POST requests to this view will be accepted even without a valid CSRF token.
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.data)
        if form.is_valid():
            user = form.save()
            username = user.username
            email = user.email
            
            try:
                # Send email
                send_mail(
                    'Account Created',
                    f'Your account has been created successfully, {username}!',
                    'from@example.com',
                    [email],
                    fail_silently=False,
                )
                
                messages.success(request, f'Account created for {username}! You can now log in.')
                return redirect('login')
            
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})

def register_page(request):
    return HttpResponse("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-12 col-md-9 col-lg-7 col-xl-6">
                <div class="card" style="border-radius: 15px;">
                    <div class="card-body p-5">
                        <h2 class="text-uppercase text-center mb-5">Register</h2>
                        
                        {% if messages %}
                            <ul class="list-unstyled">
                                {% for message in messages %}
                                    <li class="alert alert-{{ message.tags }}">
                                        {{ message }}
                                    </li>
                                {% endfor %}
                            </ul>
                        {% endif %}
                        
                        <form method="POST" action="{% url 'register' %}">
                            {% csrf_token %}
                            <div class="form-outline mb-4">
                                <input type="text" id="username" class="form-control form-control-lg" name="username" required />
                                <label class="form-label" for="username">Your Username</label>
                            </div>
                            <div class="form-outline mb-4">
                                <input type="text" id="email" class="form-control form-control-lg" name="email" required />
                                <label class="form-label" for="email">Your Email</label>
                            </div>
                            <div class="form-outline mb-4">
                                <input type="password" id="password" class="form-control form-control-lg" name="password" required />
                                <label class="form-label" for="password">Password</label>
                            </div>
                            <div class="d-flex justify-content-center">
                                <button type="submit" class="btn btn-success btn-block btn-lg gradient-custom-4 text-white">Register</button>
                            </div>
                            <p class="text-center text-muted mt-5 mb-0">Already have an account? <a href="{% url 'login' %}" class="fw-bold text-body"><u>Login here</u></a></p>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>

    """)





    # 3. test end point 
@api_view(['GET', 'POST', 'DELETE'])
def UserProfile(request):
        #to get todos
        if request.method == 'GET':
            users = Users.objects.all()
            serializer = UserSerializer(Users, many=True)
            return Response(serializer.data)

            #create todo
        elif request.method == 'POST':
            request_data = JSONParser().parse(request)    
            serializer = UserSerializer(data=request_data)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            completedUsers = Users.objects.filter(completed=True)
            if completedUsers.count() > 0:
                completedUsers.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)  

        # Potential issues:
# 1. In GET method, serializer is called with Users (model) instead of users (queryset)
# 2. POST method doesn't check if serializer is valid before saving
# 3. Inconsistent naming (UserProfile vs UsersProfile)
# 4. 'completed' field used in DELETE method may not exist in Users model

class Profile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            # Assuming you have a UserProfile model linked to User
            # If not, you can just use the User model directly
            profile = user.userprofile
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        user = request.user
        try:
            profile = user.userprofile
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)
       

    def add_item(request):
        if request.method == 'POST':
           form = YourModelForm(request.POST)
           if form.is_valid():
               form.save()
               return redirect('success_page')
        else:
           form = YourModelForm()
        return render(request, 'register.html', {'form': form})