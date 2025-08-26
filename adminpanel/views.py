from django.shortcuts import render,redirect,get_object_or_404
from myapp.models import Users,Blog,Comment
from django.contrib import messages
from myapp.constants import RoleChioice
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from django.views.decorators.cache import cache_control
import re
from myapp.decorators import role_required,login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator




def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}+$'
    return re.match(pattern, email) is not None


@method_decorator(
    [
        role_required("ADMIN"),
        login_required,
        cache_control(no_cache=True, must_revalidate=True, no_store=True),
    ],
    name="dispatch",
)
class AdminPageView(View):
    template_name='adminpanel/dashboard.html'

    def get(self,request):
        total_users = Users.objects.count()
        total_blogs = Blog.objects.count()
        total_comments = Comment.objects.count()

        return render(request, self.template_name, {
            'total_users': total_users,
            'total_blogs': total_blogs,
            'total_comments': total_comments,
        })
    

@method_decorator(
    [
        role_required("ADMIN"),
        login_required,
        cache_control(no_cache=True, must_revalidate=True, no_store=True),
    ],
    name="dispatch",
)
class AdminUsersView(View):
    template_name='adminpanel/users.html'

    def get(self,request):
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

        return render (request,self.template_name,{'users':page_obj,'q':q})


@method_decorator(
    [
        role_required("ADMIN"),
        login_required,
        cache_control(no_cache=True, must_revalidate=True, no_store=True),
    ],
    name="dispatch",
)
class AdminAddUser(View):
    template_name='adminpanel/add_user.html'

    def get(self,request):
         return render(request,self.template_name,{'roles':RoleChioice.choices})
    
    def post(self,request,*args, **kwargs):
        username=(request.POST.get("username") or "").strip()
        email = (request.POST.get("email") or "").strip()
        raw_password = request.POST.get("password") or ""
        role = request.POST.get("role")

        if not username:
            messages.error(request, 'Username cannot be blank')
            return redirect('admin_add_user')
        
        if not is_valid_email(email):
            messages.error(request, 'Invalid Email Format')
            return redirect('admin_add_user')
        
        if Users.objects.filter(email=email).exists():
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
    

@method_decorator(
    [
        role_required("ADMIN"),
        login_required,
        cache_control(no_cache=True, must_revalidate=True, no_store=True),
    ],
    name="dispatch",
)
class AdminEditUser(View):
    template_name='adminpanel/edit_user.html'
    paginate_by=6

    def get(self,request,user_id):
        obj=get_object_or_404(Users,id=user_id)
        return render(request, 'admin/edit_user.html', {'user_obj':obj,'roles':RoleChioice.choices})
    
    def post(self,request,user_id,*args, **kwargs):
        obj=get_object_or_404(Users,id=user_id)
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
    

@method_decorator(
    [
        role_required("ADMIN"),
        login_required,
        cache_control(no_cache=True, must_revalidate=True, no_store=True),
    ],
    name="dispatch",
)
class AdminDeleteUser(View):
    def post(self, request, user_id):
        current_admin_id = request.session.get('frontend_user_id')
        obj = get_object_or_404(Users, id=user_id)

        if obj.id == current_admin_id:
            messages.error(request, "You cannot delete your own admin account.")
            return redirect('admin_users')

        obj.delete()
        messages.success(request, "User deleted successfully.")
        return redirect('admin_users')

    def get(self, request, *args, **kwargs):
        messages.error(request, "Invalid request method.")
        return redirect('admin_users')


@method_decorator(
    [
        role_required("ADMIN"),
        login_required,
        cache_control(no_cache=True, must_revalidate=True, no_store=True),
    ],
    name="dispatch",
)
class AdminBlogs(View):
    template_name='adminpanel/blogs.html'

    def get(self,request):
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

        return render (request,self.template_name,{'blogs':page_obj,'q':q})
    

@method_decorator(
    [
        role_required("ADMIN"),
        login_required,
        cache_control(no_cache=True, must_revalidate=True, no_store=True),
    ],
    name="dispatch",
)
class AdminEditBlogs(View):
    template_name='adminpanel/edit_blogs.html'

    def get(self,request,blog_id):
        obj=get_object_or_404(Blog,id=blog_id)
        return render(request,self.template_name,{'blog':obj})
    
    def post(self,request,blog_id):
        obj=get_object_or_404(Blog,id=blog_id)
        title=(request.POST.get('title')or "").strip()
        content=(request.POST.get('content')or "").strip()
        image=request.FILES.get('image')

        if not title:
            messages.error(request,'Title cannot be empty')
            return redirect('admin_edit_blogs',blog_id=obj.id)
        
        if not content:
           messages.error(request,'Content cannot be empty')
           return redirect('admin_edit_blogs',blog_id=obj.id) 

        obj.title=title
        obj.content=content
        if image:
            obj.image=image
        obj.save()

        messages.success(request,'Blog Edited Successfully')
        return redirect('admin_blogs')


@method_decorator(
    [
        role_required("ADMIN"),
        login_required,
        cache_control(no_cache=True, must_revalidate=True, no_store=True),
    ],
    name="dispatch",
)
class AdminDeleteBlogs(View):
    def post(self,request,blog_id):
        obj=get_object_or_404(Blog,id=blog_id)
        obj.delete()
        messages.success(request, 'Blog Deleted Successfully')
        return redirect('admin_blogs')

    def get(self,request,blog_id):
        messages.error(request,'Invalid request method')
        return redirect('admin_blogs')


@method_decorator(
    [
        role_required("ADMIN"),
        login_required,
        cache_control(no_cache=True, must_revalidate=True, no_store=True),
    ],
    name="dispatch",
)
class AdminComments(View):
    template_name='adminpanel/comments.html'

    def get(self,request):
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


@method_decorator(
    [
        role_required("ADMIN"),
        login_required,
        cache_control(no_cache=True, must_revalidate=True, no_store=True),
    ],
    name="dispatch",
)
class AdminEditComments(View):
    template_name='adminpanel/edit_comments.html'

    def get(self,request,comment_id):
        obj=get_object_or_404(Comment,id=comment_id)
        return render(request,self.template_name,{'comment':obj})
    
    def post(self,request,comment_id):
        obj=get_object_or_404(Comment,id=comment_id)
        content=(request.POST.get('content')or"").strip()

        if not content:
            messages.error(request,"Comment cannot be blank")
            return redirect('admin_edit_comments')
        
        obj.content=content
        obj.save()
        messages.success(request,"Comment Edited Successfully")
        return redirect('admin_comments')


@method_decorator(
    [
        role_required("ADMIN"),
        login_required,
        cache_control(no_cache=True, must_revalidate=True, no_store=True),
    ],
    name="dispatch",
)
class AdminDeleteComments(View):
    def post(self,request,comment_id):
        obj=get_object_or_404(Comment,id=comment_id)
        obj.delete()
        messages.success(request, 'Comment Deleted Successfully')
        return redirect('admin_comments')

    def get(self,request,comment_id):
        messages.error(request,'Invalid request method')
        return redirect('admin_comments')

