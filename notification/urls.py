from django.urls import path
from notification.views import ShowNotification, DeleteNotification
from .views import *

urlpatterns = [
    path('', ShowNotification, name='show-notification'),
    path('<noti_id>/delete', DeleteNotification, name='delete-notification'),
    path('notifications/delete-all/', delete_all_notifications, name='delete-all-notifications'),


]
