from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login , logout

def notes_admin(request):
    if request.method == "POST":
        return admin_login(request)
    else:
        return render(request, "admin_login.html")

def dashboard(request):
    return render(request, "dashboard.html")

from django.contrib import messages

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("admin-email")
        password = request.POST.get("admin-pass")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('dashboard') 
            else:
                pass  
        else:
            # Authentication failed, display error message
            messages.error(request, "Incorrect username or password.")
    # Render the login page if no form submission or authentication failed
    return render(request, "admin_login.html")


def admin_logout(request):
    logout(request)
    return redirect(admin_login)
