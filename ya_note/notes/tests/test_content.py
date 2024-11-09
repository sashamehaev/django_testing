from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

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

    def test_notes_list_for_different_users(self):
        users_statuses = (
            (self.author, True),
            (self.user, False),
        )
        url = reverse('notes:list')
        for user, note_in_list in users_statuses:
            with self.subTest():
                self.client.force_login(user)
                response = self.client.get(url)
                object_list = response.context['object_list']
                assert (self.note in object_list) is note_in_list

    def test_pages_contains_form(self):
        pages_contains = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for name, args in pages_contains:
            with self.subTest():
                self.client.force_login(self.author)
                url = reverse(name, args=args)
                response = self.client.get(url)
                assert 'form' in response.context
                assert isinstance(response.context['form'], NoteForm)
