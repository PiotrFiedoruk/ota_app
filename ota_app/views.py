from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
import datetime
from django.views.generic.edit import UpdateView, DeleteView, FormView
from django.db.models import Avg, Sum
from ota_app.forms import AddUserForm, LoginForm, AddHotelForm, AddRoomForm, AddRateplanForm
from ota_app.models import Hotel, Room, Rateplan, Price, Reservation
from django.contrib.auth.models import Group, User

# no post
class MainView(View):
    def get(self, request):
        if 'city' in request.GET:
            city = request.GET.get('city')
            arrival = request.GET.get('arrival')
            departure = request.GET.get('departure')
            guests = request.GET.get('guests')
            # departure = (datetime.datetime.strptime(departure, '%Y-%m-%d') - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            hotelsearch = Hotel.objects.filter(
                city=city,
                hotel_rooms__room_rateplans__rateplan_prices__date__range=[arrival, departure],
                # room__rateplan__prices__price_1__isnull=False,
                hotel_rooms__room_rateplans__rateplan_prices__availability__gt=0, ).distinct()
            ctx = {'hotelsearch': hotelsearch, 'city': city, 'arrival': arrival, 'departure': departure, 'guests': guests }
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
                .annotate(avg_price=Avg('room_rateplans__rateplan_prices__price_1'))
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
class HotelDashboardView(View):
    def get(self, request, hid):
        hotel = Hotel.objects.get(id=hid)
        reservations = Reservation.objects.filter(hotel=hotel)

        # calculate average prices:
        total_average = 0
        date_today = datetime.date.today()
        date_end = date_today + datetime.timedelta(days=30)
        average_price = Price.objects.filter(rateplan_id__room_id__hotel_id=hid, date__range=[date_today, date_end])
        for price in average_price:
            total_average += price.price_1
        total_average = total_average / len(average_price)
        ctx = {'hotel': hotel, 'reservations': reservations, 'total_average': total_average}
        return render(request, 'ota_app/dahsboard.html', ctx)
#f
class HotelCreateView(FormView):
    template_name = 'ota_app/hotel_form.html'
    form_class = AddHotelForm
    success_url = '/'

    def form_valid(self, form):
        hotel = Hotel.objects.create(
            name=form.cleaned_data['name'],
            city=form.cleaned_data['city'],
        )
        hotel.save()
        # assign hotel_owner group permission to logged in user
        hotel_owner_user = self.request.user
        hotel_owner_group = Group.objects.get(name='hotel_owner_group')
        hotel_owner_group.user_set.add(hotel_owner_user)
        return redirect('dashboard', hotel.id)

class HotelUpdateView(UpdateView):
    model = Hotel
    fields = '__all__'
    template_name_suffix = '_update_form'
#f
class RoomCreateView(View):
    def get(self, request, hid):
        form = AddRoomForm
        ctx = {'form': form}
        return render(request, 'ota_app/room_form.html', ctx)

    def post(self, request, hid):
        hotel = Hotel.objects.get(id=hid)
        name = request.POST.get('name')
        room = Room.objects.create(hotel_id=hotel, name=name)
        room.save()
        return redirect('dashboard', hotel.id)

class RoomUpdateView(UpdateView):
    model = Room
    fields = '__all__'
    template_name_suffix = '_update_form'
    # define success url:
    def get_success_url(self):
        room = self.object
        hotel_id = room.hotel_id_id
        return reverse_lazy('dashboard', kwargs = {'hid': hotel_id})

class RoomDeleteView(DeleteView):
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

class RateplanCreateView(View):
    def get(self, request, hid, rid):
        form = AddRateplanForm()
        return render(request, 'ota_app/rateplan_form.html', {'form': form})

    def post(self, request, hid, rid):
        form = AddRateplanForm(request.POST)
        if form.is_valid():
            name = request.POST.get('name')
            price_1 = request.POST.get('price_1')
            price_2 = request.POST.get('price_2')
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

class RateplanUpdateView(UpdateView):
    model = Rateplan
    fields = ['name']
    template_name_suffix = '_update_form'
    def get_success_url(self):
        rateplan = self.object
        hotel_id = rateplan.room_id.hotel_id_id
        return reverse_lazy('dashboard', kwargs={'hid': hotel_id})

class RateplanDeleteView(DeleteView):
    model = Rateplan
    def get_success_url(self):
        rateplan = self.object
        hotel_id = rateplan.room_id.hotel_id_id
        return reverse_lazy('dashboard', kwargs={'hid': hotel_id})

class PriceCreateView(View): #price calendar
    def get(self, request, hid):
        hotel = Hotel.objects.get(id=hid)
        # define start and end date for price list. if start date not provided in url, set it to today's date
        if 'date' in request.GET:
            start_date = request.GET.get('date')
            start_date = datetime.datetime.strptime(start_date,
                                                    '%Y-%m-%d').date()  # convert string date to datetime object so it can be used in timedlta
        else:
            start_date = datetime.datetime.today().date()
        end_date = start_date + datetime.timedelta(days=14)  # set number of calendar days here
        prev_date = start_date - datetime.timedelta(days=14)  # get previous date for navigation links
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

class PriceUpdateView(View): #batch update
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
    success_url = '/'

    def form_valid(self, form):
        hotel_owner_user = User.objects.create_user(
            username=form.cleaned_data['username'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            password=form.cleaned_data['password'],
            email=form.cleaned_data['email']
        )
        hotel_owner_user.save()
        # assign user to hotel_owner group
        hotel_owner_group = Group.objects.get(name='hotel_owner_group')
        hotel_owner_group.user_set.add(hotel_owner_user)
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
        return redirect(request.META['HTTP_REFERER'])
