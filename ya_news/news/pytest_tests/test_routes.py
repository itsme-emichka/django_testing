from http import HTTPStatus
import pytest

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
        'name, pk',
        (
            ('news:home', None),
            ('news:detail', pytest.lazy_fixture('post_id')),
            ('news:home', None),
            ('news:home', None),
            ('news:home', None),
        )
)
def test_anonymus_access_pages(name, pk, client):
    url = reverse(name, args=pk)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'authorized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
    )
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_user_permission_comment_edit_delete(
    name, authorized_client, expected_status, comment
):
    url = reverse(name, args=(comment.id,))
    response = authorized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_anonymous_redirects(client, name, comment):
    url = reverse(name, args=(comment.id,))
    login_url = reverse('users:login')
    response = client.get(url)
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
