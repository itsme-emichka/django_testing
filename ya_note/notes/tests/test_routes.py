from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.tests.enums import Views

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
        cls.login_url = reverse(Views.LOGIN)

    def test_pages_for_all(self):
        names = (
            Views.HOME,
            Views.LOGIN,
            Views.LOGOUT,
            Views.SIGHNUP,
        )
        for name in names:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anonymous_redirects(self):
        names_args = (
            (Views.NOTE_LIST, None),
            (Views.SUCCESS, None),
            (Views.ADD_NOTE, None),
            (Views.NOTE_DETAIL, self.note.slug),
            (Views.EDIT_NOTE, self.note.slug),
            (Views.DELETE_NOTE, self.note.slug),
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
            Views.NOTE_LIST,
            Views.SUCCESS,
            Views.ADD_NOTE,
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
            Views.NOTE_DETAIL,
            Views.EDIT_NOTE,
            Views.DELETE_NOTE,
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in names:
                with self.subTest(name=name, user=user):
                    response = self.client.get(
                        reverse(name, args=(self.note.slug,))
                    )
                    self.assertEqual(response.status_code, status)
