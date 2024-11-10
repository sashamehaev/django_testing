import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from news.pytest_tests.constants import STATUS_404

pytestmark = pytest.mark.django_db

NEW_COMMENT = {'text': 'Новый комментарий'}


def test_anonymous_user_cant_create_comment(client, detail_url):
    comments_count = Comment.objects.count()
    client.post(detail_url, data=NEW_COMMENT)
    comments_count_after_request = Comment.objects.count()
    assert comments_count == comments_count_after_request


def test_user_can_create_comment(
    author_client,
    author,
    news,
    detail_url,
    url_to_comments
):
    comments_count = Comment.objects.all().delete()
    comments_count = Comment.objects.count()
    response = author_client.post(detail_url, data=NEW_COMMENT)
    comments_count_after_request = Comment.objects.count()
    assert comments_count_after_request > comments_count
    assertRedirects(response, url_to_comments)
    comment = Comment.objects.get()
    assert comment.text == NEW_COMMENT['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, detail_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    comments_count = Comment.objects.all().delete()
    comments_count = Comment.objects.count()
    response = author_client.post(detail_url, data=bad_words_data)
    comments_count_after_request = Comment.objects.count()
    assert comments_count == comments_count_after_request
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )


def test_author_can_delete_comment(
    author_client,
    comment,
    url_to_comments,
    delete_url
):
    comments_count = Comment.objects.count()
    response = author_client.delete(delete_url)
    comments_count_after_request = Comment.objects.count()
    assert comments_count > comments_count_after_request
    assertRedirects(response, url_to_comments)


def test_author_can_edit_comment(
    author_client,
    comment,
    url_to_comments,
    edit_url
):
    response = author_client.post(edit_url, data=NEW_COMMENT)
    assertRedirects(response, url_to_comments)
    comment_from_db = Comment.objects.get(pk=comment.id)
    comment.text = NEW_COMMENT['text']
    assert comment_from_db.text == comment.text
    assert comment_from_db.news == comment.news
    assert comment_from_db.author == comment.author


def test_user_cant_delete_comment_of_another_user(
    not_author_client,
    comment,
    delete_url
):
    comments_count = Comment.objects.count()
    response = not_author_client.delete(delete_url)
    comments_count_after_request = Comment.objects.count()
    assert comments_count == comments_count_after_request
    assert response.status_code == STATUS_404


def test_user_cant_edit_comment_of_another_user(
    not_author_client,
    comment,
    edit_url
):
    response = not_author_client.post(edit_url, data=NEW_COMMENT)
    assert response.status_code == STATUS_404
    comment_from_db = Comment.objects.get(pk=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author
    assert comment.news == comment_from_db.news
