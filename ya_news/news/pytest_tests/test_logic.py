from http import HTTPStatus
import pytest

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertRaisesMessage
from django.core.exceptions import ValidationError

from news.models import Comment
from news.forms import WARNING


@pytest.mark.django_db
def test_anonymous_cant_comment(client, comment_form, post):
    url = reverse('news:detail', args=(post.id,))
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.post(url, data=comment_form)
    expected_count = 0
    assert Comment.objects.count() == expected_count
    assertRedirects(response, expected_url)


@pytest.mark.django_db
def test_authorized_user_can_comment(admin_client, post, comment_form):
    url = reverse('news:detail', args=(post.id,))
    admin_client.post(url, data=comment_form)
    expected_count = 1
    assert Comment.objects.count() == expected_count
    new_comment = Comment.objects.get()
    assert new_comment.text == comment_form['text']


def test_bad_comment(admin_client, post, bad_comment_form):
    url = reverse('news:detail', args=(post.id,))
    admin_client.post(url, data=bad_comment_form)
    expected_count = 0
    assert Comment.objects.count() == expected_count
    assertRaisesMessage(ValidationError, WARNING)


def test_author_can_edit_comment(author_client, comment, comment_form_edit):
    url = reverse('news:edit', args=(comment.id,))
    author_client.post(url, data=comment_form_edit)
    expected_count = 1
    assert Comment.objects.count() == expected_count
    edited_comment = Comment.objects.get()
    assert edited_comment.text == comment_form_edit['text']


def test_author_can_delete_comment(author_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    author_client.delete(url)
    expected_count = 0
    assert Comment.objects.count() == expected_count


def test_other_user_cant_edit_comment(
    admin_client, comment, comment_form_edit
):
    url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post(url, data=comment_form_edit)
    assert response.status_code == HTTPStatus.NOT_FOUND
    expected_count = 1
    assert Comment.objects.count() == expected_count
    assert Comment.objects.get().text == comment.text


def test_other_user_cant_delete_comment(admin_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = admin_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    expected_count = 1
    assert Comment.objects.count() == expected_count
