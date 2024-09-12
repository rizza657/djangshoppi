from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Users(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)



class UserProfile(models.Model):

    name = models.CharField(max_length=30, blank=True)
    password = models.CharField(max_length=30, blank=True)
    email = models.EmailField(max_length=30, blank=True)
    

    def __str__(self):
        return self.user.username
    # class Meta:
    #     db_tables = 'users'

