from django.db import models
from users.constants import RoleChioice

class Users(models.Model):
    username=models.CharField(max_length=100,blank=True,null=True)
    email=models.EmailField(unique=True)
    password=models.CharField(blank=True,null=True)
    role= models.CharField(choices=RoleChioice.choices, default=RoleChioice.USER)
    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=False)

    def __str__(self):
        return self.email
