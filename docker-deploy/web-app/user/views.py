from http.client import responses

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DeleteView

from .forms import RegisterForm, LoginForm, DriverRegisterForm, CarForm
from django.views.decorators.http import require_http_methods
from .models import RSSUser, CarModel

# Create your views here.
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
            RSSUser.objects.create_user(username=username, password=password)
            return redirect(reverse('user:login'))
        else:
            context = {'form': form}
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
                return redirect(reverse('index'))
            else:
                return render(request, 'user/login.html', context={'form' : form})
        else:
            return render(request, 'user/login.html', context={'form' : form})

def logout_view(request):
    logout(request)
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
            return render(request, 'user/driver_register.html', context={'form': form, 'success': True})
        else:
            return render(request, 'user/driver_register.html', context={'form': form})

@require_http_methods(['GET', 'POST'])
@login_required(login_url='/user/login/')
def revise_car_view(request, pk):
    car = request.user.cars.get(pk=pk)
    if request.method == 'GET':
        form = CarForm(instance=car)
        return render(request, 'user/revise_car_info.html', context={'car': car, 'form':form})
    else:
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            form.save()
            return render(request, 'user/revise_car_info.html', context={'form': form, 'is_success': True})
        else:
            return render(request, 'user/revise_car_info.html', context={'form': form, 'is_success': False})

class delete_car_view(DeleteView):
    model = CarModel
    template_name = 'user/confirm_car_delete.html'
    success_url = reverse_lazy('index')

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
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
        user.is_driver = False
        CarModel.objects.filter(user=user).delete()
        user.save()
        return render(request, 'user/confirm_driver_delete.html', context={'success': True})