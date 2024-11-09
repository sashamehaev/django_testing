from http import HTTPStatus

import pytest
from django.conf import settings
from django.test import Client
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

NEW_COMMENT = {'text': 'Новый комментарий'}


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, detail_url):
    client.post(detail_url, data=NEW_COMMENT)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(
    author,
    news,
    detail_url,
    url_to_comments
):
    client = Client()
    client.force_login(author)
    response = client.post(detail_url, data=NEW_COMMENT)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == settings.NEW_COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, detail_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(
    author_client,
    comment,
    url_to_comments,
    delete_url
):
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_edit_comment(
    author_client,
    comment,
    url_to_comments,
    edit_url
):
    response = author_client.post(edit_url, data=NEW_COMMENT)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == settings.NEW_COMMENT_TEXT


def test_user_cant_delete_comment_of_another_user(
    not_author_client,
    comment,
    delete_url
):
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_user_cant_edit_comment_of_another_user(
    not_author_client,
    comment,
    edit_url
):
    response = not_author_client.post(edit_url, data=NEW_COMMENT)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == settings.COMMENT_TEXT
