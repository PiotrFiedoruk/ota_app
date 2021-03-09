from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
import datetime
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from ota_app.models import Hotel_owner, Hotel, Room, Rateplan, Price, Reservation, Guest
import calendar


class MainView(View):
    def get(self, request):
        if 'city' in request.GET:
            city = request.GET.get('city')
            arrival = request.GET.get('arrival')
            departure = request.GET.get('departure')
            departure = (datetime.datetime.strptime(departure, '%Y-%m-%d') - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            hotelsearch = Hotel.objects.filter(
                city=city,
                hotel_rooms__room_rateplans__rateplan_prices__date__range=[arrival, departure],
                # room__rateplan__prices__price_1__isnull=False,
                hotel_rooms__room_rateplans__rateplan_prices__availability__gt=0, ).distinct()
            ctx = {'hotelsearch': hotelsearch}
        else:
            ctx = {}
        return render(request, 'ota_app/main.html', ctx)

class HotelDashboardView(View):
    def get(self, request, hid):
        hotel = Hotel.objects.get(id=hid)
        ctx = {'hotel': hotel}
        return render(request, 'ota_app/dahsboard.html', ctx)

class HotelCreateView(CreateView):
    model = Hotel
    fields = '__all__'
    success_url = "/"

class HotelUpdateView(UpdateView):
    model = Hotel
    fields = '__all__'
    template_name_suffix = '_update_form'

class RoomCreateView(CreateView):
    model = Room
    fields = '__all__'
    success_url = "/"

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

class RateplanCreateView(View):
    def get(self, request, rid):
        return render(request, 'ota_app/rateplan_form.html')

    def post(self, request, rid):
        name = request.POST.get('name')
        availability = request.POST.get('availability')
        price_1 = request.POST.get('price_1')
        price_2 = request.POST.get('price_2')
        room_obj = Room.objects.get(id=rid)
        new_rateplan = Rateplan(name=name, room_id=room_obj)
        new_rateplan.save()
        # create list of dates
        date_today = datetime.datetime.today()
        datelist = [str(date_today + datetime.timedelta(days=x))[:10] for x in range(10)]
        # create default prices for new rateplan for the next 365 days:
        for date in datelist:
            Price.objects.create(rateplan_id=new_rateplan, date=date, availability=availability, price_1=price_1,
                                 price_2=price_2)
        return redirect('main')

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
            for rateplan in room.room_rateplans.all():
                form = form + f"<p>{rateplan.name}</p><table class=''><tr>"
                form = form + "<td><input type='text' disabled value='availability'>" \
                              "<input type='text' disabled value='price 1'>" \
                              "<input type='text' disabled value='price 2'></td>"
                for price in rateplan.rateplan_prices.filter(date__gte=start_date, date__lte=end_date):
                    form = form + "<td>"
                    form = form + f"<input type='hidden' value='{price.date}' name='dt-{price.id}'><br>"
                    form = form + f"<input type='number' value='{price.availability}' name='av-{price.id}'><br>"
                    form = form + f"<input type='number' value='{price.price_1}' name='pr1-{price.id}'><br>"
                    form = form + f"<input type='number' value='{price.price_2}' name='pr2-{price.id}'><br>"
                    form = form + "</td>"
                form = form + "</tr></table>"
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
            for rateplan in room.room_rateplans.all():
                for price in rateplan.rateplan_prices.filter(date__gte=start_date, date__lte=end_date):
                    rateplan_id = rateplan.id
                    date = price.date.strftime('%Y-%m-%d')
                    post_date = request.POST.get(f"dt-{price.id}")
                    availability = request.POST.get(f"av-{price.id}")
                    price_1 = request.POST.get(f"pr1-{price.id}")
                    price_2 = request.POST.get(f"pr2-{price.id}")
                    Price.objects.filter(id=price.id).update(rateplan_id=rateplan_id, availability=availability,
                                                             price_1=price_1,
                                                             price_2=price_2)
                    # update other rateplans in the same room ( there can be only one availability for each room)
                    Price.objects.filter(rateplan_id__room_id=room.id, date=post_date).update(availability=availability)
        return redirect('/')

class PriceUpdateView(View):
    def get(self, request, hid):
        hotel = Hotel.objects.get(id=hid)
        rateplans = Rateplan.objects.filter(room_id__hotel_id_id=hid)
        ctx = {'rateplans': rateplans, 'hotel': hotel}
        return render(request, 'ota_app/price_update_form.html', ctx)

    def post(self, request, hid):
        rateplan_id = request.POST.get('rateplan_id')
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
            Price.objects.filter(rateplan_id=rateplan_id).filter(date=date).update(
                availability = availability,
                price_1 = price_1,
                price_2 = price_2,
            )
        return redirect('create_price', hid)



