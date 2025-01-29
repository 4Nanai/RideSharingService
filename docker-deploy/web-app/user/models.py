from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class RSSUser(AbstractUser):
    is_driver = models.BooleanField(default=False)

class CarModel(models.Model):
    user = models.ForeignKey(RSSUser, on_delete=models.CASCADE, related_name='cars', default="")
    vehicle_type = models.CharField(max_length=100, blank=True)
    vehicle_number = models.CharField(max_length=100, blank=True)
    max_passenger = models.IntegerField(blank=True, default=1)
    sp_info = models.TextField(blank=True, verbose_name='Special vehicle information')

class CaptchaModel(models.Model):
    email = models.EmailField(max_length=100, unique=True)
    captcha = models.CharField(max_length=6)
    create_time = models.DateTimeField(auto_now_add=True)

#     TODO: add explicit vehicle type
