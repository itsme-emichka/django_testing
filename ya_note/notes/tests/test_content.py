from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

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

    def test_note_in_context(self):
        users__in_list = (
            (self.author, True),
            (self.reader, False),
        )
        for user, in_list in users__in_list:
            self.client.force_login(user)
            with self.subTest(user=user):
                response = self.client.get(reverse('notes:list'))
                objects = response.context['object_list']
                self.assertEqual((self.note in objects), in_list)

    def test_forms_are_in_add_edit_pages(self):
        names_args = (
            ('notes:add', None),
            ('notes:edit', self.note.slug)
        )
        for name, slug in names_args:
            self.client.force_login(self.author)
            with self.subTest(name=name):
                if slug is not None:
                    response = self.client.get(reverse(name, args=(slug,)))
                else:
                    response = self.client.get(reverse(name))
                self.assertIn('form', response.context)
