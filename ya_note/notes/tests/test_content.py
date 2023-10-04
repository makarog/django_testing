from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestContent(TestCase):
    LIST_NOTES_URL = reverse('notes:list')
    NOTE_ADD_URL = reverse('notes:add')

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            username='author'
        )
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.user,
            slug='slug1'
        )

        cls.anyuser = User.objects.create(
            username='anyuser'
        )
        cls.anyuser_client = Client()
        cls.anyuser_client.force_login(cls.anyuser)
        cls.note_anyuser = Note.objects.create(
            title='Другой Заголовок',
            text='Другой Текст',
            author=cls.anyuser,
            slug='slug2'
        )

    def test_note_on_list(self):
        response = self.auth_client.get(self.LIST_NOTES_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_on_list_any_user(self):
        response = self.auth_client.get(self.LIST_NOTES_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.note_anyuser, object_list)

    def test_create_note_page_contains_form(self):
        response = self.auth_client.get(self.NOTE_ADD_URL)
        self.assertIn('form', response.context)

    def test_edit_note_page_contains_form(self):
        slug = self.note.slug,
        url = reverse('notes:edit', args=slug)
        response = self.auth_client.get(url)
        self.assertIn('form', response.context)
