from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


def test_home_page(client, home_url):
    response = client.get(home_url)
    assert response.status_code == HTTPStatus.OK


def test_detail_page(client, detail_url):
    response = client.get(detail_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'reverse_url, parametrized_client, status',
    (
        (
            pytest.lazy_fixture('edit_url'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('delete_url'),
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        )
    )
)
def test_availability_for_comment_edit_and_delete(
    reverse_url, parametrized_client, status
):
    response = parametrized_client.get(reverse_url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'name',
    ('users:login', 'users:logout', 'users:signup'),
)
def test_pages_availability(name, client):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'reverse_url',
    (pytest.lazy_fixture('edit_url'), pytest.lazy_fixture('delete_url')),
)
def test_redirect_for_anonymous_client(client, reverse_url):
    login_url = reverse('users:login')
    redirect_url = f'{login_url}?next={reverse_url}'
    response = client.get(reverse_url)
    assertRedirects(response, redirect_url)
