from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note


User = get_user_model()

class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create(
            username='Читатель простой'
        )

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

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.user, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        slug = self.note.slug,
        urls = (
            ('notes:detail', slug),
            ('notes:edit', slug),
            ('notes:delete', slug),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name, args in urls:  
                with self.subTest(user=user, name=name):        
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        slug = self.note.slug,
        urls = (
            ('notes:detail', slug),
            ('notes:edit', slug),
            ('notes:delete', slug),
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
