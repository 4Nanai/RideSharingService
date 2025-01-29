from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/driver', views.register_driver_view, name='register_driver'),
    path('car/revise/<int:pk>/', views.revise_car_view, name='revise_info'),
    path('car/delete/<int:pk>/', views.delete_car_view.as_view(), name='delete_car'),
    path('car/info/', views.display_car_view, name='display_car'),
    path('driver/delete/', views.cancel_driver_view, name='delete_driver'),
    path('register/captcha/', views.send_email, name='captcha'),
]