import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf

from news.pytest_tests.constants import STATUS_404, STATUS_200, STATUS_302
pytestmark = pytest.mark.django_db


def test_home_page(client, home_url):
    response = client.get(home_url)
    assert response.status_code == STATUS_200


def test_detail_page(client, detail_url):
    response = client.get(detail_url)
    assert response.status_code == STATUS_200


@pytest.mark.parametrize(
    'reverse_url, parametrized_client, status',
    (
        (
            lf('edit_url'),
            lf('author_client'),
            STATUS_200
        ),
        (
            lf('delete_url'),
            lf('not_author_client'),
            STATUS_404
        )
    )
)
def test_availability_for_comment_edit_and_delete(
    reverse_url, parametrized_client, status
):
    response = parametrized_client.get(reverse_url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'url',
    (lf('login_url'), lf('logout_url'), lf('signup_url'))
)
def test_pages_availability(url, client):
    response = client.get(url)
    assert response.status_code == STATUS_200


@pytest.mark.parametrize(
    'reverse_url, status',
    (
        (lf('edit_url'), STATUS_302),
        (lf('delete_url'), STATUS_302)
    )
)
def test_redirect_for_anonymous_client(client, reverse_url, login_url, status):
    redirect_url = f'{login_url}?next={reverse_url}'
    response = client.get(reverse_url)
    assert response.status_code == status
    assertRedirects(response, redirect_url)
