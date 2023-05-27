import logging
import time
from datetime import datetime, timezone

import requests

import cfg
import models
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
            logging.info(f"login failed with '{token}' as {spotify_id}")
            raise AuthorizationException(f"Could not find user '{spotify_id}' with token '{token}' in database")

        logging.info(f"login succeeded with '{token}' as {spotify_id}")
        self.spotify_id = user["spotify_id"]
        self.display_name = user["display_name"]
        self.access_token = user["access_token"]
        self.refresh_token = user["refresh_token"]
        self.expires_at = user["expires_at"]
        self.app_token = user["app_password"]

    def refresh(self):
        logging.info(f"refreshing token for {self.refresh_token}")
        headers = {'grant_type': 'refresh_token', 'Authorization': self.refresh_token}
        parameters = {'Authorization': cfg.auth_header, 'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(f'{cfg.auth_url}/api/token', headers=headers, params=parameters)
        logging.info(f"got {response.status_code} from POST {response.url}")
        response.raise_for_status()
        response = response.json()

        self.access_token = response['access_token']
        self.expires_at = response['expires_in'] + time.time()

        cfg.db.execute(
            f"""
            UPDATE users SET 
                access_token = '{self.access_token}', 
                expires_at = '{self.expires_at}' 
            WHERE spotify_id = '{self.spotify_id}'
            """
            )

        cfg.db.commit()

    def get_playlists(self) -> list[models.Playlist]:
        query = cfg.db.execute(f"SELECT * FROM playlists WHERE owner = '{self.spotify_id}'")
        return [Playlist(**i) for i in query.fetchall()]

    def call_api(self, method: str, endpoint: str, params: dict = None, body: dict | bytes = None, raw_url: bool = False) -> dict:
        """
        Uses the `requests` library to send requests to Spotify. Refreshes user token if needed. Should not be called
        directly - use the below wrappers (get, delete, etc.) instead.
        :param method: Type of request (get, delete, etc.) to preform
        :param endpoint: The path to use for the request
        :param params: Any parameters to pass to Spotify with the request
        :param body: Data to send as the body of the request
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
                params=params,
                data=body
                )
        logging.info(f"got {response.status_code} from {method} {response.url}")
        response.raise_for_status()
        return response.json()

    def get(self, endpoint: str, params: dict = None, body: dict | bytes = None, raw_url: bool = False) -> dict:
        """
        Send a GET request to the Spotify API
        :param endpoint: The path to use for the request
        :param params: Any parameters to pass to Spotify with the request
        :param body: Data to send as the body of the request
        :param raw_url: If false, `endpoint` will be appended to the api url. If true, `endpoint` will be used directly.
        :return: The JSON response from Spotify, deserialized to a dict
        """
        return self.call_api("GET", endpoint, params, body, raw_url)

    def delete(self, endpoint: str, params: dict = None, body: dict | bytes = None, raw_url: bool = False) -> dict:
        """
        Send a DELETE request to the Spotify API
        :param endpoint: The path to use for the request
        :param params: Any parameters to pass to Spotify with the request
        :param body: Data to send as the body of the request
        :param raw_url: If false, `endpoint` will be appended to the api url. If true, `endpoint` will be used directly.
        :return: The JSON response from Spotify, deserialized to a dict
        """
        return self.call_api("DELETE", endpoint, params, body, raw_url)

    def post(self, endpoint: str, params: dict = None, body: dict | bytes = None, raw_url: bool = False) -> dict:
        """
        Send a POST request to the Spotify API
        :param endpoint: The path to use for the request
        :param params: Any parameters to pass to Spotify with the request
        :param body: Data to send as the body of the request
        :param raw_url: If false, `endpoint` will be appended to the api url. If true, `endpoint` will be used directly.
        :return: The JSON response from Spotify, deserialized to a dict
        """
        return self.call_api("POST", endpoint, params, body, raw_url)

    def put(self, endpoint: str, params: dict = None, body: dict | bytes = None, raw_url: bool = False) -> dict:
        """
        Send a PUT request to the Spotify API
        :param endpoint: The path to use for the request
        :param params: Any parameters to pass to Spotify with the request
        :param body: Data to send as the body of the request
        :param raw_url: If false, `endpoint` will be appended to the api url. If true, `endpoint` will be used directly.
        :return: The JSON response from Spotify, deserialized to a dict
        """
        return self.call_api("PUT", endpoint, params, body, raw_url)
