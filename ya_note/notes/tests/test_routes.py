from django.urls import reverse

from notes.tests.utils import TestFixture, STATUS_404, STATUS_200


class TestRoutes(TestFixture):

    def test_home_availability_for_anonymous_user(self):
        response = self.client.get(self.notes_home_url)
        self.assertEqual(response.status_code, STATUS_200)

    def test_pages_availability_for_auth_user(self):
        for url in (
            self.notes_add_url,
            self.notes_list_url,
            self.notes_success_url
        ):
            with self.subTest(url=url):
                response = self.user_client.get(url)
                self.assertEqual(response.status_code, STATUS_200)

    def test_pages_availability_for_different_users(self):
        users_statuses = (
            (self.author_client, STATUS_200),
            (self.user_client, STATUS_404),
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
        for url in (self.login_url, self.logout_url, self.signup_url):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, STATUS_200)
