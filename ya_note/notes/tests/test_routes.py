from http import HTTPStatus

import pytest

from pytest_django.asserts import assertRedirects

from django.urls import reverse


# Указываем в фикстурах встроенный клиент.
def test_home_availability_for_anonymous_user(client):
    # Адрес страницы получаем через reverse():
    url = reverse('notes:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',  # Имя параметра функции.
    # Значения, которые будут передаваться в name.
    ('notes:home', 'users:login', 'users:logout', 'users:signup')
)
# Указываем имя изменяемого параметра в сигнатуре теста.
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)  # Получаем ссылку на нужный адрес.
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('notes:list', 'notes:add', 'notes:success')
)
def test_pages_availability_for_auth_user(not_author_client, name):
    url = reverse(name)
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    # Предварительно оборачиваем имена фикстур
    # в вызов функции pytest.lazy_fixture().
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('notes:detail', 'notes:edit', 'notes:delete'),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, note, expected_status
):
    url = reverse(name, args=(note.slug,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('notes:detail', pytest.lazy_fixture('slug_for_args')),
        ('notes:edit', pytest.lazy_fixture('slug_for_args')),
        ('notes:delete', pytest.lazy_fixture('slug_for_args')),
        ('notes:add', None),
        ('notes:success', None),
        ('notes:list', None),
    ),
)
# Передаём в тест анонимный клиент, name проверяемых страниц и args:
def test_redirects(client, name, args):
    login_url = reverse('users:login')
    # Теперь не надо писать никаких if и можно обойтись одним выражением.
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


###############################################################
# news/tests/test_routes.py
# Импортируем класс HTTPStatus.
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )
        cls.user = User.objects.create(username='Мимо Крокодил')

    def test_home_availability_for_anonymous_user(self):
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        for name in ('notes:add', 'notes:list', 'notes:success'):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)


def test_availability_for_comment_edit_and_delete(self):
    users_statuses = (
        (self.author, HTTPStatus.OK),
        (self.reader, HTTPStatus.NOT_FOUND),
    )
    for user, status in users_statuses:
        # Логиним пользователя в клиенте:
        self.client.force_login(user)
        # Для каждой пары "пользователь - ожидаемый ответ"
        # перебираем имена тестируемых страниц:
        for name in ('news:edit', 'news:delete'):
            with self.subTest(user=user, name=name):
                url = reverse(name, args=(self.comment.id,))
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)


def test_redirect_for_anonymous_client(self):
    # Сохраняем адрес страницы логина:
    login_url = reverse('users:login')
    # В цикле перебираем имена страниц, с которых ожидаем редирект:
    for name in ('news:edit', 'news:delete'):
        with self.subTest(name=name):
            # Получаем адрес страницы редактирования или удаления комментария:
            url = reverse(name, args=(self.comment.id,))
            # Получаем ожидаемый адрес страницы логина,
            # на который будет перенаправлен пользователь.
            # Учитываем, что в адресе будет параметр next, в котором передаётся
            # адрес страницы, с которой пользователь был переадресован.
            redirect_url = f'{login_url}?next={url}'
            response = self.client.get(url)
            # Проверяем, что редирект приведёт именно на указанную ссылку.
            self.assertRedirects(response, redirect_url)
