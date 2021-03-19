from django.contrib.auth.models import User, Group, Permission
from django.test import TestCase
from django.test import Client
import pytest
import datetime
import random
from django.urls import reverse, reverse_lazy

from ota_app.models import Hotel


@pytest.fixture
def client():
    client = Client()
    return client

def test_check_main_page(client):
    response = client.get('')
    assert response.status_code == 200

@pytest.mark.django_db
def test_hotel_details(client, hotel):
    response = client.get(f'/hotel-details/{hotel.id}/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_main_page_results(client):
    date_today = datetime.date.today()
    rand_num = random.randint(1, 15)
    date_future_arr = (date_today + datetime.timedelta(days=rand_num))
    date_future_dep = (date_future_arr + datetime.timedelta(days=rand_num))
    response_get_future_set = client.get('', {'city': 'Warsaw', 'arrival': date_future_arr, 'departure': date_future_dep, 'guests':'2'})
    assert len(response_get_future_set.context) > 0

@pytest.mark.django_db
def test_permission(user):
    assert user.has_perm('ota_app.view_hotel') is True


@pytest.mark.django_db
def test_dashboard(client, hotel):
    client.login(username="cokolwiek", password="cokolwiek2")
    response = client.get(f'/dashboard/{hotel.id}/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_my_hotel(client, hotel):
    client.login(username="cokolwiek", password="cokolwiek2")
    response = client.get('/my-hotels/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_my_hotel_result(client, hotel):
    client.login(username="cokolwiek", password="cokolwiek2")
    response = client.get('/my-hotels/')
    hotel_list = response.context['hotels_owned']
    assert hotel in hotel_list

@pytest.mark.django_db
def test_register_hotel(client, hotel, hotel_owner):
    client.login(username="cokolwiek", password="cokolwiek2")
    response_get = client.get(f'/register-hotel/')
    assert response_get.status_code == 200

@pytest.mark.django_db
def test_reserve_room(client, hotel, room):
    response = client.get(f'/room-reserve/{hotel.id}/{room.id}/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_update_hotel(client, hotel):
    client.login(username="cokolwiek", password="cokolwiek2")
    response = client.get(f'/update-hotel/{hotel.pk}/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_add_room(client, hotel):
    client.login(username="cokolwiek", password="cokolwiek2")
    response_get = client.get(f'/add-room/{hotel.id}/')
    assert response_get.status_code == 200

@pytest.mark.django_db
def test_update_room(client, room):
    client.login(username="cokolwiek", password="cokolwiek2")
    response = client.get(f'/update-room/{room.pk}/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_delete_room(client, room):
    client.login(username="cokolwiek", password="cokolwiek2")
    response = client.get(f'/delete-room/{room.pk}/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_room_details(client, hotel, room):
    client.login(username="cokolwiek", password="cokolwiek2")
    response = client.get(f'/details-room/{hotel.id}/{room.id}/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_add_rateplan(client, hotel, room):
    client.login(username="cokolwiek", password="cokolwiek2")
    response = client.get(f'/add-rateplan/{hotel.id}/{room.id}/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_update_rateplan(client, room, rateplan):
    client.login(username="cokolwiek", password="cokolwiek2")
    response = client.get(f'/update-rateplan/{rateplan.pk}/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_delete_rateplan(client, rateplan):
    client.login(username="cokolwiek", password="cokolwiek2")
    response = client.get(f'/delete-rateplan/{rateplan.pk}/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_price_calendar(client, hotel):
    client.login(username="cokolwiek", password="cokolwiek2")
    response = client.get(f'/add-price/{hotel.id}/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_price_update(client, hotel):
    client.login(username="cokolwiek", password="cokolwiek2")
    response = client.get(f'/update-price/{hotel.id}/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_register_user(client):
    response = client.get('/register-user/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_login_page(client):
    response = client.get('/login/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_profile_page(client, hotel):
    client.login(username="cokolwiek", password="cokolwiek2")
    response = client.get('/profile/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_reservation_details(client, reservation):
    client.login(username="cokolwiek", password="cokolwiek2")
    response = client.get(f'/reservation-details/{reservation.id}/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_add_review(client, hotel):
    client.login(username="cokolwiek", password="cokolwiek2")
    response = client.get(f'/add-review/{hotel.id}/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_review_details(client, review):
    client.login(username="cokolwiek", password="cokolwiek2")
    response = client.get(f'/review-details/{review.id}/')
    assert response.status_code == 200







#
# @pytest.fixture
# def hotel_owner(db) -> Group:
#     group = Group.objects.create(name="hotel_owner_group")
#     change_user_permissions = Permission.objects.filter(codename__in=["add_hotel"])
#     group.permissions.add(*change_user_permissions)
#     user = User.objects.create_user("hotel_owner")
#     user.groups.add(group)
#     return user
#
# def test_should_create_user(hotel_owner: User) -> None:
#     assert hotel_owner.username == "hotel_owner"
#
# def test_user_in_group(hotel_owner: User) -> None:
#     assert hotel_owner.groups.filter(name="hotel_owner_group").exists()
#
#
# def test_should_check_password(db, hotel_owner: User) -> None:
#     hotel_owner.set_password("secret")
#     assert hotel_owner.check_password("secret") is True
#
# def test_should_not_check_unusable_password(db, hotel_owner: User) -> None:
#     hotel_owner.set_password("secret")
#     hotel_owner.set_unusable_password()
#     assert hotel_owner.check_password("secret") is False



# # kompletny przykłąd:
# @pytest.fixture
# def client():
#     client = Client()
#     return client
# def test_details(client):
#     response = client.get('sith/list/')
#     assert response.status_code == 200
#     assert len(response.context['sith']) == 2

# @pytest.fixture
# def test_some_client():
#     c = Client()
#     response = c.get('hotel-details/5/')
#     assert response.status_code == 200
#
# def test_my_user(db):
#     me = User.objects.get(username='pikachu')
#     assert me.username == 'pikachu'
#
# @pytest.fixture
# def client():
#     client = Client()
#     return client
# def test_main_page(client):
#     response = client.get('')
#     assert response.status_code == 200
#
# @pytest.fixture
# def client():
#     client = Client()
#     return client
# @pytest.mark.django_db
# def test_main_page_results(client):
#     date_today = datetime.date.today()
#     rand_num = random.randint(1, 15)
#     date_future_arr = (date_today + datetime.timedelta(days=rand_num))
#     date_future_dep = (date_future_arr + datetime.timedelta(days=rand_num))
#     response_get_future_set = client.get('', {'city': 'Warsaw', 'arrival': date_future_arr, 'departure': date_future_dep, 'guests':'2'})
#     assert len(response_get_future_set.context) > 0
#
# @pytest.fixture
# def client():
#     client = Client()
#     return client
# def test_login_page(client):
#     url = "/login/"
#     response = client.get(url)
#     assert response.status_code == 200
# #
# @pytest.fixture
# def client():
#     client = Client()
#     return client
# @pytest.mark.django_db(transaction=True)
# def test_hotel_details_page(client):
#     url = "/hotel-details/4/"
#     # url = reverse_lazy("hotel-details",kwargs={'hid':'2'})
#     response = client.get(url, follow=True)
#     assert response.status_code == 200


# @pytest.fixture
# def client():
#     client = Client()
#     return client
# def test_register_user(client):
#     url = reverse_lazy("register_user")
#     response = client.get(url, follow=True)
#     assert response.status_code == 200
#
# @pytest.fixture
# def client():
#     client = Client()
#     return client
# @pytest.mark.django_db
# def test_my_hotels(client):
#     # assert client.login(username='bubu', password='sdfsdff') == False
#     # response = client.get('/my-hotels/')
#     # assert response.status_code == 302
#     client.login(username='pikachu', password='pikachu')
#     response = client.get("my-hotels/", follow=True)
#     print(response)
#     assert response.status_code == 200
