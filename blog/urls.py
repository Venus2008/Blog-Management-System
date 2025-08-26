from django.urls import path
from .views import *

urlpatterns = [
    path("", EntryPageView.as_view(), name="entry_page"),
    path('guest', GuestBlogListView.as_view(), name='guest_blog_list'),
    path('home',IndexView.as_view(), name='index'),
    path('new-blog', AddBlogView.as_view(),name='newblogs'),
    path('blog-list',BlogListView.as_view(),name='blog_list'),
    path('edit-blog/<int:id>/', EditBlogView.as_view(), name='edit_blog'),
    path('delete-blog/<int:id>/',DeleteBlogView.as_view(),name='delete_blog'),
    path('comment/<int:id>/', BlogCommentView.as_view(),name='add_comment'),
    
]