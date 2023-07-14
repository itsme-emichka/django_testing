from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestAnonymousPages(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Тестовая записка',
            text='Тестовый текст',
            slug='test-note',
            author=cls.author,
        )
        cls.login_url = reverse('users:login')

    def test_pages_for_all(self):
        names = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in names:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anonymous_redirects(self):
        names_args = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', self.note.slug),
            ('notes:edit', self.note.slug),
            ('notes:delete', self.note.slug),
        )
        for name, arg in names_args:
            with self.subTest(name=name):
                if arg is not None:
                    url = reverse(name, args=(arg,))
                else:
                    url = reverse(name)
                response = self.client.get(url)
                expected_url = f'{self.login_url}?next={url}'
                self.assertRedirects(response, expected_url)


class TestNotes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Тестовая записка',
            text='Тестовый текст',
            slug='test-note',
            author=cls.author,
        )

    def test_pages_for_user(self):
        names = (
            'notes:list',
            'notes:success',
            'notes:add',
        )
        for name in names:
            with self.subTest(name=name):
                self.client.force_login(self.author)
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_editing(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        names = (
            'notes:detail',
            'notes:edit',
            'notes:delete',
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in names:
                with self.subTest(name=name, user=user):
                    response = self.client.get(
                        reverse(name, args=(self.note.slug,))
                    )
                    self.assertEqual(response.status_code, status)
