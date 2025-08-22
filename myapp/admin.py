from django.contrib import admin
from myapp.models import Users
from myapp.models import Blog
from myapp.models import Comment

admin.site.register(Users)
admin.site.register(Blog)
admin.site.register(Comment)