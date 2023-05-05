import time
import uuid

import fastapi
import requests
from fastapi import FastAPI, HTTPException

import cfg
from user import User, AuthorizationException

app = FastAPI(
        title="SpotList API",
        description="Allows users to crate automated playlists based on rulesets",
        version="v0.0.1"
        )


def get_user(spotify_id: str, token: str) -> User:
    """
    wraps User, and raises a http 401 if the id/token is incorrect
    :param spotify_id:
    :param token:
    :return:
    """
    try:
        return User(spotify_id, token)
    except AuthorizationException as e:
        raise fastapi.HTTPException(401, e)


@app.post("/new/{user_id}", status_code=201)
async def create_playlist(user_id: str):
    pass


@app.get("/rules/{playlist_id}", status_code=200)
async def get_rules(playlist_id: str):
    pass


@app.put("/rules/{playlist_id}", status_code=204)
async def put_rules(playlist_id: str):
    pass


@app.put("/build/{playlist_id}", status_code=201)
async def build_playlist(playlist_id: str):
    pass


@app.get("/auth", status_code=303)
async def get_auth_link():
    # Use our credentials to get the authorization url from Spotify
    parameters = {"response_type": "code", "client_id": cfg.client_id,
                  "redirect_uri": f"{cfg.redirect_uri}",
                  "scope": "playlist-read-private playlist-modify-private playlist-modify-public",
                  # 'state' will be passed back to us after the user logs in, allowing us to identify what client
                  # the user belongs to. The user will use this to authenticate to SpotList as well.
                  "state": uuid.uuid4().hex,
                  "show_dialog": "true"}
    request = requests.get(f"https://accounts.spotify.com/authorize", params=parameters)
    if not 200 <= request.status_code <= 299:
        raise HTTPException(500, f"got status {request.status_code} from spotify when fetching authorization url")
    # Send the URL back to the user. All further requests from the user will need the token.
    return request.url


# Once the user has authenticated with Spotify, they will be redirected here with their authorization code.
@app.get("/callback", status_code=200)
async def get_token(code: str, state: str):
    # Exchange the temporary authorization code for (semi-)permanent authorization credentials
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": cfg.auth_header}
    parameters = {"grant_type": "authorization_code",
                  "code": code,
                  "redirect_uri": f"{cfg.redirect_uri}"}
    request = requests.post(f"{cfg.auth_url}/api/token", params=parameters, headers=headers)
    if not 200 <= request.status_code <= 299:
        raise HTTPException(500, f"got status {request.status_code} from spotify when getting authorization token")
    user_auth = request.json()

    # Call the /me endpoint to get the user's spotify ID to use as the primary key for the database
    headers = {'Authorization': f'Bearer {user_auth["access_token"]}', 'Content-Type': 'application/json'}
    request = requests.get(f'{cfg.api_url}/v1/me', headers=headers)
    if not 200 <= request.status_code <= 299:
        raise HTTPException(500, f"got status {request.status_code} from spotify when getting user data")
    user_data = request.json()

    cfg.db.execute(f"""
        INSERT INTO users
            (spotify_id, 
             access_token, 
             refresh_token, 
             expires_at, 
             app_password)
        VALUES 
            ('{user_data['id']}', 
             '{user_auth['access_token']}', 
             '{user_auth['refresh_token']}', 
             '{user_auth['expires_in'] + time.time()}',
             '{state}')
        """)

    cfg.db.commit()

    return {'spotify_id': user_data['id'], 'token': state}
