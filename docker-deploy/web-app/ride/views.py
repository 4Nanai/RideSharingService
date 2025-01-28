from traceback import print_tb

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, reverse
from .forms import NewRideForm
from django.views.decorators.http import require_http_methods
from .models import RideModel
from user.models import CarModel
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
    user = request.user
    rides = RideModel.objects.filter(owner__exact=request.user)
    share_rides = RideModel.objects.filter(share_user=request.user)
    driver_rides = RideModel.objects.filter(driver__exact=user)
    return render(request, 'ride/ride.html', context={'rides': rides, 'view_my_ride': True, 'share_rides': share_rides, 'driver_rides': driver_rides})

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
    user = request.user
    if ride.owner != user and not ride.share_user.filter(pk=user.pk).exists():
        return redirect(reverse('ride:view_my_ride'))
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
        query &= ~Q(share_user__exact=user)
        query &= ~Q(driver__exact=user)
    rides = RideModel.objects.filter(query)

    return render(request, 'ride/share_ride.html', context={'rides':rides, 'view_share_ride': True})

@require_http_methods('GET')
def search_share_ride(request):
    q = request.GET.get('q')
    startTime = request.GET.get('startTime')
    endTime = request.GET.get('endTime')
    user = request.user
    query = Q(can_share=True)&Q(is_confirmed=False)&(Q(destination__icontains=q)|Q(departure__icontains=q)|Q(total_passenger__contains=q))
    if user.is_authenticated:
        query &= ~Q(owner__exact=user)
    if startTime:
        query &= Q(arrival_time__date__gte=startTime)
    if endTime:
        query &= Q(arrival_time__date__lte=endTime)
    rides = RideModel.objects.filter(query)
    return render(request, 'ride/share_ride.html', context={'rides': rides, 'view_share_ride': True, 'keyword_request': q, 'startTime_request': startTime, 'endTime_request': endTime})

# help function to get valid ride request query
def get_ride_request_query(request):
    user = request.user
    query = Q(is_confirmed=False) & ~Q(owner__exact=user) & ~Q(share_user__exact=user)
    rides = RideModel.objects.filter(query)
    return rides

@login_required(login_url='/user/login/')
def ride_requests_view(request):
    user = request.user
    if not user.is_driver:
        return redirect(reverse('index'))
    rides = get_ride_request_query(request)
    return render(request, 'ride/ride_request.html', context={'rides': rides,})

@login_required(login_url='/user/login/')
@require_http_methods(['GET', 'POST'])
def ride_info_view(request, ride_id):
    # TODO: limitation required
    if not request.user.is_driver:
        return redirect(reverse('index'))
    ride = RideModel.objects.get(pk=ride_id)
    if request.method == 'GET':
        show_info_only = request.GET.get('show_info_only')
        return render(request, 'ride/ride_info.html', context={'ride': ride, 'show_info_only': show_info_only})
    else:
        ride.driver = request.user
        ride.is_confirmed = True
        ride.save()
        return render(request, 'ride/ride_info.html', context={'ride': ride, 'success': True})

@require_http_methods('GET')
@login_required(login_url='/user/login/')
def search_ride_request(request):
    q = request.GET.get('q')
    startTime = request.GET.get('startTime')
    endTime = request.GET.get('endTime')
    user = request.user
    vehicle_type_filtered = request.GET.get('vehicle_type')
    cars = CarModel.objects.filter(Q(user__exact=user))
    cars_values = cars.values_list('vehicle_type',flat=True) 
    query = (~Q(owner__exact=user)&Q(is_confirmed=False)&
             (Q(destination__icontains=q)|
              Q(total_passenger__contains=q)|
              Q(departure__icontains=q)))
    
    if not user.is_driver:
        return redirect(reverse('index'))
    elif vehicle_type_filtered:
        query &= Q(vehicle_type__exact='any')|Q(vehicle_type__in=cars_values)
    if startTime:
        query &= Q(arrival_time__date__gte=startTime)
    if endTime:
        query &= Q(arrival_time__date__lte=endTime)
    rides = RideModel.objects.filter(query)
    return render(request, 'ride/ride_request.html', context={'rides': rides, 'keyword_request': q, 'startTime_request': startTime, 'endTime_request': endTime, 'vehicle_type_filtered':vehicle_type_filtered})

# join ride
@login_required(login_url='/user/login/')
def join_ride(request, ride_id):

    # Valid join detect
    user = request.user
    ride = RideModel.objects.get(pk=ride_id)
    if (ride.owner == user or
            ride.share_user.filter(pk=user.pk).exists() or
            ride.driver == user or
            ride.is_confirmed):
        return render(request, 'ride/ride_request.html', context={'fail': True})

    # add this user to share_user
    # update total_passenger
    ride.total_passenger += 1
    ride.share_user.add(user)
    ride.save()
    return render(request, 'ride/ride_request.html', context={'success': True})

    
# cancel my share ride
@login_required(login_url='/user/login/')
def cancel_share_ride(request, ride_id):

    # Valid cancel detect
    ride = RideModel.objects.get(pk=ride_id)
    user = request.user
    if not ride.share_user.filter(pk=user.pk).exists():
        return redirect(reverse('ride:view_my_ride'))

    # remove this user from share_user
    # update total_passenger
    ride.share_user.remove(user)
    ride.total_passenger -= 1
    ride.save()
    return redirect(reverse('ride:view_my_ride'))