from django.urls import path
from .views import *

urlpatterns =[
    path('adminside/', AdminPageView.as_view(), name='adminside'),
    path('admin/users/',AdminUsersView.as_view(), name='admin_users'),
    path('admin/users/add/',AdminAddUser.as_view(),name='admin_add_user'),
    path('admin/users/edit/<int:user_id>/',AdminEditUser.as_view(),name='admin_edit_user'),
    path('admin/users/delete/<int:user_id>/',AdminDeleteUser.as_view(),name='admin_delete_user'),
    path('admin/blogs/',AdminBlogs.as_view(),name='admin_blogs'),    
    path('admin/blogs/edit/<int:blog_id>/',AdminEditBlogs.as_view(),name='admin_edit_blogs'),
    path('admin/blogs/delete/<int:blog_id>',AdminDeleteBlogs.as_view(),name='admin_delete_blogs'),
    path('admin/comments/',AdminComments.as_view(),name='admin_comments'),
    path('admin/comments/edit/<int:comment_id>/',AdminEditComments.as_view(),name='admin_edit_comments'),
    path('admin/comments/delete/<int:comment_id>/',AdminDeleteComments.as_view(),name='admin_delete_comments'),

]