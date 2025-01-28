from django.urls import path
from . import views
from RSS.views import index_view
app_name = 'ride'

urlpatterns = [
    # create new ride request
    path('new/', views.new_ride_view, name='new_ride'),

    # show all rides
    path('view/', views.my_ride_view, name='view_my_ride'),

    # owner revise any ride info
    path('revise/<int:ride_id>', views.revise_ride_info, name='revise_ride'),

    # search any ride in view_my_ride page
    path('search/my/', views.search_my_ride, name='search_my_ride'),

    # ride owner/share user can check driver info
    path('detail/<int:ride_id>', views.ride_detail_view, name='ride_detail'),

    # ride owner delete ride confirm page
    path('delete/<int:ride_id>', views.ride_delete_view, name='delete_ride'),

    # show all shared rides
    path('share/', views.share_ride_view, name='view_share_ride'),

    # search in shared rides
    path('search/share/', views.search_share_ride, name='search_share_ride'),

    # show all open ride request
    path('requests/', views.ride_requests_view, name='ride_requests'),

    # show "ride_id open" ride request information
    path('requests/accept/<int:ride_id>', views.ride_info_view, name='ride_info'),

    # search open rides
    path('requests/search', views.search_ride_request, name='search_ride_request'),

    # join ride
    path('join/<int:ride_id>', views.join_ride, name='join_ride'),

    # cancel my share ride
    path('cancel_share_ride/<int:ride_id>', views.cancel_share_ride, name='cancel_share_ride'),
]