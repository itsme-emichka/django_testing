from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestAddNotes(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note_form = {
            'title': 'Тестовый заголовок для формы',
            'text': 'Тестовый текст для формы',
            'slug': 'test-slug-for-form',
        }

    def test_authorized_user_can_add_note(self):
        self.client.force_login(self.author)
        response = self.client.post(reverse('notes:add'), data=self.note_form)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.note_form['title'])
        self.assertEqual(new_note.text, self.note_form['text'])
        self.assertEqual(new_note.slug, self.note_form['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_cant_add_note(self):
        login_url = reverse('users:login')
        url = reverse('notes:add')
        response = self.client.post(url, data=self.note_form)
        self.assertEqual(Note.objects.count(), 0)
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)

    def test_empty_slug(self):
        url = reverse('notes:add')
        self.note_form.pop('slug')
        self.client.force_login(self.author)
        response = self.client.post(url, data=self.note_form)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.note_form['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNotesEdit(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Тестовая записка',
            text='Тестовый текст',
            slug='test-note',
            author=cls.author,
        )
        cls.note_form = {
            'title': 'Тестовый заголовок для формы',
            'text': 'Тестовый текст для формы',
            'slug': 'test-slug-for-form',
        }

    def test_slug_is_unique(self):
        self.note_form['slug'] = self.note.slug
        self.client.force_login(self.author)
        response = self.client.post(reverse('notes:add'), data=self.note_form)
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        self.client.force_login(self.author)
        response = self.client.post(url, data=self.note_form)
        self.assertRedirects(response, reverse('notes:success'))
        edited_note = Note.objects.get()
        self.assertEqual(edited_note.title, self.note_form['title'])
        self.assertEqual(edited_note.text, self.note_form['text'])
        self.assertEqual(edited_note.slug, self.note_form['slug'])

    def test_author_can_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        self.client.force_login(self.author)
        response = self.client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        self.client.force_login(self.reader)
        response = self.client.post(url, data=self.note_form)
        assert response.status_code == HTTPStatus.NOT_FOUND
        note = Note.objects.get()
        self.assertNotEqual(note.title, self.note_form['title'])
        self.assertNotEqual(note.text, self.note_form['text'])
        self.assertNotEqual(note.slug, self.note_form['slug'])

    def test_other_user_cant_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        self.client.force_login(self.reader)
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
