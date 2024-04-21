from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from datetime import datetime , timedelta 
import random
from django.core.mail import send_mail
from django.conf import settings 

from post.models import Post, Follow, Stream
from django.contrib.auth.models import User
from authy.models import Profile
from .forms import EditProfileForm, UserRegisterForm
from django.urls import resolve
from comment.models import Comment
import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from .models import Profile

@login_required
def UserProfile(request, username):
    try:
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Proceed with the view logic
            Profile.objects.get_or_create(user=request.user)
            user = get_object_or_404(User, username=username)
            profile = Profile.objects.get(user=user)
            url_name = resolve(request.path).url_name
            posts = Post.objects.filter(user=user).order_by('-posted')

            if url_name == 'profile':
                posts = Post.objects.filter(user=user).order_by('-posted')
            else:
                posts = profile.favourite.all()

            # Profile Stats
            posts_count = Post.objects.filter(user=user).count()
            following_count = Follow.objects.filter(follower=user).count()
            followers_count = Follow.objects.filter(following=user).count()
            follow_status = Follow.objects.filter(following=user, follower=request.user).exists()

            # Pagination
            paginator = Paginator(posts, 8)
            page_number = request.GET.get('page')
            posts_paginator = paginator.get_page(page_number)

            context = {
                'posts': posts,
                'profile': profile,
                'posts_count': posts_count,
                'following_count': following_count,
                'followers_count': followers_count,
                'posts_paginator': posts_paginator,
                'follow_status': follow_status,
            }

            return render(request, 'profile.html', context)
        else:
            # User is not authenticated, render custom 404 page
            return render(request, '404.html', status=404)
    except ObjectDoesNotExist:
        # Profile does not exist, render custom 404 page
        return render(request, '404.html', status=404)

@login_required
def EditProfile(request):
    user = request.user.id
    profile = Profile.objects.get(user__id=user)

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            profile.image = form.cleaned_data.get('image')
            profile.first_name = form.cleaned_data.get('first_name')
            profile.last_name = form.cleaned_data.get('last_name')
            profile.location = form.cleaned_data.get('location')
            profile.url = form.cleaned_data.get('url')
            profile.bio = form.cleaned_data.get('bio')
            profile.save()
            return redirect('profile', profile.user.username)
    else:
        form = EditProfileForm(instance=request.user.profile)

    context = {
        'form':form,
    }
    return render(request, 'editprofile.html', context)

def follow(request, username, option):
    user = request.user
    following = get_object_or_404(User, username=username)

    try:
        f, created = Follow.objects.get_or_create(follower=request.user, following=following)

        if int(option) == 0:
            f.delete()
            Stream.objects.filter(following=following, user=request.user).all().delete()
        else:
            posts = Post.objects.all().filter(user=following)[:25]
            with transaction.atomic():
                for post in posts:
                    stream = Stream(post=post, user=request.user, date=post.posted, following=following)
                    stream.save()
        return HttpResponseRedirect(reverse('profile', args=[username]))

    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('profile', args=[username]))

# edit section


from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from .forms import UserRegisterForm

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                form.add_error('email', 'This email is already associated with an account.')
            else:
                new_user = form.save()
                username = form.cleaned_data.get('username')
                # messages.success(request, 'Hurray your account was created!!')

                # Automatically Log In The User
                new_user = authenticate(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password1'])
                login(request, new_user)
                return redirect('index')

    elif request.user.is_authenticated:
        return redirect('index')
    else:
        form = UserRegisterForm()
    context = {
        'form': form,
    }
    return render(request, 'signIn/sign-up.html', context)




def sign_in(request):
    remember_me_username = ''
    remember_me_password = ''
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        checked = request.POST.get("checked", False)
        print(checked)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if checked:
                request.session['username'] = username 
                request.session['password'] = password 
                print("ooooooooooooooooo")
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Incorrect username or password.")
    else:
        remember_me_username = request.session.get('username', '')  
        remember_me_password = request.session.get('password', '')  
        print("rem", remember_me_username)
        
    return render(request, 'signIn/sign-in.html', {'remember_me_username': remember_me_username ,'remember_me_password': remember_me_password})


def sign_out(request):
    logout(request)
    return redirect('sign-in')
    


def otpVerify(request):
    otp = request.session.get("otp")
    email = request.session.get("email")
    time = request.session.get("time")
    send_time = datetime.strptime(time , "%Y-%m-%d %H:%M:%S.%f")
    current_time = datetime.now()
    time_diff = current_time - send_time  
    print(otp , type(otp))
    if request.method == "POST":
        confirmOtp = int(request.POST.get("otp"))
        print(confirmOtp , type(confirmOtp))
        newPass = request.POST.get("newPass")
        confirmPass = request.POST.get("confirmPass")
        if otp == confirmOtp and newPass == confirmPass and time_diff <= timedelta(minutes =5):
            user = User.objects.get(email = email)
            user.set_password(newPass)
            user.save()
            user_login = authenticate(request , username = user.username , password = newPass)
            if user_login is not None:
                login(request , user_login)
                return redirect("sign-in")
            else:
                messages.error(request , " oops account not found !")
        elif otp != confirmOtp:
           messages.error(request , "invalid otp")
        elif newPass != confirmPass:
            messages.error(request , "password mismatch") 
        elif otp == confirmOtp and time_diff >= timedelta(minutes=5):
            messages.error(request , "otp expiries ")
        
            
    return render(request , 'signIn/otpVerify.html')

def forgotPass(request):
    if request.method == 'POST':
        email = request.POST.get("email") # name email from otpverify page
    # try:
        if User.objects.get(email = email):
            print("found")
            def generateOtp():
                return random.randint(1000 , 9999)
            otp = generateOtp()
            time = datetime.now()
            print("generated otp ", otp)
            # time.sleep(300)
            # print("new otp is" , otp)
            # send_mail("Your Otp " , f"your otp for reset the password:{otp} your otp expiries in 5 minutes " ,settings.EMAIL_HOST_USER,[email])
            message = f"your otp for reset the password:{otp} your otp expiries in 5 minutes "
            msg = MIMEMultipart()
            msg["From"] = settings.EMAIL_HOST_USER
            msg["To"] = email 
            msg["Subject"] = "Your Otp"
            msg.attach(MIMEText(message, "plain"))
            try:
                server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
                server.starttls()
                server.login(settings.EMAIL_HOST_USER , settings.EMAIL_HOST_PASSWORD)
                server.sendmail(settings.EMAIL_HOST_USER, email, msg.as_string())
                server.quit()
                print("email snd")
            except:
                print("error sending mail")
            request.session['otp'] = otp
            request.session['email'] = email
            request.session['time'] = str(time)
            return redirect('otpVerify')
        else:
            messages.warning(request , "Email doesnot exists")
    return render(request , 'signIn/forgotPass.html')


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate
from .models import Profile
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.conf import settings


@login_required
def settingsForm(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form_type = request.POST.get("formType")
        if form_type == "form2":  
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            sec_email = request.POST.get("sec_email")
            profile.email = email
            profile.phone_no = phone
            profile.sec_email = sec_email
            profile.save()
            messages.success(request, "Personal details updated successfully.")
            return redirect('settings')  # Redirect to the same page to avoid form resubmission prompt
        elif form_type == "form1":
            current_password = request.POST.get("current-password")
            new_password = request.POST.get("new-password")
            confirm_password = request.POST.get("confirm-password")
            password = authenticate(request, username=request.user.username, password=current_password)
            if password is not None:
                if new_password == confirm_password:
                    user = request.user
                    user.set_password(new_password)
                    user.save()

                    # Sending email notification with password reset link
                    
                    message = f"Your password has been successfully updated. if not by you reset your password immediately "
                    msg = MIMEMultipart()
                    msg["From"] = settings.EMAIL_HOST_USER
                    msg["To"] = user.email
                    msg["Subject"] = "Password Updated with Reset Link"
                    msg.attach(MIMEText(message, "plain"))

                    try:
                        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
                        server.starttls()
                        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                        server.sendmail(settings.EMAIL_HOST_USER, user.email, msg.as_string())
                        server.quit()
                        print("Email notification sent")
                    except Exception as e:
                        print("Error sending email notification:", str(e))

                    messages.success(request, "Password updated successfully. Check your email for further instructions.")
                    return redirect('settings')  # Redirect to the same page to avoid form resubmission prompt
                else:
                    messages.error(request, "Passwords do not match.")
            else:
                messages.error(request, "Incorrect current password.")
    return render(request, 'settings-form/settings.html', {"profile": profile})





def essay(request):
    return render(request , 'settings-form/essay.html')


