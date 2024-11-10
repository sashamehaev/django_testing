from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

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
        cls.notes_delete_url = reverse('notes:delete', args=(cls.note.slug,))

        return super().setUpTestData()
