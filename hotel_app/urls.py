from django.contrib import admin
from django.urls import path
from ota_app.views import HotelCreateView, RoomCreateView, RateplanCreateView, MainView, PriceCreateView, \
    HotelDashboardView, RateplanUpdateView, RoomUpdateView, HotelUpdateView, RoomDeleteView, RateplanDeleteView, \
    PriceUpdateView, CreateUserView, LoginView, LogoutView, RoomDetailsView, HotelDetailsView, RoomReserveView, \
    ConfirmReservationView, ProfileView, MyHotelsView, ReservationDetailsView, CreateReviewView, ReviewView, \
    ReservationDetailsHotelView

urlpatterns = [
    path('admin/', admin.site.urls),

    # guest part
    path('', MainView.as_view(), name='main'),
    path('hotel-details/<int:hid>/', HotelDetailsView.as_view(), name='hotel-details'),
    path('room-reserve/<int:hid>/<int:rid>/', RoomReserveView.as_view(), name='room-reserve'),
    path('confirm-reservation/', ConfirmReservationView.as_view(), name='confirm-reservation'),

    # hotelier part:
    path('dashboard/<int:hid>/', HotelDashboardView.as_view(), name='dashboard'),
    path('register-hotel/', HotelCreateView.as_view(), name='create_hotel'),
    path('update-hotel/<int:pk>/', HotelUpdateView.as_view(), name='update_hotel'),
    path('add-room/<int:hid>/', RoomCreateView.as_view(), name='create_room'),
    path('update-room/<int:pk>/', RoomUpdateView.as_view(), name='update_room'),
    path('delete-room/<int:pk>/', RoomDeleteView.as_view(), name='delete_room'),
    path('details-room/<int:hid>/<rid>/', RoomDetailsView.as_view(), name='details-room'),
    path('add-rateplan/<int:hid>/<int:rid>/', RateplanCreateView.as_view(), name='create_rateplan'),
    path('update-rateplan/<int:pk>/', RateplanUpdateView.as_view(), name='update_rateplan'),
    path('delete-rateplan/<int:pk>/', RateplanDeleteView.as_view(), name='delete_rateplan'),
    path('add-price/<int:hid>/', PriceCreateView.as_view(), name='create_price'),
    path('update-price/<int:hid>/', PriceUpdateView.as_view(), name='update_price'),
    path('register-user/', CreateUserView.as_view(), name='register_user'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('my-hotels/', MyHotelsView.as_view(), name='my_hotels'),
    path('reservation-details/<int:resid>/', ReservationDetailsView.as_view(), name='reservation_details'),
    path('reservation-details-hotel/<int:resid>/', ReservationDetailsHotelView.as_view(),
         name='reservation_details_hotel'),
    path('add-review/<int:hid>/', CreateReviewView.as_view(), name='create_review'),
    path('review-details/<int:revid>/', ReviewView.as_view(), name='review_details'),
]
