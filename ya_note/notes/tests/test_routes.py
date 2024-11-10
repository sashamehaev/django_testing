from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.tests.utils import TestFixture

User = get_user_model()


class TestRoutes(TestFixture):

    @classmethod
    def setUpTestData(cls):
        cls.notes_home_url = reverse('notes:home')
        cls.login_url = reverse('users:login')
        return super().setUpTestData()

    def test_home_availability_for_anonymous_user(self):
        response = self.client.get(self.notes_home_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        self.client.force_login(self.user)
        for url in (
            self.notes_add_url,
            self.notes_list_url,
            self.notes_success_url
        ):
            with self.subTest(url=url):
                response = self.user_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.user_client, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for url in (
                self.notes_detail_url,
                self.notes_delete_url,
                self.notes_edit_url
            ):
                with self.subTest(url=url):
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        for url in (
            self.notes_list_url,
            self.notes_success_url,
            self.notes_add_url,
            self.notes_detail_url,
            self.notes_edit_url,
            self.notes_delete_url,
        ):
            with self.subTest(url=url):
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_pages_availability(self):
        for name in ('users:login', 'users:logout', 'users:signup'):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
