from django.urls import path
from . import views
from .views import Profile

urlpatterns = [
    path("details/", Profile.as_view()),  # Added a trailing slash
    path('profile/', Profile.as_view(), name='profile'),
]