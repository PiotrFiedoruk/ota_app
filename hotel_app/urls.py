"""hotel_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ota_app.views import HotelCreateView, RoomCreateView, RateplanCreateView, MainView, PriceCreateView, \
    HotelDashboardView, RateplanUpdateView, RoomUpdateView, HotelUpdateView, RoomDeleteView, RateplanDeleteView, \
    PriceUpdateView, CreateHotelOwnerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MainView.as_view(), name='main'),
    path('dashboard/<int:hid>/', HotelDashboardView.as_view(), name='dashboard'),
    path('register-hotel/', HotelCreateView.as_view(), name='create_hotel'),
    path('update-hotel/<int:pk>/', HotelUpdateView.as_view(), name='update_hotel'),
    path('add-room/<int:hid>/', RoomCreateView.as_view(), name='create_room'),
    path('update-room/<int:pk>/', RoomUpdateView.as_view(), name='update_room'),
    path('delete-room/<int:pk>/', RoomDeleteView.as_view(), name='delete_room'),
    path('add-rateplan/<int:rid>/', RateplanCreateView.as_view(), name='create_rateplan'),
    path('update-rateplan/<int:pk>/', RateplanUpdateView.as_view(), name='update_rateplan'),
    path('delete-rateplan/<int:pk>/', RateplanDeleteView.as_view(), name='delete_rateplan'),
    path('add-price/<int:hid>/', PriceCreateView.as_view(), name='create_price'),
    path('update-price/<int:hid>/', PriceUpdateView.as_view(), name='update_price'),
    path('register-hotel-owner/', CreateHotelOwnerView.as_view(), name='create_hotel_owner'),
]
