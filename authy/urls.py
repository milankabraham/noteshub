from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from authy.views import UserProfile, EditProfile
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    # Profile Section
    path('profile/edit', EditProfile, name="editprofile"),

    # User Authentication
    path('sign-up/', views.register, name="sign-up"),
    path('sign-in/', views.sign_in, name='sign-in'),
    path('sign-out/', views.sign_out, name='sign-out'), 
    path('forgotPass/',forgotPass,name="forgotPass"),
    path('otpVerify/',otpVerify,name="otpVerify"),
    path('settings/',settingsForm,name="settings"),
    path('essay/', essay, name='essay'),
    
]
