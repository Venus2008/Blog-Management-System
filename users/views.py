from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password,check_password
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.mail import send_mail
signer = TimestampSigner()
import re
from myapp.models import Users
from myapp.constants import RoleChioice


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}+$'
    return re.match(pattern, email) is not None

def register(request):
    if request.method == 'POST':
        email=request.POST.get('email')
        username=request.POST.get('username')
        raw_password=request.POST.get('password')
        role=request.POST.get('role')

        trimmed=username.strip()
        if not len(trimmed)>0:
            messages.error(request,'Username coul not be blank')
            return redirect('signup')

        if not is_valid_email(email):
            messages.error(request, 'Invalid Email Format')
            return redirect('signup')

        if Users.objects.filter(email=email).exists():
            messages.error(request, 'User Already exists')
            return redirect('login')
        
        hashed_password=make_password(raw_password)
        user=Users(email=email,username=username,password=hashed_password,role=role,is_active=True)
        user.save()
        messages.success(request,'User register successfully')
        return redirect('login')
    
    return render(request, 'users/registration.html',{'roles':RoleChioice.choices})


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        raw_password = request.POST.get('password')

        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            messages.error(request, 'User does not exist')
            return redirect('login')

        # check password
        if check_password(raw_password, user.password):

            # check if user is active before logging in
            if not user.is_active:
                messages.error(request, 'User is inactive. Contact Admin.')
                return redirect('login')

            # login success
            request.session['frontend_user_id'] = user.id
            messages.success(request, 'Login successful')

            # role-based redirect
            if user.role == 'ADMIN':
                return redirect('adminside')
            else:
                return redirect('index')

        else:
            messages.error(request, 'Invalid email or password')
            return redirect('login')

    return render(request, 'users/login.html')


def logout(request):
    request.session.pop('frontend_user_id',None)
    messages.success(request,'Logout Successfully')
    return redirect('login')


def password_reset_request(request):
    if request.method == 'POST':
        email=request.POST.get('email')

        try:
            user=Users.objects.get(email=email)
        except Users.DoesNotExist:
            messages.error(request, 'No account found with the email')
            return redirect('password_reset_request')
        
        token=signer.sign(str(user.id))

        reset_link=request.build_absolute_uri( f"/reset-password/{token}/")

        send_mail(
            subject="Reset Your Password",
            message=f"Click here to reset your password: {reset_link}",
            from_email="venuskh.tagline@gmail.com",
            recipient_list=[email],
        )

        messages.success(request, "We sent you a reset link! Check your email.")
        return redirect('login')
    return render(request, "users/password_reset.html")


def reset_password(request,token):
    try:
        user_id=signer.unsign(token, max_age=600)
        user=Users.objects.get(id=user_id)
    except (BadSignature,SignatureExpired, Users.DoesNotExist):
         messages.error(request, "Invalid or expired link.")
         return redirect('password_reset_request')
    
    if request.method == 'POST':
        new_password = request.POST.get("password")
        user.password = make_password(new_password)
        user.save()
        messages.success(request, 'Password Reset Successfully')
        return redirect('login')
    return render(request,"users/reset_password.html", {"user": user})
