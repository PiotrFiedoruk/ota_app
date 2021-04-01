from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
import datetime
from django.views.generic.edit import UpdateView, DeleteView, FormView, CreateView
from django.db.models import Avg, Sum, Min
from ota_app.forms import AddUserForm, LoginForm, AddRateplanForm, AddReviewForm
from ota_app.models import Hotel, Room, Rateplan, Price, Reservation, Hotel_owner, Review
from django.contrib.auth.models import Group, User


class MainView(View):
    def get(self, request):
        if 'city' in request.GET:
            city = request.GET.get('city')
            # provide dummy rates if no rates selected
            if request.GET.get('arrival'):
                arrival = request.GET.get('arrival')
                departure = request.GET.get('departure')
                guests = request.GET.get('guests')
            else:
                arrival = datetime.date.today()
                departure = arrival + datetime.timedelta(days=3)
                arrival = arrival.strftime("%Y-%m-%d")
                departure = departure.strftime("%Y-%m-%d")
                guests = 1
            # below search returns all hotels with availability on ANY given date between arrival-departure.
            hotelsearch = Hotel.objects.filter(
                city=city, hotel_rooms__room_rateplans__rateplan_prices__date__range=[arrival, departure],
                hotel_rooms__room_rateplans__rateplan_prices__availability__gt=0).distinct()
            ctx = {'hotelsearch': hotelsearch, 'city': city, 'arrival': arrival, 'departure': departure,
                   'guests': guests}
        else:
            ctx = {}
        return render(request, 'ota_app/main.html', ctx)


class HotelDetailsView(View):
    def get(self, request, hid):
        hotel = Hotel.objects.get(id=hid)
        # get reviews queryset
        reviews = Review.objects.filter(hotel_id=hid)
        reviews_avg = reviews.aggregate(Avg('score_overall'))

        ''' 
        1 display available rooms if dates are known. 
        2 get list of available rooms and rooms with no availability
          on any given date. 
        3 then compare both queryset using 'difference'.'''
        if 'arrival' in request.GET:
            arrival = request.GET.get('arrival')
            departure = request.GET.get('departure')
            guests = request.GET.get('guests')
            hotel_rooms = hotel.hotel_rooms.filter(
                room_rateplans__rateplan_prices__date__range=[arrival, departure],
                room_rateplans__rateplan_prices__availability__gt=0, ).distinct()

            not_available_rooms = hotel.hotel_rooms.filter(
                room_rateplans__rateplan_prices__date__range=[arrival, departure],
                room_rateplans__rateplan_prices__availability__lt=1, ).distinct()
            available_rooms = hotel_rooms.difference(not_available_rooms)
            # count average room price for each room
            available_rooms_price = hotel.hotel_rooms.filter(
                room_rateplans__rateplan_prices__date__range=[arrival, departure],
                room_rateplans__rateplan_prices__availability__gt=0, ).distinct() \
                .annotate(avg_price=Min('room_rateplans__rateplan_prices__price_1'))
            ctx = {'hotel': hotel, 'available_rooms': available_rooms, 'available_rooms_price': available_rooms_price,
                   'arrival': arrival, 'departure': departure, 'guests': guests, 'reviews': reviews,
                   'reviews_avg': reviews_avg}
        else:
            available_rooms = []
            available_rooms_price = []
            ctx = {'hotel': hotel, 'available_rooms': available_rooms, 'available_rooms_price': available_rooms_price,
                   'reviews': reviews, 'reviews_avg': reviews_avg}
        return render(request, 'ota_app/hotel.html', ctx)


class RoomReserveView(View):
    def get(self, request, hid, rid):
        room = Room.objects.get(id=rid)
        if 'arrival' in request.GET:
            arrival = request.GET.get('arrival')
            departure = request.GET.get('departure')
            guests = request.GET.get('guests')
            # get price 1 or 2:
            if guests == '1':
                price_variable = 'rateplan_prices__price_1'
            elif guests == '2':
                price_variable = 'rateplan_prices__price_2'
            else:
                raise Exception('Please provide number of guests')
            available_rateplans = Rateplan.objects.filter(room_id=rid, rateplan_prices__date__gte=arrival,
                                                          rateplan_prices__date__lt=departure,
                                                          rateplan_prices__availability__gt=0,
                                                          ).annotate(total_price=Sum(price_variable))
            ctx = {'room': room, 'available_rateplans': available_rateplans, 'arrival': arrival, 'departure': departure,
                   'guests': guests}
        else:
            ctx = {'room': room}
        return render(request, 'ota_app/room_reserve.html', ctx)


class ConfirmReservationView(LoginRequiredMixin, View):
    def post(self, request):
        # get post data:
        rpid = request.POST.get('rpid')
        arrival = request.POST.get('arrival')
        departure = request.POST.get('departure')
        guests = request.POST.get('guests')
        # create departure -1 day date for availability and price count:
        departure_obj = datetime.datetime.strptime(departure, "%Y-%m-%d")
        departure_decreased = departure_obj - datetime.timedelta(days=1)
        departure_dec = departure_decreased.strftime("%Y-%m-%d")
        # get objects to create new reservation:
        hotel_obj = Hotel.objects.get(hotel_rooms__room_rateplans__in=[rpid])
        guest_id = request.user.id
        guest_obj = User.objects.get(id=guest_id)
        rateplan = Rateplan.objects.get(id=rpid)
        room = Room.objects.get(room_rateplans__in=[rpid])
        # count total price:
        total_price_query = Price.objects.filter(rateplan_id=rateplan, date__range=[arrival, departure_dec])
        total_price = 0
        for price in total_price_query:
            total_price += price.price_1
        # save new reservation:
        new_reservation = Reservation.objects.create(hotel=hotel_obj, guest=guest_obj,
                                                     price=int(float(total_price)), room=room, arrival=arrival,
                                                     departure=departure,
                                                     num_of_guests=int(guests), status='active')
        new_reservation.save()
        # assign new reservation to a rateplan
        new_reservation.rateplan.add(rateplan)
        # decrease room availability for the booked dates:
        availability_set = Price.objects.filter(rateplan_id__room_id=room, date__range=[arrival, departure_dec])
        for price in availability_set:
            price_availability = price.availability
            price.availability = price_availability - 1
            price.save()
        ctx = {'hotel': hotel_obj, 'room': room, 'rateplan': rateplan, 'guests': guests, 'arrival': arrival,
               'departure': departure, 'total_price': total_price}
        return render(request, 'ota_app/confirm_reservation.html', ctx)


class HotelDashboardView(PermissionRequiredMixin, View):
    permission_required = 'ota_app.view_hotel'

    def get(self, request, hid):
        hotel = Hotel.objects.get(id=hid)
        # check if property belongs to logged in user:
        hotel_owner_username = hotel.hotel_owner.user.username
        if hotel_owner_username != request.user.username:
            raise Exception('this property does not belong to you')
        # paginate reservations:
        reservations = Reservation.objects.filter(hotel=hotel).order_by('-created')
        paginator = Paginator(reservations, 5)  # Show reservations per page.
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        # get recent reviews:
        date_recent = datetime.date.today()
        date_recent = date_recent - datetime.timedelta(days=30)
        reviews = Review.objects.filter(hotel_id=hid, created__gt=date_recent).order_by('-created')
        # calculate average prices:
        date_today = datetime.date.today()
        date_end = date_today + datetime.timedelta(days=30)
        date_today = datetime.date.today().strftime("%Y-%m-%d")
        date_end = date_end.strftime("%Y-%m-%d")
        total_average = Price.objects.filter(rateplan_id__room_id__hotel_id=hid,
                                             date__range=[date_today, date_end]).aggregate(Avg('price_1'))
        ctx = {'hotel': hotel, 'reservations': reservations, 'total_average': total_average, 'page_obj': page_obj,
               'reviews': reviews}
        return render(request, 'ota_app/dahsboard.html', ctx)


# f
class HotelCreateView(LoginRequiredMixin, CreateView):
    model = Hotel
    fields = ['name', 'city', 'street', 'description', 'facilities']
    exclude = ['hotel_owner']

    def get_success_url(self):
        hid = self.kwargs['hid']
        return f'/dashboard/{hid}'

    def form_valid(self, form):
        hotel = Hotel(
            name=form.cleaned_data['name'],
            city=form.cleaned_data['city'],
            street=form.cleaned_data['street'],
            description=form.cleaned_data['description'],
            facilities=form.cleaned_data['facilities'],
        )
        # assign current user to hotel_owner_group permission
        user = self.request.user
        hotel_owner_group = Group.objects.get(name='hotel_owner_group')
        hotel_owner_group.user_set.add(user)
        # assign hotel_owner to new hotel
        hotel_owner = Hotel_owner.objects.create(user=user)
        hotel.hotel_owner = hotel_owner
        # save hotel:
        hotel.save()
        return redirect('dashboard', hotel.id)


class HotelUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = ('ota_app.view_hotel', 'ota_app.add_hotel',)
    model = Hotel
    fields = ('name', 'city', 'description', 'facilities')
    template_name_suffix = '_update_form'

    def get_success_url(self):
        hid = self.kwargs['pk']
        return f"/dashboard/{hid}"


# f
class RoomCreateView(PermissionRequiredMixin, CreateView):
    permission_required = ('ota_app.view_room', 'ota_app.add_room',)
    model = Room
    fields = ['name', 'description', 'amenities']

    def get_success_url(self):
        hid = self.kwargs['hid']
        return f"dashboard/{hid}"

    def form_valid(self, form):
        hid = self.kwargs['hid']
        hotel = Hotel.objects.get(id=hid)
        name = form.cleaned_data['name']
        description = form.cleaned_data['description']
        amenities = form.cleaned_data['amenities']
        room = Room(hotel_id=hotel, name=name, description=description, amenities=amenities)
        room.save()
        return redirect('dashboard', hid)


class RoomUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = ('ota_app.view_room', 'ota_app.add_room',)
    model = Room
    fields = ['name', 'description', 'amenities']
    template_name_suffix = '_update_form'

    # define success url:
    def get_success_url(self):
        room = self.object
        hid = room.hotel_id_id
        return f'/dashboard/{hid}'


class RoomDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = ('ota_app.view_hotel', 'ota_app.delete_room')
    model = Room

    def get_success_url(self):
        room = self.object
        hotel_id = room.hotel_id_id
        return reverse_lazy('dashboard', kwargs={'hid': hotel_id})


class RoomDetailsView(View):

    def get(self, request, hid, rid):
        room = Room.objects.get(id=rid)
        ctx = {'room': room}
        return render(request, 'ota_app/room_details.html', ctx)


class RateplanCreateView(PermissionRequiredMixin, View):
    permission_required = ('ota_app.view_rateplan', 'ota_app.add_rateplan',)
    model = Rateplan
    fields = ['name']

    def get(self, request, hid, rid):
        form = AddRateplanForm()
        return render(request, 'ota_app/rateplan_form.html', {'form': form})

    def post(self, request, hid, rid):
        form = AddRateplanForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            price_1 = form.cleaned_data['price_1']
            price_2 = form.cleaned_data['price_2']
            room_obj = Room.objects.get(id=rid)
            hotel_id = room_obj.hotel_id.id
            new_rateplan = Rateplan(name=name, room_id=room_obj)
            new_rateplan.save()
            # create list of dates
            date_today = datetime.date.today()
            datelist = [date_today + datetime.timedelta(days=x) for x in range(365)]  # number of initial dates here
            # create default prices for new rateplan for the datelist range:
            for date in datelist:
                Price.objects.create(rateplan_id=new_rateplan, date=date, price_1=price_1,
                                     price_2=price_2, availability=0)
            return redirect('dashboard', hotel_id)


class RateplanUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = ('ota_app.view_rateplan', 'ota_app.change_rateplan',)
    model = Rateplan
    fields = ['name']
    template_name_suffix = '_update_form'

    def get_success_url(self):
        rateplan = self.object
        hotel_id = rateplan.room_id.hotel_id_id
        return reverse_lazy('dashboard', kwargs={'hid': hotel_id})


class RateplanDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = ('ota_app.view_hotel', 'ota_app.delete_rateplan',)
    model = Rateplan

    def get_success_url(self):
        rateplan = self.object
        hotel_id = rateplan.room_id.hotel_id_id
        return reverse_lazy('dashboard', kwargs={'hid': hotel_id})


class PriceCreateView(PermissionRequiredMixin, View):  # price calendar
    permission_required = ('ota_app.view_price', 'ota_app.add_price', 'ota_app.change_price')

    def get(self, request, hid):
        hotel = Hotel.objects.get(id=hid)
        # # check if property belongs to logged in user:
        if hotel.hotel_owner.user.username != request.user.username:
            raise Exception('this property does not belong to you')
        else:
            # define start and end date for price list. if start date not provided in url, set it to today's date
            if 'date' in request.GET:
                start_date = request.GET.get('date')
                start_date = datetime.datetime.strptime(start_date,
                                                        '%Y-%m-%d').date()
                if start_date < datetime.date.today():  # changing past prices not allowed
                    start_date = datetime.date.today()
            else:
                start_date = datetime.date.today()
            end_date = start_date + datetime.timedelta(days=14)  # set number of calendar days here
            prev_date = start_date - datetime.timedelta(days=14)  # get previous date for navigation links
            if prev_date < datetime.date.today():  # changing past prices not allowed
                prev_date = datetime.date.today()
            # create price form:
            form = ""
            for room in hotel.hotel_rooms.all():
                form = form + f"<p><h3>{room.name}</h3></p>"
                loop = 1
                for rateplan in room.room_rateplans.all():
                    form = form + f"<p><strong>{rateplan.name}</strong></p>"
                    form = form + f"<table class='table' style='table-layout: fixed'><tr>"
                    for price in rateplan.rateplan_prices.filter(date__gte=start_date, date__lte=end_date):
                        form = form + "<td>"
                        if loop == 1:
                            form = form + f"{price.date.strftime('%a %d %b')}<br>"
                            form = form + f"<input type='hidden' value='{price.date}' name='dt-{price.id}'><br>"
                            form = form + f"<input type='number' value='{price.availability}' name='av-{price.id}'><br>"
                        form = form + f"<p></p>"
                        form = form + f"<input type='number' value='{price.price_1}' name='pr1-{price.id}'><br>"
                        form = form + f"<input type='number' value='{price.price_2}' name='pr2-{price.id}'><br>"
                        form = form + "</td>"
                    form = form + "</tr></table>"
                    loop += 1

            ctx = {'hotel': hotel, 'start_date': start_date, 'end_date': end_date, 'prev_date': prev_date, 'form': form}
            return render(request, 'ota_app/add_price.html', ctx)

    def post(self, request, hid):
        hotel = Hotel.objects.get(id=hid)
        if 'date' in request.GET:
            start_date = request.GET.get('date')
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_date = datetime.datetime.today().date()
        end_date = start_date + datetime.timedelta(days=14)  # set number of calendar days here
        # save dates from form:
        for room in hotel.hotel_rooms.all():
            loop = 1
            for rateplan in room.room_rateplans.all():
                for price in rateplan.rateplan_prices.filter(date__gte=start_date, date__lte=end_date):
                    rateplan_id = rateplan.id
                    date = price.date.strftime('%Y-%m-%d')
                    price_1 = request.POST.get(f"pr1-{price.id}")
                    price_2 = request.POST.get(f"pr2-{price.id}")
                    if loop == 1:
                        # first update availability for room prices on the same date:
                        availability = request.POST.get(f"av-{price.id}")
                        Price.objects.filter(rateplan_id__room_id=room.id).filter(date=date).update(
                            availability=availability)
                        Price.objects.filter(id=price.id).update(rateplan_id=rateplan_id,
                                                                 price_1=price_1,
                                                                 price_2=price_2)
                    else:
                        # then update other fields:
                        Price.objects.filter(id=price.id).update(rateplan_id=rateplan_id,
                                                                 price_1=price_1,
                                                                 price_2=price_2)
                loop += 1
        return redirect('create_price', hid)


class PriceUpdateView(PermissionRequiredMixin, View):  # batch update
    permission_required = ('ota_app.view_price', 'ota_app.add_price', 'ota_app.change_price')

    def get(self, request, hid):
        hotel = Hotel.objects.get(id=hid)
        # # check if property belongs to logged in user:
        if hotel.hotel_owner.user.username != request.user.username:
            raise Exception('this property does not belong to you')
        else:
            rateplans = Rateplan.objects.filter(room_id__hotel_id_id=hid)
            ctx = {'rateplans': rateplans, 'hotel': hotel}
            return render(request, 'ota_app/price_update_form.html', ctx)

    def post(self, request, hid):
        rateplan_id = request.POST.get('rateplan_id')
        room = Room.objects.get(room_rateplans__id=rateplan_id)
        start_date = request.POST.get('date_start')
        end_date = request.POST.get('date_end')
        availability = request.POST.get('availability')
        price_1 = request.POST.get('price_1')
        price_2 = request.POST.get('price_2')
        # convert dates to datetime objects:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        # create a list of dates:
        date_list = [start_date + datetime.timedelta(days=x) for x in range((end_date - start_date).days + 1)]
        for date in date_list:
            # update availability for all rateplans:
            if availability != "":
                Price.objects.filter(rateplan_id__room_id=room.id).filter(date=date).update(
                    availability=availability)
            # # update prices for chosen rateplan
            price = Price.objects.filter(rateplan_id=rateplan_id).filter(date=date)
            if price_1 != "":
                price.update(price_1=price_1)
            if price_2 != "":
                price.update(price_2=price_2)
        return redirect('create_price', hid)


class CreateUserView(FormView):
    template_name = 'ota_app/hotelowner_form.html'
    form_class = AddUserForm
    success_url = '/login'

    def form_valid(self, form):
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            password=form.cleaned_data['password'],
            email=form.cleaned_data['email']
        )
        user.save()
        # assign to user guest_group permission
        guest_group = Group.objects.get(name='guest_group')
        guest_group.user_set.add(user)
        return super().form_valid(form)


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, "ota_app/login.html", {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get('login')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return render(request, "ota_app/main.html")
            else:
                err = 'wrong username or password. try again'
                return render(request, "ota_app/login.html", {"form": form, 'err': err})
        else:
            err = 'something went wrong'
            return render(request, "ota_app/login.html", {"form": form, 'err': err})


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('main')


class ProfileView(PermissionRequiredMixin, View):
    permission_required = 'ota_app.view_reservation'

    def get(self, request):
        user = request.user
        # get list of user's reservations:
        reservations = user.guest_reservations.all().order_by('-created')
        ctx = {'reservations': reservations}
        return render(request, 'ota_app/profile_view.html', ctx)


class MyHotelsView(PermissionRequiredMixin, View):
    permission_required = 'ota_app.view_hotel'

    def get(self, request):
        user = request.user
        # get list of owned hotels:
        hotels_owned = user.hotel_owner.hotels_owned.all()
        ctx = {'hotels_owned': hotels_owned}
        return render(request, 'ota_app/my_hotels.html', ctx)


class ReservationDetailsView(PermissionRequiredMixin, View):
    permission_required = 'ota_app.view_reservation'

    def get(self, request, resid):
        reservation = Reservation.objects.get(id=resid)
        user = request.user
        # check if reservation belongs to user:
        if reservation in user.guest_reservations.all():
            ctx = {'reservation': reservation}
            return render(request, 'ota_app/reservation_details.html', ctx)
        else:
            raise Exception('This reservation does not belong to you')

    def post(self, request, resid):
        # change reservation status to 'cancelled'
        reservation_obj = Reservation.objects.get(id=resid)
        reservation_obj.status = 'CLX'
        reservation_obj.save()

        # if reservation cancelled return room availability for the booked dates:
        reservation = Reservation.objects.get(id=resid)
        room = reservation.room
        arrival = reservation.arrival
        departure = reservation.departure
        availability_set = Price.objects.filter(rateplan_id__room_id=room, date__range=[arrival, departure])
        for price in availability_set:
            price_availability = price.availability
            price.availability = price_availability + 1
            price.save()
        return redirect('profile')


class CreateReviewView(PermissionRequiredMixin, View):
    permission_required = 'ota_app.view_reservation'

    def get(self, request, hid):
        form = AddReviewForm
        ctx = {'form': form}
        return render(request, 'ota_app/review_form.html', ctx)

    def post(self, request, hid):
        form = AddReviewForm(request.POST)
        hotel = Hotel.objects.get(id=hid)
        guest = request.user
        if form.is_valid():
            review = Review(
                hotel=hotel,
                guest=guest,
                title=form.cleaned_data['title'],
                text=form.cleaned_data['text'],
                score_overall=form.cleaned_data['score_overall'],
                score_location=form.cleaned_data['score_location'],
                score_cleaning=form.cleaned_data['score_cleaning'],
                score_service=form.cleaned_data['score_service']
            )
            review.save()
            return redirect('main')
        else:
            return redirect(f'ota_app/add-review/{hotel.id}/')


class ReviewView(View):
    def get(self, request, revid):
        review = Review.objects.get(id=revid)
        ctx = {'review': review}
        return render(request, 'review_details.html', ctx)


class ReservationDetailsHotelView(PermissionRequiredMixin, View):
    permission_required = 'ota_app.view_reservation'

    def get(self, request, resid):
        reservation = Reservation.objects.get(id=resid)
        ctx = {'reservation': reservation}
        return render(request, 'ota_app/reservation_details_hotel.html', ctx)
