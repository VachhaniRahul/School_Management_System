# from django.db import models
# from django.contrib.auth.models import AbstractUser
# from django.conf import settings

# # Create your models here.

# class CustomUser(AbstractUser):
#     username = models.CharField(max_length=100, unique=True)
#     email = models.EmailField(max_length=100, unique=True)
#     first_name = models.CharField(max_length=100, blank=True)
#     last_name = models.CharField(max_length=30, blank=True)
#     date_joined = models.DateTimeField(auto_now_add=True)
#     is_authorised = models.BooleanField(default=False)
#     is_student = models.BooleanField(default=False)
#     is_teacher = models.BooleanField(default=False)

#     groups = models.ManyToManyField(
#         'auth.Group',
#         related_name= 'customuser_groups',
#         blank= True
#     )
#     user_permissions = models.ManyToManyField(
#         'auth.Permission',
#         related_name='customuser_permissions',
#         blank=True
#     )

#     def __str__(self):
#         return self.username
    


from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver

from .manager import UserManager


class CustomUser(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_authorised = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()

    def __str__(self):
        return self.username
    


class GroupChatMessage(models.Model):
    """
    Model for storing group chat messages in a single chat room.
    """
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="group_messages")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.message[:50]} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    
    

