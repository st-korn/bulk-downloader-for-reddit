#!/usr/bin/env python3

import logging
import pathlib
import re
import urllib.error
import urllib.request
from html.parser import HTMLParser

from praw.models import Submission

from bulkredditdownloader.errors import NotADownloadableLinkError
from bulkredditdownloader.site_downloaders.base_downloader import BaseDownloader

logger = logging.getLogger(__name__)


class Erome(BaseDownloader):
    def __init__(self, directory: pathlib.Path, post: Submission):
        super().__init__(directory, post)

    def download(self):
        try:
            images = self._get_links(self.post.url)
        except urllib.error.HTTPError:
            raise NotADownloadableLinkError("Not a downloadable link")

        if len(images) == 1:

            image = images[0]
            if not re.match(r'https?://.*', image):
                image = "https://" + image
            return [self._download_resource(image)]

        else:
            out = []
            for i, image in enumerate(images):
                if not re.match(r'https?://.*', image):
                    image = "https://" + image

                    out.append(self._download_resource(image))
            return out

    @staticmethod
    def _get_links(url: str) -> list[str]:
        content = []
        line_number = None

        # TODO: move to bs4 and requests
        class EromeParser(HTMLParser):
            tag = None

            def handle_starttag(self, tag, attrs):
                self.tag = {tag: {attr[0]: attr[1] for attr in attrs}}

        page_source = (urllib.request.urlopen(url).read().decode().split('\n'))

        """ FIND WHERE ALBUM STARTS IN ORDER NOT TO GET WRONG LINKS"""
        for i in range(len(page_source)):
            obj = EromeParser()
            obj.feed(page_source[i])
            tag = obj.tag

            if tag is not None:
                if "div" in tag:
                    if "id" in tag["div"]:
                        if tag["div"]["id"] == "album":
                            line_number = i
                            break

        for line in page_source[line_number:]:
            obj = EromeParser()
            obj.feed(line)
            tag = obj.tag
            if tag is not None:
                if "img" in tag:
                    if "class" in tag["img"]:
                        if tag["img"]["class"] == "img-front":
                            content.append(tag["img"]["src"])
                elif "source" in tag:
                    content.append(tag["source"]["src"])

        return [link for link in content if link.endswith("_480p.mp4") or not link.endswith(".mp4")]