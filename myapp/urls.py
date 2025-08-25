"""
URL configuration for Backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path,include
from .views import *
from . import views 




urlpatterns = [
    path('', views.entry_page, name='entry_page'),  
    path('guest', views.guest_blog_list, name='guest_blog_list'),
    path('home',views.index, name='index'),
    path('new-blog', views.add_blogs,name='newblogs'),
    path('blog-list',views.blog_list,name='blog_list'),
    path('edit-blog/<int:id>/', views.edit_blog, name='edit_blog'),
    path('delete-blog/<int:id>/',views.delete_blog,name='delete_blog'),
    path('comment/<int:id>/', views.add_comment,name='add_comment'),
  

#------------------- Admin Urls ---------------------

    path('adminside/', views.admin_page, name='adminside'),
    path('admin/users/',views.admin_users, name='admin_users'),
    path('admin/users/add/',views.admin_add_user,name='admin_add_user'),
    path('admin/users/edit/<int:user_id>/',views.admin_edit_user,name='admin_edit_user'),
    path('admin/users/delete/<int:user_id>/',views.admin_delete_user,name='admin_delete_user'),
    path('admin/blogs/',views.admin_blogs,name='admin_blogs'),    
    path('admin/blogs/edit/<int:blog_id>/',views.admin_edit_blogs,name='admin_edit_blogs'),
    path('admin/blogs/delete/<int:blog_id>',views.admin_delete_blog,name='admin_delete_blogs'),
    path('admin/comments/',views.admin_comments,name='admin_comments'),
    path('admin/comments/edit/<int:comment_id>/',views.admin_edit_comments,name='admin_edit_comments'),
    path('admin/comments/delete/<int:comment_id>/',views.admin_delete_comments,name='admin_delete_comments'),

]
