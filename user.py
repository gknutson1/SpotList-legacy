from time import gmtime

import requests

import cfg
from playlist import Playlist


class AuthorizationException(Exception):
    pass


class User:
    spotify_id: str
    access_token: str
    refresh_token: str
    expires_at: float
    app_token: str
    playlists: list[Playlist]

    def __init__(self, spotify_id: str, token: str) -> None:
        search = cfg.db.execute(
            f"SELECT * FROM users where spotify_id = '{spotify_id}' and app_password = '{token}'")

        user = search.fetchone()

        # fetchone() returns None if there are no more results to grab, so we can check user for None to see if the
        # login info was correct
        if not user:
            raise AuthorizationException(f"Could not find user '{spotify_id}' with token '{token}' in database")

        self.spotify_id = user[0]
        self.access_token = user[1]
        self.refresh_token = user[2]
        self.expires_at = user[3]
        self.app_token = user[4]

    def refresh(self):
        pass

    def call_api(self, method: str, endpoint: str, params: dict = None) -> dict:
        """
        Uses the `requests` library to send requests to Spotify. Refreshes user token if needed. Should not be called
        directly - use the below wrappers (get, delete, etc.) instead.
        :param method: Type of request (get, delete, etc.) to preform
        :param endpoint: The path to use for the request
        :param params: Any parameters to pass to Spotify with the request
        :return: The JSON response from Spotify, deserialized to a dict
        """
        if self.expires_at <= gmtime():
            pass
            self.refresh(self)

        headers = {'Authorization': f'Bearer {self.access_token}', 'Content-Type': 'application/json'}
        response = requests.request(method, f'{cfg.api_url}/v1{endpoint}', headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def get(self, endpoint: str, params: dict = None) -> dict:
        """
        Send a GET request to the Spotify API
        :param endpoint: The path to use for the request
        :param params: Any parameters to pass to Spotify with the request
        :return: The JSON response from Spotify, deserialized to a dict
        """
        return self.call_api("get", endpoint, params)

    def delete(self, endpoint: str, params: dict = None) -> dict:
        """
        Send a DELETE request to the Spotify API
        :param endpoint: The path to use for the request
        :param params: Any parameters to pass to Spotify with the request
        :return: The JSON response from Spotify, deserialized to a dict
        """
        return self.call_api("delete", endpoint, params)

    def post(self, endpoint: str, params: dict = None) -> dict:
        """
        Send a POST request to the Spotify API
        :param endpoint: The path to use for the request
        :param params: Any parameters to pass to Spotify with the request
        :return: The JSON response from Spotify, deserialized to a dict
        """
        return self.call_api("post", endpoint, params)

    def put(self, endpoint: str, params: dict = None) -> dict:
        """
        Send a PUT request to the Spotify API
        :param endpoint: The path to use for the request
        :param params: Any parameters to pass to Spotify with the request
        :return: The JSON response from Spotify, deserialized to a dict
        """
        return self.call_api("put", endpoint, params)
