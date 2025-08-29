from django.db import models
from users.models import Users

class Blog(models.Model):
    title=models.CharField(max_length=50,blank=True)
    content=models.TextField(blank=True)
    image=models.ImageField(blank=True,upload_to='blog_image/',null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    author=models.ForeignKey(Users,on_delete=models.CASCADE,related_name='posts')

    def __str__(self):
        return self.title

class Comment(models.Model):
    blog=models.ForeignKey(Blog,on_delete=models.CASCADE,related_name='comments')
    author=models.ForeignKey(Users,on_delete=models.CASCADE,related_name='author')
    content=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.blog.title}"