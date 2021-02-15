#!/usr/bin/env python3
# coding=utf-8

import praw
import praw.models
import pytest

from bulkredditdownloader.resource import Resource
from bulkredditdownloader.site_downloaders.gallery import Gallery


@pytest.fixture()
def reddit_submission() -> praw.models.Submission:
    rd = praw.Reddit(client_id='U-6gk4ZCh3IeNQ', client_secret='7CZHY6AmKweZME5s50SfDGylaPg', user_agent='test')
    return rd.submission(id='ljyy27')


def test_gallery(reddit_submission: praw.models.Submission):
    gallery = Gallery(reddit_submission)
    results = gallery.download()
    assert len(results) == 4
    assert all([isinstance(result, Resource) for result in results])