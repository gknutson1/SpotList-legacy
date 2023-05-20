import logging
import time
from datetime import datetime, timezone

import requests

import cfg
from playlist import Playlist


class AuthorizationException(Exception):
    pass


class User:
    spotify_id: str
    display_name: str
    access_token: str
    refresh_token: str
    expires_at: float
    app_token: str

    def __init__(self, spotify_id: str, token: str) -> None:
        search = cfg.db.execute(f"SELECT * FROM users where spotify_id = '{spotify_id}' and app_password = '{token}'")

        user = search.fetchone()

        # fetchone() returns None if there are no more results to grab, so we can check user for None to see if the
        # login info was correct
        if not user:
            logging.info(f"login attempt with '{token}' as {spotify_id} failed")
            raise AuthorizationException(f"Could not find user '{spotify_id}' with token '{token}' in database")

        logging.info(f"login attempt with '{token}' as {spotify_id} succeeded")
        self.spotify_id = user[0]
        self.display_name = user[1]
        self.access_token = user[2]
        self.refresh_token = user[3]
        self.expires_at = user[4]
        self.app_token = user[5]

    def refresh(self):
        headers = {'grant_type': 'refresh_token', 'Authorization': self.refresh_token}
        parameters = {'Authorization': cfg.auth_header, 'Content-Type': 'application/x-www-form-urlencoded'}

        request = requests.post(f'{cfg.auth_url}/api/token', headers=headers, params=parameters)
        request.raise_for_status()
        request = request.json()

        self.access_token = request['access_token']
        self.expires_at = request['expires_in'] + time.time()

        cfg.db.execute(f"""
            UPDATE users SET 
                access_token = '{self.access_token}', 
                expires_at = '{self.expires_at}' 
            WHERE spotify_id = '{self.spotify_id}'
            """)

        cfg.db.commit()

    def call_api(self, method: str, endpoint: str, params: dict = None, raw_url: bool = False) -> dict:
        """
        Uses the `requests` library to send requests to Spotify. Refreshes user token if needed. Should not be called
        directly - use the below wrappers (get, delete, etc.) instead.
        :param method: Type of request (get, delete, etc.) to preform
        :param endpoint: The path to use for the request
        :param params: Any parameters to pass to Spotify with the request
        :param raw_url: If false, `endpoint` will be appended to the api url. If true, `endpoint` will be used directly.
        :return: The JSON response from Spotify, deserialized to a dict
        """

        # If the access token has expired, refresh the token.
        if self.expires_at <= datetime.now(timezone.utc).timestamp():
            self.refresh()

        headers = {'Authorization': f'Bearer {self.access_token}', 'Content-Type': 'application/json'}
        response = requests.request(
                method,
                f'{cfg.api_url}/v1{endpoint}' if not raw_url else endpoint,
                headers=headers,
                params=params
                )
        response.raise_for_status()
        return response.json()

    def get(self, endpoint: str, params: dict = None, raw_url: bool = False) -> dict:
        """
        Send a GET request to the Spotify API
        :param endpoint: The path to use for the request
        :param params: Any parameters to pass to Spotify with the request
        :param raw_url: If false, `endpoint` will be appended to the api url. If true, `endpoint` will be used directly.
        :return: The JSON response from Spotify, deserialized to a dict
        """
        return self.call_api("get", endpoint, params, raw_url)

    def delete(self, endpoint: str, params: dict = None, raw_url: bool = False) -> dict:
        """
        Send a DELETE request to the Spotify API
        :param endpoint: The path to use for the request
        :param params: Any parameters to pass to Spotify with the request
        :param raw_url: If false, `endpoint` will be appended to the api url. If true, `endpoint` will be used directly.
        :return: The JSON response from Spotify, deserialized to a dict
        """
        return self.call_api("delete", endpoint, params, raw_url)

    def post(self, endpoint: str, params: dict = None, raw_url: bool = False) -> dict:
        """
        Send a POST request to the Spotify API
        :param endpoint: The path to use for the request
        :param params: Any parameters to pass to Spotify with the request
        :param raw_url: If false, `endpoint` will be appended to the api url. If true, `endpoint` will be used directly.
        :return: The JSON response from Spotify, deserialized to a dict
        """
        return self.call_api("post", endpoint, params, raw_url)

    def put(self, endpoint: str, params: dict = None, raw_url: bool = False) -> dict:
        """
        Send a PUT request to the Spotify API
        :param endpoint: The path to use for the request
        :param params: Any parameters to pass to Spotify with the request
        :param raw_url: If false, `endpoint` will be appended to the api url. If true, `endpoint` will be used directly.
        :return: The JSON response from Spotify, deserialized to a dict
        """
        return self.call_api("put", endpoint, params, raw_url)
