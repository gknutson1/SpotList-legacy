import time
import uuid
from typing import Annotated

import requests
from fastapi import FastAPI, HTTPException, Header, status
from fastapi.responses import JSONResponse

import cfg
from user import User, AuthorizationException

app = FastAPI(
        title="SpotList API",
        description="Allows users to crate automated playlists based on rulesets",
        version="v0.0.1"
        )


@app.exception_handler(AuthorizationException)
async def authorization_exception_handler(request, exception: AuthorizationException):
    return JSONResponse('username or password incorrect', status.HTTP_401_UNAUTHORIZED)


@app.exception_handler(requests.HTTPError)
async def http_exception_handler(request, exception: requests.HTTPError):
    return JSONResponse(
            'encountered an error when communicating with the Spotify API',
            status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post("/new", status_code=status.HTTP_201_CREATED)
async def create_playlist(user_id: Annotated[str, Header()], token: Annotated[str, Header()]):
    return HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@app.get("/rules/{playlist_id}", status_code=status.HTTP_200_OK)
async def get_rules(user_id: Annotated[str, Header()], token: Annotated[str, Header()], playlist_id: str):
    return HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@app.put("/rules/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def put_rules(user_id: Annotated[str, Header()], token: Annotated[str, Header()], playlist_id: str):
    return HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@app.put("/build/{playlist_id}", status_code=status.HTTP_201_CREATED)
async def build_playlist(user_id: Annotated[str, Header()], token: Annotated[str, Header()], playlist_id: str):
    return HTTPException(status.HTTP_501_NOT_IMPLEMENTED)




@app.get("/auth", status_code=status.HTTP_303_SEE_OTHER)
async def get_auth_link():
    # Use our credentials to get the authorization url from Spotify
    parameters = {"response_type": "code", "client_id": cfg.client_id,
                  "redirect_uri" : f"{cfg.redirect_uri}",
                  "scope"        : "playlist-read-private playlist-modify-private playlist-modify-public",
                  # 'state' will be passed back to us after the user logs in, allowing us to identify what client
                  # the user belongs to. The user will use this to authenticate to SpotList as well.
                  "state"        : uuid.uuid4().hex,
                  "show_dialog"  : "true"}
    request = requests.get(f"https://accounts.spotify.com/authorize", params=parameters)
    request.raise_for_status()
    # Send the URL back to the user. All further requests from the user will need the token.
    return request.url


# Once the user has authenticated with Spotify, they will be redirected here with their authorization code.
@app.get("/callback", status_code=status.HTTP_200_OK)
async def get_token(code: str, state: str):
    # Exchange the temporary authorization code for (semi-)permanent authorization credentials
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": cfg.auth_header}
    parameters = {"grant_type"  : "authorization_code",
                  "code"        : code,
                  "redirect_uri": f"{cfg.redirect_uri}"}
    request = requests.post(f"{cfg.auth_url}/api/token", params=parameters, headers=headers)
    request.raise_for_status()
    user_auth = request.json()

    # Call the /me endpoint to get the user's spotify ID to use as the primary key for the database
    headers = {'Authorization': f'Bearer {user_auth["access_token"]}', 'Content-Type': 'application/json'}
    request = requests.get(f'{cfg.api_url}/v1/me', headers=headers)
    request.raise_for_status()
    user_data = request.json()

    cfg.db.execute(
            f"""
        INSERT INTO users
            (spotify_id, 
             display_name,
             access_token, 
             refresh_token, 
             expires_at, 
             app_password)
        VALUES 
            ('{user_data['id']}', 
             '{user_data['display_name']}',
             '{user_auth['access_token']}', 
             '{user_auth['refresh_token']}', 
             '{user_auth['expires_in'] + time.time()}',
             '{state}')
        """
            )

    cfg.db.commit()

    return {'spotify_id': user_data['id'], 'token': state}
