from django.shortcuts import render,redirect,get_object_or_404
from myapp.models import Users,Blog,Comment
from django.contrib import messages
from django.contrib.auth.hashers import make_password,check_password
from .decorators import login_required,role_required
from .constants import RoleChioice
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.mail import send_mail
signer = TimestampSigner()
from django.db.models import Case, When, BooleanField
from myapp.decorators import get_logged_in_user
import re
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_control
from django.db.models import Q


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}+$'
    return re.match(pattern, email) is not None

# ---------------------------------------- Admin Pages ----------------------------------
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@role_required('ADMIN')
@login_required
def admin_page(request):
    total_users = Users.objects.count()
    total_blogs = Blog.objects.count()
    total_comments = Comment.objects.count()

    return render(request, 'admin/dashboard.html', {
        'total_users': total_users,
        'total_blogs': total_blogs,
        'total_comments': total_comments,
    })



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@role_required('ADMIN')
@login_required
def admin_users(request):
    q = request.GET.get('q', '').strip()
    users_qs=Users.objects.all().order_by('-id')
    if q:
        users_qs=users_qs.filter(
            Q(username__icontains=q)|
            Q(email__icontains=q) |
            Q(role__icontains=q)
        )
    paginator=Paginator(users_qs,10)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)

    return render (request,'Admin/users.html',{'users':page_obj,'q':q})



@role_required('ADMIN')
@login_required
def admin_add_user(request):
    if request.method == 'POST':
        username=(request.POST.get("username") or "").strip()
        email = (request.POST.get("email") or "").strip()
        raw_password = request.POST.get("password") or ""
        role = request.POST.get("role")

        #Validations
        if not username:
            messages.error(request, 'Username cananot be blank')
            return redirect('admin_add_user')
        
        if not is_valid_email(email):
            messages.error(request, 'Invalid Email Format')
            return redirect('admin_add_user')
        
        if Users.objects.filter(email=email):
            messages.error(request, 'Email already exists')
            return redirect('admin_add_user')
        
        if not raw_password:
            messages.error(request, 'Password is required')
            return redirect('admin_add_user')
        
        if not role:
            messages.error(request, 'Role is required')
            return redirect('admin_add_user')

        user=Users.objects.create(
            username=username,
            email=email,
            password=make_password(raw_password),
            role=role,
            is_active=True,
        )
        messages.success(request, f"Users '{user.email}' added successfully ")
        return redirect('admin_users')
    return render(request,'admin/add_user.html',{'roles':RoleChioice.choices})



@role_required('ADMIN')
@login_required
def admin_edit_user(request,user_id):
    obj=get_object_or_404(Users,id=user_id)
    if request.method == 'POST':
        username = (request.POST.get("username") or "").strip()
        email = (request.POST.get("email") or "").strip()
        raw_password = request.POST.get("password") or ""
        role = request.POST.get("role")
        is_active = True if request.POST.get("is_active") == "on" else False

        if not username:
            messages.error(request, 'Username cananot be blank')
            return redirect('admin_add_user',user_id=obj.id)
        
        if not is_valid_email(email):
            messages.error(request, 'Invalid Email Format')
            return redirect('admin_add_user',user_id=obj.id)
        
        if Users.objects.exclude(id=obj.id).filter(email=email).exists():
            messages.error(request, "Email already in use by another user.")
            return redirect('admin_edit_user', user_id=obj.id)

        obj.username = username
        obj.email = email
        obj.role = role
        obj.is_active = is_active
        if raw_password:
            obj.password = make_password(raw_password)
        obj.save()
        messages.success(request, 'User Updated Successfully')
        return redirect('admin_users')
    return render(request, 'admin/edit_user.html', {'user_obj':obj,'roles':RoleChioice.choices})



@role_required('ADMIN')
@login_required
def admin_delete_user(request, user_id):
    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('admin_users')

    current_admin_id = request.session.get('frontend_user_id')
    obj = get_object_or_404(Users, id=user_id)

    # prevent accidental self-delete
    if obj.id == current_admin_id:
        messages.error(request, "You cannot delete your own admin account.")
        return redirect('admin_users')

    obj.delete()
    messages.success(request, "User deleted successfully.")
    return redirect('admin_users')


@role_required('ADMIN')
@login_required
def admin_blogs(request):
    q = request.GET.get('q','').strip()
    blog_qs=Blog.objects.all().order_by('-created_at')
    if q:
        blog_qs=blog_qs.filter(
            Q(title__icontains=q)|
            Q(author__username__icontains=q)|
            Q(author__email__icontains=q)
        )
    paginator=Paginator(blog_qs,10)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)

    return render (request,'Admin/blogs.html',{'blogs':page_obj,'q':q})
    


@role_required('ADMIN')
@login_required
def admin_edit_blogs(request,blog_id):
    obj=get_object_or_404(Blog,id=blog_id)

    if request.method == 'POST':
        title=(request.POST.get('title')or "").strip()
        content=(request.POST.get('content')or "").strip()
        image=request.FILES.get('image')

        if not title:
            messages.error(request,'Title cannot be empty')
            return redirect('admin_edit_blogs')
        
        if not content:
           messages.error(request,'Content cannot be empty')
           return redirect('admin_edit_blogs') 

        obj.title=title
        obj.content=content
        if image:
            obj.image=image
        obj.save()

        messages.success(request,'Blog Edited Successfully')
        return redirect('admin_blogs')
    return render(request,'Admin/edit_blogs.html',{'blog':obj})



@role_required('ADMIN')
@login_required
def admin_delete_blog(request,blog_id):
    if not request.method == 'POST':
        messages.error(request,'Invalid request method')
        return redirect('admin_blogs')
    
    obj=get_object_or_404(Blog,id=blog_id)
    obj.delete()
    messages.success(request, 'Blog Deleted Successfully')
    return redirect('admin_blogs')



@role_required('ADMIN')
@login_required
def admin_comments(request):
    q=request.GET.get('q','').strip()
    comment_qs=Comment.objects.all().order_by('-created_at')
    if q:
        comment_qs=comment_qs.filter(
            Q(content__icontains=q)|
            Q(author__username__icontains=q)|
            Q(author__email__icontains=q)
        )
    paginator=Paginator(comment_qs,10)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)

    return render(request,'Admin/comments.html',{'comments':page_obj,'q':q})



@role_required('ADMIN')
@login_required
def admin_edit_comments(request,comment_id):
    obj=get_object_or_404(Comment,id=comment_id)

    if request.method == 'POST':
        content=(request.POST.get('content')or"").strip()

        if not content:
            messages.error(request,"Comment cannot be blank")
            return redirect('admin_edit_comments')
        
        obj.content=content
        obj.save()
        messages.success(request,"Comment Edited Successfully")
        return redirect('admin_comments')
    return render(request,'Admin/edit_comments.html',{'comment':obj})



@role_required('ADMIN')
@login_required
def admin_delete_comments(request,comment_id):
    if not request.method == 'POST':
        messages.error(request,'Invalid request method')
        return redirect('admin_blogs')
    
    obj = get_object_or_404(Comment, id=comment_id)
    obj.delete()
    messages.success(request, "Comment deleted successfully.")
    return redirect('admin_comments')


# ---------------------------------------- Login/Signin Page ----------------------------------

# def register(request):
#     if request.method == 'POST':
#         email=request.POST.get('email')
#         username=request.POST.get('username')
#         raw_password=request.POST.get('password')
#         role=request.POST.get('role')

#         trimmed=username.strip()
#         if not len(trimmed)>0:
#             messages.error(request,'Username coul not be blank')
#             return redirect('signup')

#         if not is_valid_email(email):
#             messages.error(request, 'Invalid Email Format')
#             return redirect('signup')

#         if Users.objects.filter(email=email).exists():
#             messages.error(request, 'User Already exists')
#             return redirect('login')
        
#         hashed_password=make_password(raw_password)
#         user=Users(email=email,username=username,password=hashed_password,role=role,is_active=True)
#         user.save()
#         messages.success(request,'User register successfully')
#         return redirect('login')
    
#     return render(request, 'registration.html',{'roles':RoleChioice.choices})


# def login(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         raw_password = request.POST.get('password')

#         try:
#             user = Users.objects.get(email=email)
#         except Users.DoesNotExist:
#             messages.error(request, 'User does not exist')
#             return redirect('login')

#         # check password
#         if check_password(raw_password, user.password):

#             # check if user is active before logging in
#             if not user.is_active:
#                 messages.error(request, 'User is inactive. Contact Admin.')
#                 return redirect('login')

#             # login success
#             request.session['frontend_user_id'] = user.id
#             messages.success(request, 'Login successful')

#             # role-based redirect
#             if user.role == 'ADMIN':
#                 return redirect('adminside')
#             else:
#                 return redirect('index')

#         else:
#             messages.error(request, 'Invalid email or password')
#             return redirect('login')

#     return render(request, 'login.html')


# def logout(request):
#     request.session.pop('frontend_user_id',None)
#     messages.success(request,'Logout Successfully')
#     return redirect('login')


# def password_reset_request(request):
#     if request.method == 'POST':
#         email=request.POST.get('email')

#         try:
#             user=Users.objects.get(email=email)
#         except Users.DoesNotExist:
#             messages.error(request, 'No account found with the email')
#             return redirect('password_reset_request')
        
#         token=signer.sign(str(user.id))

#         reset_link=request.build_absolute_uri( f"/reset-password/{token}/")

#         send_mail(
#             subject="Reset Your Password",
#             message=f"Click here to reset your password: {reset_link}",
#             from_email="venuskh.tagline@gmail.com",
#             recipient_list=[email],
#         )

#         messages.success(request, "We sent you a reset link! Check your email.")
#         return redirect('login')
#     return render(request, "password_reset.html")


# def reset_password(request,token):
#     try:
#         user_id=signer.unsign(token, max_age=600)
#         user=Users.objects.get(id=user_id)
#     except (BadSignature,SignatureExpired, Users.DoesNotExist):
#          messages.error(request, "Invalid or expired link.")
#          return redirect('password_reset_request')
    
#     if request.method == 'POST':
#         new_password = request.POST.get("password")
#         user.password = make_password(new_password)
#         user.save()
#         messages.success(request, 'Password Reset Successfully')
#         return redirect('login')
#     return render(request,"reset_password.html", {"user": user})


# ---------------------------------------- Blog Pages ----------------------------------


# def entry_page(request):
#     return render(request, 'entry_page.html')


# def guest_blog_list(request):
#     blogs = Blog.objects.all().order_by('-created_at')
#     paginator = Paginator(blogs, 6)  
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     return render(request, 'guest_blog_list.html', {'blogs': page_obj})


# @role_required('ADMIN','USER','STAFF')
# @login_required
# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# def index(request):  
#     user = get_logged_in_user(request)
#     return render(request,'index.html', {'user':user})



# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# @role_required('ADMIN','USER','STAFF')
# @login_required
# def add_blogs(request):
#     user = get_logged_in_user(request)
#     if request.method == 'POST':
#         title=request.POST.get('title')
#         content=request.POST.get('content')
#         image=request.FILES.get('image')
#         author=user

#         Blog.objects.create(
#             title=title,
#             content=content,
#             image=image,
#             author=author,
#         )
#         messages.success(request,'New Blog Added Successfully')
#         return redirect('blog_list')

#     user_blogs=Blog.objects.filter(author=user).order_by('-created_at')
#     return render(request,'Addblogs.html',{'user':user,'blogs':user_blogs,'is_edit':False,'blog':None})



# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# @login_required
# @role_required('ADMIN','USER','STAFF')
# def blog_list(request):
#     user = get_logged_in_user(request)

#     blogs=Blog.objects.annotate(
#         is_author=Case(
#             When(author=user,then=True),
#             default=False,
#             output_field=BooleanField(),
#         )
#     ).order_by('-is_author','-created_at')
#     paginator = Paginator(blogs, 6)  
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     return render(request, 'blog_list.html', {'blogs':page_obj,'user':user})



# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# @role_required('ADMIN','USER','STAFF')
# @login_required
# def edit_blog(request,id):
#     user = get_logged_in_user(request)
#     blog=get_object_or_404(Blog,author=user,id=id)

#     if request.method == 'POST':
#         title=request.POST.get('title')
#         content=request.POST.get('content')
#         image=request.FILES.get('image')

#         blog.title=title
#         blog.content=content
#         if image:
#             blog.image=image
#         blog.save()

#         messages.success(request,'Blog Updated Successfully')
#         return redirect('blog_list')
#     user_blogs=Blog.objects.filter(author=user).order_by('-created_at')
#     return render(request,'Addblogs.html', {'blog': blog,'blogs':user_blogs,'is_edit':True,'user':user})



# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# @role_required('ADMIN','USER','STAFF')
# @login_required
# def delete_blog(request,id):
#     user = get_logged_in_user(request)
#     blog=get_object_or_404(Blog,id=id,author=user)
#     blog.delete()
#     return redirect('blog_list')



# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# @role_required('ADMIN','USER','STAFF')
# @login_required
# def add_comment(request,id):
#     user=get_logged_in_user(request)
#     blog=get_object_or_404(Blog,id=id)
#     if request.method == 'POST':
#         content=request.POST.get('content')

#         if not content.strip():
#             messages.error(request,'Comment cannot be Empty')
#             return redirect('blog_list')
        
#         Comment.objects.create(
#             blog=blog,
#             author=user,
#             content=content,
#         )
#         messages.success(request,"Comment added successfully")
#         return redirect('blog_list')
    
#     return redirect('blog_list')
