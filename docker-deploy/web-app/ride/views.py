from traceback import print_tb

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, reverse
from .forms import NewRideForm
from django.views.decorators.http import require_http_methods
from .models import RideModel
# Create your views here.

@require_http_methods(['GET', 'POST'])
def new_ride_view(request):
    if not request.user.is_authenticated:
        return redirect(reverse('user:login'))
    if request.method == 'GET':
        form = NewRideForm()
        return render(request, 'ride/new_ride.html', context={'form': form})
    else:
        form = NewRideForm(request.POST)
        if form.is_valid():
            departure = form.cleaned_data.get('departure')
            destination = form.cleaned_data.get('destination')
            arrival_time = form.cleaned_data.get('arrival_time')
            total_passenger = form.cleaned_data.get('total_passenger')
            can_share = form.cleaned_data.get('can_share')
            vehicle_type = form.cleaned_data.get('vehicle_type')
            sp_info = form.cleaned_data.get('sp_info')
            owner = request.user

            RideModel.objects.create(departure=departure,
                                     destination=destination,
                                     arrival_time=arrival_time,
                                     total_passenger=total_passenger,
                                     can_share=can_share,
                                     vehicle_type=vehicle_type,
                                     sp_info=sp_info,
                                     owner=owner)
            return render(request, 'ride/new_ride.html', context={'form': form, 'success': True})
        else:
            return render(request, 'ride/new_ride.html', context={'form': form, 'success': False})

@login_required(login_url='/user/login/')
def my_ride_view(request):
    rides = RideModel.objects.filter(owner__exact=request.user)
    share_rides = RideModel.objects.filter(share_user=request.user)
    return render(request, 'ride/ride.html', context={'rides': rides, 'view_my_ride': True, 'share_rides': share_rides})

# TODO: add a view for share ride form
@login_required(login_url='/user/login/')
@require_http_methods(['GET', 'POST'])
def revise_ride_info(request, ride_id):
    ride = RideModel.objects.get(pk=ride_id)
    if ride.owner != request.user:
        return redirect(reverse('ride:view_my_ride'))
    form = NewRideForm(instance=ride)
    if request.method == 'GET':
        return render(request, 'ride/revise_ride.html', context={'form': form, 'ride': ride})
    else:
        form = NewRideForm(request.POST, instance=ride)
        if form.is_valid():
            form.owner = request.user
            form.save()
            return render(request, 'ride/revise_ride.html', context={'form': form, 'success': True})
        else:
            return render(request, 'ride/revise_ride.html', context={'form': form, 'success': False})

@login_required(login_url='/user/login/')
@require_http_methods('GET')
def search_my_ride(request):
    q = request.GET.get('q')
    date = request.GET.get('date')
    ride_query = Q(owner=request.user) & (Q(destination__icontains=q) | Q(departure__icontains=q))
    share_query = Q(share_user=request.user) & (Q(destination__icontains=q) | Q(departure__icontains=q))
    if date:
        ride_query &= Q(arrival_time__date=date)
        share_query &= Q(arrival_time__date=date)

    rides = RideModel.objects.filter(ride_query)
    share_rides = RideModel.objects.filter(share_query)
    return render(request, 'ride/ride.html', context={'rides': rides, 'is_search': True, 'share_rides': share_rides, 'view_my_ride': True, 'keyword_request': q, 'date_request': date})

@login_required(login_url='/user/login')
def ride_detail_view(request, ride_id):
    ride = RideModel.objects.get(pk=ride_id)
    driver = ride.driver
    cars = driver.cars.all()
    return render(request, 'user/display_car_info.html', context={'cars': cars, 'to_guest': True})

@login_required(login_url='user/login')
@require_http_methods(['GET','POST'])
def ride_delete_view(request, ride_id):
    ride = RideModel.objects.get(pk=ride_id)
    user = request.user
    if user != ride.owner:
        return redirect(reverse('ride:view_my_ride'))
    if request.method == 'GET':
        return render(request,'ride/delete_ride.html', context={'ride': ride})
    else:
        ride.delete()
        return render(request, 'ride/delete_ride.html', context={'success': True})

def share_ride_view(request):
    user = request.user
    # list share ride:
    # 1. ride can be shared
    # 2. ride cannot have been confirmed
    # 3. user cannot be the owner of this ride
    query = Q(can_share=True)&Q(is_confirmed=False)
    if user.is_authenticated:
        query &= ~Q(owner__exact=user)
    rides = RideModel.objects.filter(query)
    return render(request, 'ride/share_ride.html', context={'rides':rides, 'view_share_ride': True})

@require_http_methods('GET')
def search_share_ride(request):
    q = request.GET.get('q')
    startTime = request.GET.get('startTime')
    endTime = request.GET.get('endTime')
    user = request.user
    query = Q(can_share=True)&Q(is_confirmed=False)&(Q(departure__icontains=q)|Q(destination__icontains=q)|Q(total_passenger__contains=q))
    if user.is_authenticated:
        query &= ~Q(owner__exact=user)
    if startTime:
        query &= Q(arrival_time__date__gte=startTime)
    if endTime:
        query &= Q(arrival_time__date__lte=endTime)
    rides = RideModel.objects.filter(query)
    return render(request, 'ride/share_ride.html', context={'rides': rides, 'view_share_ride': True, 'keyword_request': q, 'startTime_request': startTime, 'endTime_request': endTime})

