from random import randint

import pytest
from rest_framework.test import APIClient
from backend.models import User, ConfirmEmailToken, Contact
from rest_framework.authtoken.models import Token


@pytest.fixture()
def client():
    """Фикстура создания клиента"""
    return APIClient()


@pytest.fixture()
def create_user():
    """Фикстура создания пользователя"""

    user = User.objects.create_user(first_name='First',
                                    last_name='Second',
                                    email='FirstSecond@mail.ru',
                                    password='qwer1234A',
                                    company='CompanyOne',
                                    position='worker',
                                    type='shop'
                                    )
    return user


@pytest.fixture()
def create_active_user():
    """Фикстура создания активного пользователя """

    user = User.objects.create_user(first_name='First',
                                    last_name='Second',
                                    email=f'FirstSecond{randint(0, 1000)}@mail.ru',
                                    password='qwer1234A',
                                    company='CompanyOne',
                                    position='worker',
                                    type='shop',
                                    is_active=True
                                    )
    return user


@pytest.fixture()
def create_token(create_active_user):
    """Фикстура создания пользователя и токена для авторизации"""

    token, _ = Token.objects.get_or_create(user_id=create_active_user.id)
    return token


@pytest.fixture()
def create_contact(create_token):
    """Фикстура создания контакта пользователя"""

    contact = Contact.objects.create(user_id=create_token.user.id,
                                     city='NewCity',
                                     street='WestStreet',
                                     phone='',
                                     house='50'
                                     )
    return contact


@pytest.mark.django_db()
def test_reg(client):
    """Тест регистрации пользователя"""
    count = User.objects.count()
    response = client.post('/api/v1/user/register', data={'first_name': 'Vova',
                                                           'last_name': 'Ivanov',
                                                           'email': 'FirstSecond@mail.ru',
                                                           'password': 'qwer1234A',
                                                           'company': 'CompanyOne',
                                                           'position': 'worker',
                                                           'type': 'shop',
                                                           'is_active': True
                                                           })

    assert response.status_code == 200
    assert User.objects.count() == count + 1

@pytest.mark.django_db
def test_confirm_reg(create_active_user, client):
    """Тест подтверждения регистрации пользователя"""

    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=create_active_user.id)
    response = client.post('/api/v1/user/register/confirm', data=dict(email=f'{create_active_user.email}', token=token.key))

    user = User.objects.get(id=create_active_user.id, is_active=True)

    assert user
    assert response.status_code == 200
    data = response.json()
    assert data['Status']


@pytest.mark.django_db
def test_login(create_active_user, client):
    """Тест авторизации"""

    response = client.post('/api/v1/user/login', data=dict(email=f'{create_active_user.email}', password='qwer1234A'))

    assert response.status_code == 200
    data = response.json()
    assert data['Status']


@pytest.mark.django_db()
def test_edit_user(create_active_user, client):
    """Тест изменения данных пользователя"""

    token, _ = Token.objects.get_or_create(user_id=create_active_user.id)
    client = APIClient(HTTP_AUTHORIZATION='Token ' + token.key)
    response = client.post('/api/v1/user/details', headers={'Authorization': 'Token ' + token.key},
                                                        data=dict(last_name='Third')
                           )

    # Проверка на корректное изменение данных пользователя, после смены пароля статус активности - False
    user = User.objects.get_or_create(id=create_active_user.id)


    assert user
    assert user[0].last_name == 'Third'
    assert response.status_code == 200
    data = response.json()
    assert data['Status']


@pytest.mark.django_db
def test_create_contact(create_active_user, client):
    """Тест создания контактов пользователя"""
    token, _ = Token.objects.get_or_create(user_id=create_active_user.id)
    client = APIClient(HTTP_AUTHORIZATION='Token ' + token.key)
    response = client.post('/api/v1/user/contact', data=dict(city='NewCity',
                                                          street='WestStreet',
                                                          phone='+79998883344',
                                                          house='50'),
                                                          headers={'Authorization': 'Token ' + token.key}
                           )

    contact = Contact.objects.get(user_id=create_active_user.id)

    assert contact
    assert response.status_code == 200


@pytest.mark.django_db
def test_edit_contact(create_contact, client):
    """Тест редактирования контакта пользователя"""

    token, _ = Token.objects.get_or_create(user_id=create_contact.user_id)
    client = APIClient(HTTP_AUTHORIZATION='Token ' + token.key)
    response2 = client.put(f'/api/v1/user/contact', data=dict(id=f'{create_contact.id}',
                                                                   phone='+79998888888'),
                                                                   headers={'Authorization': 'Token ' + token.key}
                          )

    contact = Contact.objects.get(user_id=create_contact.user_id)

    assert response2.status_code == 200
    assert contact.phone == '+79998888888'


@pytest.mark.django_db
def test_reset_password(create_active_user, client):
    """Тест сброса пароля"""

    response = client.post('/api/v1/user/password_reset', data=dict(email=create_active_user.email))

    assert response.status_code == 200
