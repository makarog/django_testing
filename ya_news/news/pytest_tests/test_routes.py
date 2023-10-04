from http import HTTPStatus
import pytest

from django.urls import reverse

from pytest_django.asserts import assertRedirects

HOME_URL = 'news:home'
LOGIN_URL = 'users:login'
LOGOUT_URL = 'users:logout'
SIGNUP_URL = 'users:signup'


@pytest.mark.parametrize(
    'name',
    (HOME_URL, LOGIN_URL, LOGOUT_URL, SIGNUP_URL)
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_detail_page(client, detail_url):
    response = client.get(detail_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit'),
)
def test_pages_availability_for_different_users(
    parametrized_client, name, id_comment_for_args, expected_status
):
    url = reverse(name, args=(id_comment_for_args))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, comment_object',
    (
        ('news:edit', pytest.lazy_fixture('comment')),
        ('news:delete', pytest.lazy_fixture('comment')),
    ),
)
def test_redirects(client, name, comment_object):
    login_url = reverse(LOGIN_URL)
    url = reverse(name, args=(comment_object.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
