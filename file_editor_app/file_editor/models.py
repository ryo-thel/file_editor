from django.db import models
from django.contrib.auth.models import User


class SambaServer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    share_name = models.CharField(max_length=255)
