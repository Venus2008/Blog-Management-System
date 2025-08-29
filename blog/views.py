from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import TemplateView
from django.views import View
from blog.models import Blog,Comment
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from blog.decorators import role_required,login_required,get_logged_in_user
from django.views.decorators.cache import cache_control
from django.contrib import messages
from django.db.models import Case, When, BooleanField
from django.core.paginator import Paginator



class EntryPageView(TemplateView):
    template_name = "blog/entry_page.html"


class GuestBlogListView(ListView):
    template_name='blog/guest_blog_list.html'
    model=Blog
    context_object_name='blogs'
    paginate_by=6
    ordering=["-created_at"]


@method_decorator(
    [
        role_required("ADMIN", "USER", "STAFF"),
        login_required,
        cache_control(no_cache=True, must_revalidate=True, no_store=True),
    ],
    name="dispatch",
)
class IndexView(View):
    template_name = "blog/index.html"

    def get(self, request, *args, **kwargs):
        user = get_logged_in_user(request)
        return render(request, self.template_name, {"user": user})


@method_decorator(
    [
        role_required("ADMIN", "USER", "STAFF"),
        login_required,
        cache_control(no_cache=True, must_revalidate=True, no_store=True),
    ],
    name="dispatch",
)
class AddBlogView(View):
    template_name="blog/Addblogs.html"

    def get(self,request,*args, **kwargs):
        user=get_logged_in_user(request)
        user_blog=Blog.objects.filter(author=user).order_by('-created_at')
        return render (request,self.template_name,{'user':user,'blog':user_blog,'is_edit':False,'blog':None})
    
    def post(self,request,*args, **kwargs):
        user=get_logged_in_user(request)
        title=request.POST.get('title')
        content=request.POST.get('content')
        image=request.FILES.get('image')

        Blog.objects.create(
            title=title,
            content=content,
            image=image,
            author=user,
        )
        messages.success(request,'New Blog Added Successfully')
        return redirect('blog_list')
    

@method_decorator(
    [
        role_required("ADMIN", "USER", "STAFF"),
        login_required,
        cache_control(no_cache=True, must_revalidate=True, no_store=True),
    ],
    name="dispatch",
)
class BlogListView(View):
    template_name="blog/blog_list.html"
    paginated_by=6
    def get(self,request,*args, **kwargs):
        user = get_logged_in_user(request)    
        blogs=Blog.objects.annotate(
            is_author=Case(
                When(author=user,then=True),
                default=False,
                output_field=BooleanField(),
            )
        ).order_by('-is_author','-created_at')
        paginator=Paginator(blogs,self.paginated_by)
        page_number=request.GET.get('page')
        page_obj=paginator.get_page(page_number)
        return render (request,self.template_name,{'blogs':page_obj,'user':user})
        

@method_decorator(
    [
        role_required("ADMIN", "USER", "STAFF"),
        login_required,
        cache_control(no_cache=True, must_revalidate=True, no_store=True),
    ],
    name="dispatch",
)
class EditBlogView(View):
    template_name="blog/Addblogs.html"

    def get(self,request,*args, **kwargs,):
        user=get_logged_in_user(request)
        blog_id = kwargs.get("id")
        blog=get_object_or_404(Blog,author=user,id=blog_id)
        user_blogs=Blog.objects.filter(author=user).order_by('-created_at')
        return render(request,self.template_name, {'blog': blog,'blogs':user_blogs,'is_edit':True,'user':user})
    
    def post(self,request,*args, **kwargs):
        user=get_logged_in_user(request)
        blog_id = kwargs.get("id")
        blog=get_object_or_404(Blog,author=user,id=blog_id)
        title=request.POST.get('title')
        content=request.POST.get('content')
        image=request.FILES.get('image')

        blog.title=title
        blog.content=content
        if image:
            blog.image=image
        blog.save()
        messages.success(request,"Blog Edited Successfully")
        return redirect('blog_list')
    

@method_decorator(
    [
        role_required("ADMIN", "USER", "STAFF"),
        login_required,
        cache_control(no_cache=True, must_revalidate=True, no_store=True),
    ],
    name="dispatch",
)
class DeleteBlogView(View):
    def get(self,request,*args, **kwargs):
        user = get_logged_in_user(request)
        blog_id = kwargs.get("id")
        blog=get_object_or_404(Blog,id=blog_id,author=user)
        blog.delete()
        messages.success(request,"Blog Deleted Successfully")
        return redirect('blog_list')
        

@method_decorator(
    [
        role_required("ADMIN", "USER", "STAFF"),
        login_required,
        cache_control(no_cache=True, must_revalidate=True, no_store=True),
    ],
    name="dispatch",
)
class BlogCommentView(View):

    def get(self, request, *args, **kwargs):
        return redirect("blog_list")
    
    def post(self,request,*args, **kwargs):
        user = get_logged_in_user(request)
        blog_id = kwargs.get("id")
        blog=get_object_or_404(Blog,id=blog_id)
        content=request.POST.get('content')

        if not content.strip():
            messages.error(request,'Comment cannot be Empty')
            return redirect('blog_list')
        
        Comment.objects.create(
            blog=blog,
            author=user,
            content=content,
        )
        messages.success(request,"Comment added successfully")
        return redirect('blog_list')

    

