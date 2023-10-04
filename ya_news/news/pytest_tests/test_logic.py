from http import HTTPStatus
import pytest

from pytest_django.asserts import assertRedirects, assertFormError
from django.contrib.auth import get_user_model

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


User = get_user_model()


@pytest.mark.django_db
def test_user_can_create_comment(
    author_client, form_data,
    news, author, detail_url
):
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == 'Новый текст'
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, detail_url):
    client.post(detail_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_use_bad_words(author_client, detail_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(
        detail_url,
        data=bad_words_data
    )
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, detail_url, delite_url):
    url_to_comments = detail_url + '#comments'
    response = author_client.delete(delite_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_edit_comment(
    author_client,
    form_data, comment,
    detail_url,
    edit_url
):
    response = author_client.post(edit_url, form_data)
    url_to_comments = detail_url + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == 'Новый текст'


def test_other_user_cant_edit_comment(
    admin_client, form_data,
    comment, edit_url
):
    response = admin_client.post(edit_url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    note_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == note_from_db.text


def test_other_user_cant_delete_note(admin_client, comment, delite_url):
    response = admin_client.post(delite_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
