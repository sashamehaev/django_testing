from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from notes.tests.utils import TestFixture

User = get_user_model()


class TestContent(TestFixture):

    def test_notes_list_for_different_users(self):
        users_statuses = (
            (self.author_client, True),
            (self.user_client, False),
        )
        for user, note_in_list in users_statuses:
            with self.subTest(user=user, note_in_list=note_in_list):
                response = user.get(self.notes_list_url)
                notes = response.context['object_list']
                self.assertIs(self.note in notes, note_in_list)

    def test_pages_contains_form(self):
        pages_contains = (
            self.notes_add_url,
            self.notes_edit_url
        )
        for url in pages_contains:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
