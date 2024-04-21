from django.shortcuts import render, redirect
from notification.models import Notification

def ShowNotification(request):
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-date')
    print(notifications)
    context = {
        'notifications': notifications,

    }
    return render(request, 'notifications/notification.html', context)


def delete_all_notifications(request):
    user = request.user
    Notification.objects.filter(user=user).delete()
    return redirect('show-notification')


def DeleteNotification(request, noti_id):
    print('noti_id')
    user = request.user
    notify = Notification.objects.filter(id=noti_id, user=user).delete()
    return redirect('show-notification')
