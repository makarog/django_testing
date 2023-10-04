import pytest
from django.contrib.auth import get_user_model
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone
from django.urls import reverse

from news.models import News, Comment


User = get_user_model()


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):  # Вызываем фикстуру автора и клиента.
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def news():
    news = News.objects.create(  # Создаём объект заметки.
        title='Заголовок',
        text='Текст заметки'
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def form_data():
    return {'text': 'Новый текст'}


@pytest.fixture
def all_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    return all_news


@pytest.fixture
def comment_data(news, author):
    now = timezone.now()
    for index in range(5):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def id_news_for_args(news):
    return news.id,


@pytest.fixture
def detail_url(id_news_for_args):
    detail_url = reverse('news:detail', args=(id_news_for_args))
    return detail_url


@pytest.fixture
def id_comment_for_args(comment):
    return comment.id,


@pytest.fixture
def edit_url(id_comment_for_args):
    edit_url = reverse('news:edit', args=(id_comment_for_args))
    return edit_url


@pytest.fixture
def delite_url(id_comment_for_args):
    delite_url = reverse('news:delete', args=(id_comment_for_args))
    return delite_url
