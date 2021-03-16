from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
import datetime
from django.views.generic.edit import UpdateView, DeleteView, FormView
from django.db.models import Avg, Sum, Min
from ota_app.forms import AddUserForm, LoginForm, AddHotelForm, AddRoomForm, AddRateplanForm
from ota_app.models import Hotel, Room, Rateplan, Price, Reservation, Hotel_owner
from django.contrib.auth.models import Group, User, Permission


# no post
class MainView(View):
    def get(self, request):
        if 'city' in request.GET:
            city = request.GET.get('city')
            arrival = request.GET.get('arrival')
            departure = request.GET.get('departure')
            guests = request.GET.get('guests')
            hotelsearch = Hotel.objects.filter(
                city=city, hotel_rooms__room_rateplans__rateplan_prices__date__range=[arrival, departure],
                hotel_rooms__room_rateplans__rateplan_prices__availability__gt=0).distinct()
            ctx = {'hotelsearch': hotelsearch, 'city': city, 'arrival': arrival, 'departure': departure,
                   'guests': guests }
        else:
            ctx = {}
        return render(request, 'ota_app/main.html', ctx)
# no post
class HotelDetailsView(View):
    def get(self, request, hid):
        hotel = Hotel.objects.get(id=hid)
        #display available rooms if dates are known
        if 'arrival' in request.GET:
            arrival = request.GET.get('arrival')
            departure = request.GET.get('departure')
            guests = request.GET.get('guests')
            available_rooms = hotel.hotel_rooms.filter(
                room_rateplans__rateplan_prices__date__range=[arrival, departure],
                room_rateplans__rateplan_prices__availability__gt=0, ).distinct()
            # count the average room price for each room:
            available_rooms_price = hotel.hotel_rooms.filter(
            room_rateplans__rateplan_prices__date__range=[arrival, departure],
            room_rateplans__rateplan_prices__availability__gt=0, ).distinct()\
                .annotate(avg_price=Min('room_rateplans__rateplan_prices__price_1'))
        else:
            available_rooms = []
            available_rooms_price = []
        ctx = {'hotel': hotel, 'available_rooms': available_rooms, 'available_rooms_price': available_rooms_price,
               'arrival': arrival, 'departure': departure, 'guests': guests}
        return render(request, 'ota_app/hotel.html',ctx )
# no post
class RoomReserveView(View):
    def get(self, request, hid, rid):
        room = Room.objects.get(id=rid)
        if 'arrival' in request.GET:
            arrival = request.GET.get('arrival')
            departure = request.GET.get('departure')
            guests = request.GET.get('guests')
            available_rateplans = Rateplan.objects.filter(room_id=rid, rateplan_prices__date__gte=arrival,
                                                      rateplan_prices__date__lt=departure,
                                                      rateplan_prices__availability__gt=0,
                                                      ).annotate(total_price=Sum('rateplan_prices__price_1'))
            ctx = {'room': room, 'available_rateplans': available_rateplans, 'arrival': arrival, 'departure': departure,
                   'guests': guests}
        return render(request, 'ota_app/room_reserve.html', ctx)

class ConfirmReservationView(View):
    def post(self, request):
        # get post data:
        rpid = request.POST.get('rpid')
        arrival = request.POST.get('arrival')
        departure = request.POST.get('departure')
        guests = request.POST.get('guests')
        total_price = request.POST.get('total_price')
        # get necessarily objects to create new reservation:
        hotel_obj = Hotel.objects.get(hotel_rooms__room_rateplans__in=[rpid])
        guest_id = request.user.id
        guest_obj = User.objects.get(id=guest_id)
        rateplan_obj=Rateplan.objects.get(id=rpid)
        room = Room.objects.get(room_rateplans__in=[rpid])
        rateplan = Rateplan.objects.get(id=rpid)
        # save new reservation:
        new_reservation = Reservation.objects.create(hotel=hotel_obj, guest=guest_obj,
                                                     price=int(float(total_price)), arrival=arrival, departure=departure,
                                                     num_of_guests=int(guests))
        new_reservation.save()
        # assign new reservation to a rateplan
        new_reservation.rateplan.add(rateplan_obj)
        # decrease room availability for the booked dates:
        availability_set = Price.objects.filter(rateplan_id__room_id=room, date__range=[arrival, departure])
        for price in availability_set:
            price_availability = price.availability
            price.availability = price_availability -1
            price.save()
        ctx = {'hotel': hotel_obj, 'room': room, 'rateplan': rateplan, 'guests': guests, 'arrival': arrival,
               'departure': departure, 'total_price':total_price}
        return render(request, 'ota_app/confirm_reservation.html', ctx)

#no post
class HotelDashboardView(LoginRequiredMixin, View):

    def get(self, request, hid):
        hotel = Hotel.objects.get(id=hid)
        hotel_owner_username = hotel.hotel_owner.user.username
        # check if property belongs to logged in user:
        if hotel_owner_username != request.user.username:
            raise Exception('this property does not belong to you')
        # paginate reservations:
        reservations = Reservation.objects.filter(hotel=hotel)
        paginator = Paginator(reservations, 5)  # Show reservations per page.

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)





        # calculate average prices:
        total_average = 0
        date_today = datetime.date.today()
        date_end = date_today + datetime.timedelta(days=30)
        date_today = datetime.date.today().strftime("%Y-%m-%d")
        date_end = date_end.strftime("%Y-%m-%d")
        # average price not working:
        total_average = Price.objects.filter(rateplan_id__room_id__hotel_id=hid, date__range=[date_today, date_end]).aggregate(Avg('price_1'))
        ctx = {'hotel': hotel, 'reservations': reservations, 'total_average': total_average, 'page_obj': page_obj}
        return render(request, 'ota_app/dahsboard.html', ctx)
#f
class HotelCreateView(LoginRequiredMixin, FormView):
    permission_required = ('ota_app.view_hotel', 'ota_app.add_hotel',)
    template_name = 'ota_app/hotel_form.html'
    form_class = AddHotelForm
    success_url = '/'
    login_url = 'login'

    def form_valid(self, form):

        hotel = Hotel(
            name=form.cleaned_data['name'],
            city=form.cleaned_data['city'],
        )
        # assign to user hotel_owner_group permission
        user = self.request.user
        hotel_owner_group = Group.objects.get(name='hotel_owner_group')
        hotel_owner_group.user_set.add(user)
        # assign hotel_owner to hotel:
        try:
            hotel_owner = Hotel_owner.objects.get(user=user)
        except:
            hotel_owner = Hotel_owner.objects.create(user=user)
        hotel.hotel_owner = hotel_owner
        # save hotel:
        hotel.save()
        return redirect('dashboard', hotel.id)

class HotelUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = ('ota_app.view_hotel', 'ota_app.add_hotel',)
    model = Hotel
    fields = ('name',)
    template_name_suffix = '_update_form'
#f
class RoomCreateView(PermissionRequiredMixin, View):
    permission_required = ('ota_app.view_room', 'ota_app.add_room',)
    def get(self, request, hid):
        form = AddRoomForm
        ctx = {'form': form}
        return render(request, 'ota_app/room_form.html', ctx)

    def post(self, request, hid):
        form = AddRoomForm(request.POST)
        if form.is_valid():
            hotel = Hotel.objects.get(id=hid)
            name = form.cleaned_data['name']
            room = Room.objects.create(hotel_id=hotel, name=name)
            room.save()
        return redirect('dashboard', hid)

class RoomUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = ('ota_app.view_room', 'ota_app.add_room',)
    model = Room
    fields = ('name',)
    template_name_suffix = '_update_form'
    # define success url:
    def get_success_url(self):
        room = self.object
        hotel_id = room.hotel_id_id
        return reverse_lazy('dashboard', kwargs = {'hid': hotel_id})

class RoomDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = ('ota_app.view_hotel', 'ota_app.delete_room')
    model = Room
    # define success url:
    def get_success_url(self):
        room = self.object
        hotel_id = room.hotel_id_id
        return reverse_lazy('dashboard', kwargs={'hid': hotel_id})
# no post
class RoomDetailsView(View):

    def get(self, request, hid, rid):
        room = Room.objects.get(id=rid)
        ctx = {'room': room}
        return render(request, 'ota_app/room_details.html', ctx)

class RateplanCreateView(PermissionRequiredMixin, View):
    permission_required = ('ota_app.view_rateplan', 'ota_app.add_rateplan',)
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
            datelist = [date_today + datetime.timedelta(days=x) for x in range(365)] # number of initial dates here
            # create default prices for new rateplan for the next 365 days:
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

class PriceCreateView(PermissionRequiredMixin, View): #price calendar
    permission_required = ('ota_app.view_price', 'ota_app.add_price', 'ota_app.change_price')
    def get(self, request, hid):
        hotel = Hotel.objects.get(id=hid)
        # define start and end date for price list. if start date not provided in url, set it to today's date
        if 'date' in request.GET:
            start_date = request.GET.get('date')
            start_date = datetime.datetime.strptime(start_date,'%Y-%m-%d').date()  # convert string date to datetime object so it can be used in timedlta
            if start_date < datetime.date.today(): # changing past prices not allowed
                start_date = datetime.date.today()
        else:
            start_date = datetime.date.today()
        end_date = start_date + datetime.timedelta(days=14)  # set number of calendar days here
        prev_date = start_date - datetime.timedelta(days=14)  # get previous date for navigation links
        if prev_date < datetime.date.today(): # changing past prices not allowed
            prev_date = datetime.date.today()
        # create price form:
        form = ""
        for room in hotel.hotel_rooms.all():
            form = form + f"<p>{room.name}</p>"
            loop = 1
            for rateplan in room.room_rateplans.all():
                form = form + f"<table class=''><tr>"
                form = form + f"<td><input type='text' disabled value='{rateplan.name}'>" \
                              "<input type='text' disabled value='price 1'>" \
                              "<input type='text' disabled value='price 2'></td>"
                for price in rateplan.rateplan_prices.filter(date__gte=start_date, date__lte=end_date):
                    form = form + "<td>"
                    if loop == 1:
                        form = form + f"{price.date.strftime('%a %d %b')}<br>"
                        form = form + f"<input type='hidden' value='{price.date}' name='dt-{price.id}'><br>"
                        form = form + f"<input type='number' value='{price.availability}' name='av-{price.id}'><br>"
                        # form = form + f"<p></p>"
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
            start_date = datetime.datetime.strptime(start_date,
                                                    '%Y-%m-%d').date()  # convert string date to datetime object so it can be used in timedlta
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
                    post_date = request.POST.get(f"dt-{price.id}")

                    price_1 = request.POST.get(f"pr1-{price.id}")
                    price_2 = request.POST.get(f"pr2-{price.id}")
                    if loop == 1:
                        # update availability for room prices on the same date:
                        availability = request.POST.get(f"av-{price.id}")
                        Price.objects.filter(rateplan_id__room_id=room.id).filter(date=date).update(
                            availability=availability)
                        Price.objects.filter(id=price.id).update(rateplan_id=rateplan_id,
                                                                 price_1=price_1,
                                                                 price_2=price_2)
                    else:
                        # update other fields:
                        Price.objects.filter(id=price.id).update(rateplan_id=rateplan_id,
                                                                 price_1=price_1,
                                                                 price_2=price_2)
                loop += 1
        return redirect('create_price', hid)

class PriceUpdateView(PermissionRequiredMixin, View): #batch update
    permission_required = ('ota_app.view_price', 'ota_app.add_price', 'ota_app.change_price')
    def get(self, request, hid):
        hotel = Hotel.objects.get(id=hid)
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
#f
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
        return super().form_valid(form)

class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, "ota_app/login.html", {"form":form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get('login')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
            else:
                err = 'wrong username or password. try again'
                return render(request, "ota_app/login.html", {"form":form, 'err': err})
        else:
            err = 'something went wrong'
            return render(request, "ota_app/login.html", {"form":form, 'err': err})

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('main')

class ProfileView(View):
    # def test_func(self, hid):
    #     return len(self.user.request.hotel_owner.hotels_owned.filter(id=hid)) > 0
    def get(self, request):
        user = request.user
        # get list of owned hotels:
        reservations = user.guest_reservations.all().order_by('arrival')
        ctx = {'reservations': reservations}
        return render(request, 'ota_app/profile_view.html', ctx)

class MyHotelsView(View):
    def get(self, request):
        user = request.user
        # get list of owned hotels:
        hotels_owned = user.hotel_owner.hotels_owned.all()
        ctx = {'hotels_owned': hotels_owned}
        return render(request, 'ota_app/my_hotels.html', ctx)
