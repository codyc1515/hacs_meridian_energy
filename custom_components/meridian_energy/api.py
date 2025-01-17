"""Meridian Energy API."""

import logging
import requests

from datetime import datetime, timedelta
from bs4 import BeautifulSoup


_LOGGER = logging.getLogger(__name__)


class MeridianEnergyApi:
    """Define the Meridian Energy API."""

    def __init__(self, email, password):
        """Initialise the API."""
        self._email = email
        self._password = password
        self._url_base = "https://secure.meridianenergy.co.nz/"
        self._token = None
        self._data = None
        self._session = requests.Session()

    def token(self):
        """Get token from the Meridian Energy API."""
        response = self._session.get(self._url_base)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            self._token = soup.find("input", {"name": "authenticity_token"})["value"]
            self.login()
        else:
            _LOGGER.error("Failed to retrieve the token page.")

    def login(self):
        """Login to the API."""
        result = False
        form_data = {
            "authenticity_token": self._token,
            "email": self._email,
            "password": self._password,
            "commit": "Login",
        }
        loginResult = self._session.post(
            self._url_base + "customer/login", data=form_data
        )
        if loginResult.status_code == 200:
            _LOGGER.debug("Logged in")
            self.get_data()
            result = True
        else:
            _LOGGER.error("Could not login")
        return result

    def get_data(self):
        """Get data from the API."""
        today = datetime.now().strftime("%d/%m/%Y")
        days_ago = (datetime.now() - timedelta(days=365)).strftime("%d/%m/%Y")

        response = self._session.get(
            self._url_base
            + "reports/consumption_data/detailed_export?date_from="
            + days_ago
            + "&date_to="
            + today
            + "&all_icps=&download=true"
        )
        if response.status_code == 200:
            data = response.text
            if not data:
                _LOGGER.warning(
                    "Fetched consumption successfully but there was no data"
                )
                return False
            return data
        else:
            _LOGGER.error("Could not fetch consumption")
            return data
