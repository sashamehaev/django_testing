import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf

from news.pytest_tests.constants import STATUS_404, STATUS_200, STATUS_302

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'reverse_url, parametrized_client, status',
    (
        (lf('home_url'), lf('client'), STATUS_200),
        (lf('detail_url'), lf('client'), STATUS_200),
        (lf('login_url'), lf('client'), STATUS_200),
        (lf('logout_url'), lf('client'), STATUS_200),
        (lf('signup_url'), lf('client'), STATUS_200),
        (lf('edit_url'), lf('author_client'), STATUS_200),
        (lf('edit_url'), lf('not_author_client'), STATUS_404),
        (lf('edit_url'), lf('client'), STATUS_302),
        (lf('delete_url'), lf('author_client'), STATUS_200),
        (lf('delete_url'), lf('not_author_client'), STATUS_404),
        (lf('delete_url'), lf('client'), STATUS_302)
    )
)
def test_routes_status_code(
    reverse_url, parametrized_client, status
):
    response = parametrized_client.get(reverse_url)
    assert response.status_code == status


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
