from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.utils import TestFixture

User = get_user_model()


class TestLogic(TestFixture):

    @classmethod
    def setUpTestData(cls):
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        return super().setUpTestData()

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        notes_count = Note.objects.count()
        response = self.author_client.post(
            self.notes_add_url,
            data=self.form_data
        )
        notes_count_after_request = Note.objects.count()
        self.assertGreater(notes_count_after_request, notes_count)
        self.assertRedirects(response, self.notes_success_url)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_not_unique_slug(self):
        notes_count = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(
            self.notes_add_url,
            data=self.form_data
        )
        notes_count_after_request = Note.objects.count()
        self.assertEqual(notes_count_after_request, notes_count)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )

    def test_empty_slug(self):
        Note.objects.all().delete()
        notes_count = Note.objects.count()
        self.form_data.pop('slug')
        response = self.author_client.post(
            self.notes_add_url,
            data=self.form_data
        )
        notes_count_after_request = Note.objects.count()
        self.assertGreater(notes_count_after_request, notes_count)
        self.assertRedirects(response, self.notes_success_url)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.notes_edit_url, self.form_data)
        self.assertRedirects(response, self.notes_success_url)
        new_note = Note.objects.get(pk=self.note.id)
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_other_user_cant_edit_note(self):
        response = self.user_client.post(self.notes_edit_url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.author, self.author)

    def test_author_can_delete_note(self):
        notes_count = Note.objects.count()
        response = self.author_client.post(self.notes_delete_url)
        notes_count_after_request = Note.objects.count()
        self.assertRedirects(response, self.notes_success_url)
        self.assertGreater(notes_count, notes_count_after_request)

    def test_other_user_cant_delete_note(self):
        notes_count = Note.objects.count()
        response = self.user_client.post(self.notes_delete_url)
        notes_count_after_request = Note.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(notes_count, notes_count_after_request)
