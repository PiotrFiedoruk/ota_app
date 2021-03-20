import datetime

import pytest
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

from ota_app.models import Hotel, Hotel_owner, Room, Rateplan, Price, Reservation, Review
import pytz

@pytest.fixture
def user():
    u = User.objects.create_user(username="cokolwiek", password="cokolwiek2")
    g = Group.objects.create(name="hotel_owner_group")
    content_type = ContentType.objects.create(app_label='ota_app', model='Hotel')
    permission_view_h = Permission.objects.create(codename='view_hotel', name='view_hotel', content_type=content_type)
    permission_add_h = Permission.objects.create(codename='add_hotel', name='add_hotel', content_type=content_type)
    permission_change_h = Permission.objects.create(codename='change_hotel', name='change_hotel', content_type=content_type)
    permission_delete_h = Permission.objects.create(codename='delete_hotel', name='delete_hotel', content_type=content_type)

    permission_view_r = Permission.objects.create(codename='view_room', name='view_room', content_type=content_type)
    permission_add_r = Permission.objects.create(codename='add_room', name='add_room', content_type=content_type)
    permission_change_r = Permission.objects.create(codename='change_room', name='change_room', content_type=content_type)
    permission_delete_r = Permission.objects.create(codename='delete_room', name='delete_room', content_type=content_type)

    permission_view_rp = Permission.objects.create(codename='view_rateplan', name='view_rateplan', content_type=content_type)
    permission_add_rp = Permission.objects.create(codename='add_rateplan', name='add_rateplan', content_type=content_type)
    permission_change_rp = Permission.objects.create(codename='change_rateplan', name='change_rateplan', content_type=content_type)
    permission_delete_rp = Permission.objects.create(codename='delete_rateplan', name='delete_rateplan', content_type=content_type)

    permission_view_pr = Permission.objects.create(codename='view_price', name='view_price', content_type=content_type)
    permission_add_pr = Permission.objects.create(codename='add_price', name='add_price', content_type=content_type)
    permission_change_pr = Permission.objects.create(codename='change_price', name='change_price', content_type=content_type)
    permission_delete_pr = Permission.objects.create(codename='delete_price', name='delete_price', content_type=content_type)

    permission_view_res = Permission.objects.create(codename='view_reservation', name='view_reservation',
                                                     content_type=content_type)
    permission_change_res = Permission.objects.create(codename='change_reservation', name='change_reservation',
                                                     content_type=content_type)
    permission_add_res = Permission.objects.create(codename='add_reservation', name='add_reservation',
                                                     content_type=content_type)

    permission_view_rev = Permission.objects.create(codename='view_review', name='view_review',
                                                    content_type=content_type)
    permission_change_rev = Permission.objects.create(codename='change_review', name='change_review',
                                                      content_type=content_type)
    permission_add_rev = Permission.objects.create(codename='add_review', name='add_review',
                                                   content_type=content_type)

    g.permissions.add(permission_view_h, permission_add_h, permission_add_h, permission_change_h, permission_delete_h,
                       permission_view_r, permission_add_r, permission_change_r, permission_delete_r,
                      permission_view_rp, permission_add_rp, permission_change_rp, permission_delete_rp,
                      permission_view_pr, permission_add_pr, permission_change_pr, permission_delete_pr,
                      permission_view_res, permission_add_res, permission_change_res, permission_add_rev,
                      permission_change_rev, permission_view_rev)
    u.groups.add(g)
    return u

@pytest.fixture
def hotel_owner(user):
    ho = Hotel_owner.objects.create(user=user)
    return ho

@pytest.fixture
def hotel(hotel_owner):
    h = Hotel.objects.create(name="Hilton", city='Warsaw', hotel_owner=hotel_owner)
    return h

@pytest.fixture
def room(hotel):
    r = Room.objects.create(name='Double', hotel_id=hotel)
    return r

@pytest.fixture
def rateplan(room):
    rp = Rateplan.objects.create(name='Standard', room_id=room)
    return rp

@pytest.fixture
def price(rateplan):
    pr = Price.objects.create(rateplan_id=rateplan, date='2021-03-21', availability=1, price_1=20,price_2=30)
    return pr

@pytest.fixture
def reservation(hotel, user, room, rateplan, price):
    created = datetime.datetime.now()
    price = float(100)
    res = Reservation.objects.create(hotel=hotel, guest=user, room=room, price=price,
                             arrival='2021-03-22', departure='2021-03-25', num_of_guests=1,
                             status='Act', created=created)
    res.rateplan.add(rateplan)
    return res


@pytest.fixture
def review(hotel, user):
    created = datetime.datetime.now()
    rev = Review.objects.create(hotel=hotel, guest=user, title='sometitle', text='sometext', score_overall=9,
                                score_location=9, score_cleaning=9,score_service=9,created=created)
    return rev