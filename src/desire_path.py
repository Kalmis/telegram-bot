import requests
import logging

logger = logging.getLogger('telegram-bot.' + __name__)


class DesirePathError(Exception):
    pass


class DesirePathApi():

    """Implements functions for fetching information from Desire path

    Attributes:
        url (str): Desire path api url, including version number
    """

    def __init__(self, url):
        self.url = url

    def listing_info_from_url(self, listing_url):
        """Fetch information of oikotie listing from Desire path service based on oikotie url

        Args:
            listing_url (str): Full url to a oikotie listing

        Returns:
            dict: Data dict

        Raises:
            DesirePathError: Error fetching or parsing response
        """
        full_url = f"{self.url}/oikotie/{listing_url}"
        try:
            r = requests.get(full_url, timeout=20)
            r.raise_for_status()
            data = r.json()
            if 'error' in data:
                logger.error(data['error'])
                raise DesirePathError
            return data
        except Exception as e:
            logger.exception("Listing fetch error")
            raise DesirePathError from e
