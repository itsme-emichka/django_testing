import pytest

from django.urls import reverse
from django.conf import settings


@pytest.mark.django_db
def test_posts_count_on_main(posts, client):
    response = client.get(reverse('news:home'))
    assert (
        len(
            response.context['object_list']
        ) == settings.NEWS_COUNT_ON_HOME_PAGE
    )


@pytest.mark.django_db
def test_news_sorting(posts, client):
    response = client.get(reverse('news:home'))
    all_dates = []
    for post in response.context['object_list']:
        all_dates.append(post.date)
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_sorting(comments, client, post):
    response = client.get(reverse('news:detail', args=(post.id,)))
    assert 'news' in response.context
    page_comments = response.context['news'].comment_set.all()
    print(page_comments[0].created)
    assert page_comments[0].created < page_comments[1].created


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, form_available',
    (
        (pytest.lazy_fixture('admin_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_comment_form(parametrized_client, form_available, post):
    response = parametrized_client.get(reverse('news:detail', args=(post.id,)))
    assert ('form' in response.context) is form_available
