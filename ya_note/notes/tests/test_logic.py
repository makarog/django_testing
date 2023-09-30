from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            username='author'
        )
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_user_can_create_note(self):
        url = reverse('notes:add')
        response = self.auth_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.user)

    def test_anonymous_user_cant_create_note(self):
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_not_unique_slug(self):
        url = reverse('notes:add')
        note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.user,
            slug='slug1'
        )
        self.form_data['slug'] = note.slug
        response = self.auth_client.post(url, data=self.form_data)
        self.assertFormError(response, 'form', 'slug', errors=(note.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        url = reverse('notes:add')
        self.form_data.pop('slug')
        response = self.auth_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.user,
            slug='slug1'
        )
        url = reverse('notes:edit', args=(note.slug,))
        response = self.auth_client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        note.refresh_from_db()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.user,
            slug='slug1'
        )
        url = reverse('notes:edit', args=(note.slug,))
        response = self.reader_client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=note.id)
        # Проверяем, что атрибуты объекта из БД равны атрибутам заметки до запроса.
        self.assertEqual(note.title, note_from_db.title)
        self.assertEqual(note.text, note_from_db.text)
        self.assertEqual(note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.user,
            slug='slug1'
        )
        slug = note.slug,
        url = reverse('notes:delete', args=slug)
        response = self.auth_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.user,
            slug='slug1'
        )
        slug = note.slug,
        url = reverse('notes:delete', args=slug)
        response = self.reader_client.post(url)
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
