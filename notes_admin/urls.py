from django.urls import path
from .views import *

urlpatterns = [
    path('', notes_admin, name='notes_admin'),
    path('dashboard/', dashboard, name='dashboard'),
    path('admin_login/', admin_login, name='admin_login'),
    path('admin_logout',admin_logout , name='admin_logout' ),
]
