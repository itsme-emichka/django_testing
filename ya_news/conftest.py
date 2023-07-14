import pytest
from datetime import datetime, timedelta, date

from django.utils import timezone
from django.conf import settings

from news.models import News, Comment


@pytest.fixture
def comment_author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(comment_author, client):
    client.force_login(comment_author)
    return client


@pytest.fixture
def post():
    return News.objects.create(
        title='Тестовая новость',
        text='Тестовый текст',
        date=date(2002, 7, 7)
    )


@pytest.fixture
def post_id(post):
    return post.id,


@pytest.fixture
def posts():
    all_news = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        date = datetime.today() - timedelta(days=index)
        all_news.append(
            News(
                title=f'Новость {index}',
                text=f'Текст {index}',
                date=date,
            )
        )
    return News.objects.bulk_create(all_news)


@pytest.fixture
def comment(post, comment_author):
    return Comment.objects.create(
        news=post,
        author=comment_author,
        text='Текст комментария',
    )


@pytest.fixture
def comments(post, comment_author):
    comments = []
    for index in range(2):
        created = timezone.now() + timedelta(days=index)
        comment = Comment.objects.create(
            news=post,
            author=comment_author,
            text=f'Текст {index}',
        )
        comment.created = created
        comment.save()
        comments.append(comment)
    return comments


@pytest.fixture
def comment_id(comment):
    return comment.id,


@pytest.fixture
def comment_form():
    return {
        'text': 'Еще один тестовый текст'
    }


@pytest.fixture
def comment_form_edit():
    return {
        'text': 'Еще один тестовый текст, отредактированный'
    }


@pytest.fixture
def bad_comment_form():
    return {
        'text': 'Еще один редиска текст'
    }
