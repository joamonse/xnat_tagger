import logging

import requests
from getpass import getpass


class Session:
    def __init__(self, username, password="", password_text="Password: "):
        self.session = requests.session()
        if password == "":
            password = getpass(password_text)
        self.session.auth = (username, password)

        self.logger = logging.getLogger("requests")
        self.logger.setLevel("WARNING")

    def get(self, url, **kwargs):
        whiling = True
        r = None
        while whiling:
            try:
                self.logger.info("Got get requests")
                r = self.session.get(url, **kwargs)
                if r.status_code != requests.codes.ok:
                    self.logger.error(f"Get request to {url} returned status code {r.status_code}:\n{r.text} ")
                whiling = False
            except requests.exceptions.RequestException:
                self.logger.warning(f"Exception raised during get requests. Retrying", exc_info=True)
        self.logger.debug("Get request ended")
        return r

    def put(self, url, **kwargs):
        whiling = True
        r = None
        while whiling:
            try:
                self.logger.info("Got get requests")
                r = self.session.put(url, **kwargs)
                if r.status_code != requests.codes.ok:
                    self.logger.error(f"Get request to {url} returned status code {r.status_code}:\n{r.text} ")
                whiling = False
            except requests.exceptions.RequestException:
                self.logger.warning(f"Exception raised during get requests. Retrying", exc_info=True)
        self.logger.debug("Get request ended")
        return r

    def post(self, url, **kwargs):
        whiling = True
        r = None
        while whiling:
            try:
                self.logger.info("Got get requests")
                r = self.session.post(url, **kwargs)
                if r.status_code != requests.codes.ok:
                    self.logger.error(f"Get request to {url} returned status code {r.status_code}:\n{r.text} ")
                whiling = False
            except requests.exceptions.RequestException:
                self.logger.warning(f"Exception raised during get requests. Retrying", exc_info=True)
        self.logger.debug("Get request ended")
        return r

    def delete(self, url, **kwargs):
        whiling = True
        r = None
        while whiling:
            try:
                self.logger.info("Got get requests")
                r = self.session.delete(url, **kwargs)
                if r.status_code != requests.codes.ok:
                    self.logger.error(f"Get request to {url} returned status code {r.status_code}:\n{r.text} ")
                whiling = False
            except requests.exceptions.RequestException:
                self.logger.warning(f"Exception raised during get requests. Retrying", exc_info=True)
        self.logger.debug("Get request ended")
        return r