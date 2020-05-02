import logging
import requests
import re
import random
from datetime import datetime

logger = logging.getLogger('telegram-bot.' + __name__)


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class PhotoUrlsIsEmptyError(Error):
    pass


class GooglePhotosAlbum():

    def __init__(self, album_url, cache_ttl=60*15):
        self.cache_ttl = cache_ttl
        self.downloaded_at = None
        self.album_url = album_url
        self._photo_urls = []
        self._download_photo_urls()

    @property
    def photo_urls(self):
        if (datetime.now() - self.downloaded_at).total_seconds() > self.cache_ttl:
            self._download_photo_urls()
        return self._photo_urls

    def random_photo_url(self):
        """Returns an url to random photo in the album.

        Returns:
            str: Url to a photo
        """
        try:
            return random.choice(self.photo_urls)
        except IndexError:
            raise NoPhotoUrlsFoundError

    def _download_photo_urls(self):
        link_regex = r"(https:\/\/lh3\.googleusercontent\.com\/[a-zA-Z0-9\-_]{128,})"
        try:
            r = requests.get(self.album_url)
            r.raise_for_status()
            self.downloaded_at = datetime.now()
            photo_urls = re.findall(link_regex, r.text)
            photo_urls_without_album_covers = photo_urls[1:-1]
            self._photo_urls = photo_urls_without_album_covers
        except Exception as e:
            logger.exception("Fetching google photos urls")
