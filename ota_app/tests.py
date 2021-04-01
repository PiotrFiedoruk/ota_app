from django.test import Client
import pytest
import datetime
import random


@pytest.fixture
def client():
    client = Client()
    return client


@pytest.mark.django_db
def test_user_in_group(user):
    assert user.groups.filter(name="hotel_owner_group").exists()


@pytest.mark.django_db
def test_should_check_password(user):
    user.set_password("secret")
    assert user.check_password("secret") is True


@pytest.mark.django_db
def test_should_not_check_unusable_password(user):
    user.set_password("secret")
    user.set_unusable_password()
    assert user.check_password("secret") is False


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
    response_get_future_set = client.get('', {'city': 'Warsaw', 'arrival': date_future_arr,
                                              'departure': date_future_dep, 'guests': '2'})
    assert response_get_future_set.status_code == 200

@pytest.mark.django_db
def test_main_page_results_content(client):
    date_today = datetime.date.today()
    rand_num = random.randint(1, 15)
    date_future_arr = (date_today + datetime.timedelta(days=rand_num))
    date_future_dep = (date_future_arr + datetime.timedelta(days=rand_num))
    date_future_arr = date_future_arr.strftime("%Y-%m-%d")
    date_future_dep = date_future_dep.strftime("%Y-%m-%d")
    response_get_future_set = client.get('', {'city': 'Warsaw', 'arrival': date_future_arr,
                                              'departure': date_future_dep, 'guests': '2'})
    assert response_get_future_set.context['city'] == 'Warsaw'

@pytest.mark.django_db
def test_main_page_results_content(client):
    date_today = datetime.date.today()
    rand_num = random.randint(1, 15)
    date_future_arr = (date_today + datetime.timedelta(days=rand_num))
    date_future_dep = (date_future_arr + datetime.timedelta(days=rand_num))
    date_future_arr = date_future_arr.strftime("%Y-%m-%d")
    date_future_dep = date_future_dep.strftime("%Y-%m-%d")
    response_get_future_set = client.get('', {'city': 'Warsaw', 'arrival': date_future_arr,
                                              'departure': date_future_dep, 'guests': '2'})
    assert response_get_future_set.context['guests'] == '2'



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
