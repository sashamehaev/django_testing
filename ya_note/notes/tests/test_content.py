from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestFixture(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )
        cls.notes_list_url = reverse('notes:list')
        cls.notes_edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.notes_add_url = reverse('notes:add')
        
        return super().setUpTestData()


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
            with self.subTest():
                self.client.force_login(self.author)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
