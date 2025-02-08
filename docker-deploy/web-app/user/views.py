import json
import random
import string
from datetime import timedelta

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.generic import DeleteView

from RSS.Email import *
from .forms import RegisterForm, LoginForm, DriverRegisterForm, CarForm
from .models import RSSUser, CarModel, CaptchaModel

import _string
import random
import logging
logger = logging.getLogger('django')


# Create your views here.
@require_http_methods(['POST'])
def send_email(request):
    
    # only post request is allowed
    if request.method != 'POST':
        return JsonResponse({'code': 405, 'msg': 'Method not allowed'}, status=405)

    try:
        # Parse the JSON request body
        data = json.loads(request.body)
        email = data.get('email')
    except json.JSONDecodeError:
        return JsonResponse({'code': 400, 'msg': 'Invalid JSON format'}, status=400)

    # validate email
    if not email:
        return JsonResponse({'code': 400, 'msg': 'Email is required'}, status=400)

    # validate frequency
    if CaptchaModel.objects.filter(
        email=email,
        create_time__gt=timezone.now() - timedelta(seconds=60)
    ).exists():
        return JsonResponse({'code': 400, 'msg': 'Do not request frequently'}, status=400)

    # generate captcha
    captcha = "".join(random.sample(string.digits, 6))
    CaptchaModel.objects.update_or_create(
        email=email,
        defaults={'captcha': captcha, 'create_time': timezone.now()}
    )

    # send email
    try:
        service = gmail_authenticate()
        send_message(service, "4nanaiiyo@gmail.com", email, "Ride Sharing System Register",
                     f'<div>Your CAPTCHA is {captcha}</div><div>Please do not share this CAPTCHA with anyone else.</div><br></br><br></br>This is an auto-generated email from Ride Sharing System. Please do not reply.')
        logger.info(f"sending email to {email} success!")
    # error handler
    except Exception as e:
        logger.error(f"sending email to {email} fail!")
        return JsonResponse({'code': 500, 'msg': f'Sending email failed: {str(e)}'}, status=500)

    return JsonResponse({'code': 200, 'msg': 'Email sent'})

@require_http_methods(['GET', 'POST'])
def register_view(request):
    if request.user.is_authenticated:
        return redirect(reverse('index'))
    if request.method == 'GET':
        form = RegisterForm()
        context = {'form': form}
        return render(request, 'user/register.html', context=context)
    else:
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('pwd2')
            email = form.cleaned_data.get('email')
            RSSUser.objects.create_user(email=email, username=username, password=password)
            logger.warning(f"user ({username}) created successfully!")
            return redirect(reverse('user:login'))
        else:
            context = {'form': form}
            print(form.errors)
            logger.warning(f"fail to create user: {form.errors.get_json_data()}")
            return render(request, 'user/register.html', context=context)

@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect(reverse('index'))
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'user/login.html', context={'form': form})
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('pwd')
            remember = form.cleaned_data.get('remember')
            user = RSSUser.objects.filter(username=username).first()
            if user and user.check_password(password):
                # login
                login(request, user)
                # if not remember
                if not remember:
                    request.session.set_expiry(0)
                logger.warning(f"user ({username}) log in successfully!")
                return redirect(reverse('index'))
            else:
                logger.warning(f"user ({username}) fail to log in!")
                return render(request, 'user/login.html', context={'form' : form})
        else:
            return render(request, 'user/login.html', context={'form' : form})

def logout_view(request):
    user=request.user
    logout(request)
    logger.warning(f"user ({user}) succeed to log out")
    return redirect(reverse('index'))

@require_http_methods(['GET', 'POST'])
def register_driver_view(request):
    if not request.user.is_authenticated:
        return redirect(reverse('user:login'))
    if request.user.is_driver:
        return redirect(reverse('index'))
    if request.method == 'GET':
        form = DriverRegisterForm()
        return render(request, 'user/driver_register.html', context={'form': form})
    else:
        form = DriverRegisterForm(request.POST)
        if form.is_valid():
            # get post data
            vehicle_type = form.cleaned_data.get('vehicle_type')
            vehicle_number = form.cleaned_data.get('vehicle_number')
            max_passenger = form.cleaned_data.get('max_passenger')
            sp_info = form.cleaned_data.get('sp_info')

            # get user
            user = request.user

            # set user info
            user.is_driver = True
            cars = CarModel.objects.create(user=user,
                                    vehicle_type=vehicle_type,
                                    vehicle_number=vehicle_number,
                                    max_passenger=max_passenger,
                                    sp_info=sp_info)
            user.save()
            logger.warning(f"user succeed to register new vehicle: {vehicle_type} ({vehicle_number})" )
            return render(request, 'user/driver_register.html', context={'form': form, 'success': True})
        else:
            logger.warning(f"user failed to register new vehicle: {form.errors.get_json_data()}" )
            return render(request, 'user/driver_register.html', context={'form': form})

@require_http_methods(['GET', 'POST'])
@login_required(login_url='/user/login/')
def revise_car_view(request, pk):

    car = CarModel.objects.get(pk=pk)
    if car.user != request.user:
        logger.warning(f"user {request.user} attempts to revise vehicle information of another user {car.user}.")
        return redirect(reverse('index'))
    for ride in request.user.confirmed_rides.all():
        if ride.status == 'confirmed':
            logger.warning(f"user {request.user} attempts to revise vehicle information while a ride is still in progress.")
            return redirect(reverse('ride:view_my_ride'))
    if request.method == 'GET':
        form = CarForm(instance=car)
        return render(request, 'user/revise_car_info.html', context={'car': car, 'form':form})
    else:
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            form.save()
            logger.warning(f"user {request.user} succeed to revise vehicle {car.vehicle_type} {car.vehicle_number}")
            return render(request, 'user/revise_car_info.html', context={'form': form, 'is_success': True})
        else:
            logger.warning(f"user {request.user} failed to revise vehicle {car.vehicle_type} {car.vehicle_number}")
            return render(request, 'user/revise_car_info.html', context={'form': form, 'is_success': False})

class delete_car_view(DeleteView):
    model = CarModel
    template_name = 'user/confirm_car_delete.html'
    success_url = reverse_lazy('index')

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

    def form_valid(self, form):
        user = self.request.user
        for ride in user.confirmed_rides.all():
            if ride.status == 'confirmed':
                logger.warning(f"user {user} attempts to delete vehicle information while a ride is still in progress.")
                return redirect(reverse('ride:view_my_ride'))
        response = super().form_valid(form)
        if user.cars.count() == 0:
            user.is_driver = False
            user.save()
        if not CarModel.objects.filter(user=user).exists():
            user.is_driver = False
            user.save()
        return response

@login_required(login_url='/user/login/')
def display_car_view(request):
    return render(request, 'user/display_car_info.html', context={'cars': request.user.cars.all()})

@login_required(login_url='/user/login/')
@require_http_methods(['GET', 'POST'])
def cancel_driver_view(request):
    user = request.user
    if request.method == 'GET':
        if user.is_driver:
            if user.confirmed_rides.exists():
                return render(request, 'user/confirm_driver_delete.html', context={'fail': True})
            return render(request, 'user/confirm_driver_delete.html', context={'fail': False})
        else:
            return render(request, 'user/confirm_driver_delete.html', context={'not_driver': True})
    else:
        logger.warning(f"user ({user}) try to delete vehicle")
        user.is_driver = False
        CarModel.objects.filter(user=user).delete()
        user.save()
        logger.warning(f"user ({user}) succeed to delete vehicle")
        return render(request, 'user/confirm_driver_delete.html', context={'success': True})