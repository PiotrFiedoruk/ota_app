from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
import datetime
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView

from ota_app.forms import AddUserForm, LoginForm, AddHotelForm, AddRoomForm
from ota_app.models import Hotel_owner, Hotel, Room, Rateplan, Price, Reservation, Guest, HotelOwner
from django.contrib.auth.models import Group, User
import calendar


class MainView(View):
    def get(self, request):
        if 'city' in request.GET:
            city = request.GET.get('city')
            arrival = request.GET.get('arrival')
            departure = request.GET.get('departure')
            guests = request.GET.get('guests')
            departure = (datetime.datetime.strptime(departure, '%Y-%m-%d') - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            hotelsearch = Hotel.objects.filter(
                city=city,
                hotel_rooms__room_rateplans__rateplan_prices__date__range=[arrival, departure],
                # room__rateplan__prices__price_1__isnull=False,
                hotel_rooms__room_rateplans__rateplan_prices__availability__gt=0, ).distinct()
            ctx = {'hotelsearch': hotelsearch, 'city': city, 'arrival': arrival, 'departure': departure, 'guests': guests }
        else:
            ctx = {}
        return render(request, 'ota_app/main.html', ctx)

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
        else:
            available_rooms = []
        ctx = {'hotel': hotel, 'available_rooms': available_rooms}
        return render(request, 'ota_app/hotel.html',ctx )


class HotelDashboardView(View):
    def get(self, request, hid):
        hotel = Hotel.objects.get(id=hid)
        ctx = {'hotel': hotel}
        return render(request, 'ota_app/dahsboard.html', ctx)

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


class RoomDetailsView(View):

    def get(self, request, hid, rid):
        room = Room.objects.get(id=rid)
        ctx = {'room': room}
        return render(request, 'ota_app/room_details.html', ctx)

class RateplanCreateView(View):
    def get(self, request,hid, rid):
        return render(request, 'ota_app/rateplan_form.html')

    def post(self, request,hid, rid):
        name = request.POST.get('name')
        price_1 = request.POST.get('price_1')
        price_2 = request.POST.get('price_2')
        room_obj = Room.objects.get(id=rid)
        hotel_id = room_obj.hotel_id.id
        new_rateplan = Rateplan(name=name, room_id=room_obj)
        new_rateplan.save()
        # create list of dates
        date_today = datetime.datetime.today()
        datelist = [str(date_today + datetime.timedelta(days=x))[:10] for x in range(10)] # number of initial dates here
        # create default prices for new rateplan for the next 365 days:
        for date in datelist:
            Price.objects.create(rateplan_id=new_rateplan, date=date, price_1=price_1,
                                 price_2=price_2)
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

class PriceCreateView(View):
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
                form = form + f"<p>{rateplan.name}</p><table class=''><tr>"
                form = form + "<td><input type='text' disabled value='availability'>" \
                            "<p></p>"\
                              "<input type='text' disabled value='price 1'>" \
                              "<input type='text' disabled value='price 2'></td>"
                for price in rateplan.rateplan_prices.filter(date__gte=start_date, date__lte=end_date):
                    form = form + "<td>"
                    if loop == 1:
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

class PriceUpdateView(View):
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
            Price.objects.filter(rateplan_id__room_id=room.id).filter(date=date).update(
                availability=availability)
            # update price for rateplan
            Price.objects.filter(rateplan_id=rateplan_id).filter(date=date).update(
                price_1 = price_1,
                price_2 = price_2,
            )
        return redirect('create_price', hid)

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
