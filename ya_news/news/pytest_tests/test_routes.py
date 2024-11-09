from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home_page(client):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_detail_page(client, detail_url):
    response = client.get(detail_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'user, status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND)
    )
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_availability_for_comment_edit_and_delete(
    user, status, name, comment
):
    url = reverse(name, kwargs={'pk': comment.id})
    response = user.get(url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'name',
    ('users:login', 'users:logout', 'users:signup'),
)
def test_pages_availability(name, client):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
