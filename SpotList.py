import logging
import time
import uuid
from typing import Annotated

import requests
from fastapi import FastAPI, HTTPException, Header, status, Query, Path, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import cfg
import models
from user import User, AuthorizationException

app = FastAPI(
    title="SpotList API",
    description="Allows users to crate automated playlists based on rulesets",
    version="v0.0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.cors_urls,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Return an HTTP 401 code if login fails
@app.exception_handler(AuthorizationException)
async def authorization_exception_handler(request, exception: AuthorizationException):
    return JSONResponse('username or password incorrect', status.HTTP_401_UNAUTHORIZED)


# If Requests throws an error, return all the details w/ a HTTP 500
@app.exception_handler(requests.HTTPError)
async def http_exception_handler(request, exception: requests.HTTPError):
    logging.warning(exception)
    return JSONResponse(
        {'msg': 'encountered an error when communicating with the Spotify API',
         'details': {
            'code': exception.response.status_code,
            'text': exception.response.text,
            'url': exception.response.url
            }},
        status.HTTP_500_INTERNAL_SERVER_ERROR
    )


@app.get("/search", status_code=status.HTTP_200_OK, response_model=models.SearchResult, name="Search Spotify for a object")
async def search(
        user_id: Annotated[str, Header(title="User ID", description="User ID of the active user.")],
        token: Annotated[str, Header(description="Token of the active user.")],
        types: Annotated[list[models.SearchType], Query(description="List of item types to search across.")],
        query: Annotated[str, Query(description="Search query.")],
        limit: Annotated[int, Query(ge=0, le=50, description="The maximum number of results to return.")] = 20,
        offset: Annotated[int, Query(ge=0, le=1000, description="The index of the first result to return. Use with `limit` to get the next page of search results.")] = 0
        ):
    user = User(user_id, token)
    request = user.get("/search", params={"type": types, "q": query, "limit": limit, "offset": offset})
    return models.SearchResult.from_raw(request)


@app.get("/playlists", status_code=status.HTTP_200_OK, name="get list of a user's playlists")
async def get_playlists(
        user_id: Annotated[str, Header(title="User ID", description="User ID of the active user.")],
        token: Annotated[str, Header(description="Token of the active user.")],
        limit: Annotated[int, Query(ge=0, le=50, description="The maximum number of results to return.")] = 20,
        offset: Annotated[int, Query(ge=0, le=1000, description="The index of the first result to return. Use with `limit` to get the next page of search results.")] = 0
        ):
    return User(user_id, token).get_playlists()


@app.post("/playlist", status_code=status.HTTP_200_OK, name="Create a new playlist")
async def create_playlist(
        user_id: Annotated[str, Header(title="User ID", description="User ID of the active user.")],
        token: Annotated[str, Header(description="Token of the active user.")]
        ):
    user = User(user_id, token)
    return HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@app.get("/playlist/{playlist_id}", status_code=status.HTTP_200_OK, name="get details of a playlist")
async def get_playlist_details(
        user_id: Annotated[str, Header(title="User ID", description="User ID of the active user.")],
        token: Annotated[str, Header(description="Token of the active user.")],
        playlist_id: Annotated[str, Path(description="ID of the playlist to fetch")]
        ):
    user = User(user_id, token)
    return HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@app.put("/playlist/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT, name="set details of a playlist")
async def set_playlist_details(
        user_id: Annotated[str, Header(title="User ID", description="User ID of the active user.")],
        token: Annotated[str, Header(description="Token of the active user.")],
        playlist_id: Annotated[str, Path(description="ID of the playlist to update")]
        ):
    user = User(user_id, token)
    return HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@app.get("/playlist/{playlist_id}/rules", status_code=status.HTTP_200_OK, name="get rules of a playlist")
async def get_playlist_rules(
        user_id: Annotated[str, Header(title="User ID", description="User ID of the active user.")],
        token: Annotated[str, Header(description="Token of the active user.")],
        playlist_id: Annotated[str, Path(description="ID of the playlist to fetch rules for")],
        limit: Annotated[int, Query(ge=0, le=50, description="The maximum number of results to return.")] = 20,
        offset: Annotated[int, Query(ge=0, le=1000, description="The index of the first result to return. Use with `limit` to get the next page of search results.")] = 0
        ):
    user = User(user_id, token)
    return HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@app.put("/playlist/{playlist_id}/rules", status_code=status.HTTP_204_NO_CONTENT, name="set rules of a playlist")
async def set_playlist_rules(
        user_id: Annotated[str, Header(title="User ID", description="User ID of the active user.")],
        token: Annotated[str, Header(description="Token of the active user.")],
        playlist_id: Annotated[str, Path(description="ID of the playlist to set rules for")]
        ):
    user = User(user_id, token)
    return HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@app.put("/build/{playlist_id}", status_code=status.HTTP_201_CREATED, name="Compile a playlist and push to spotify")
async def build_playlist(
        user_id: Annotated[str, Header(title="User ID", description="User ID of the active user.")],
        token: Annotated[str, Header(description="Token of the active user.")],
        playlist_id: Annotated[str, Path(description="ID of the playlist to build")]
        ):
    user = User(user_id, token)
    return HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@app.get("/auth", status_code=status.HTTP_303_SEE_OTHER, name="Get a Spotify authorization URL to create a user")
async def get_auth_link():
    # Use our credentials to get the authorization url from Spotify
    parameters = {"response_type": "code", "client_id": cfg.client_id,
                  "redirect_uri": f"{cfg.redirect_uri}",
                  "scope": "playlist-read-private playlist-modify-private playlist-modify-public",
                  # 'state' will be passed back to us after the user logs in, allowing us to identify what client
                  # the user belongs to. The user will use this to authenticate to SpotList as well.
                  "state": uuid.uuid4().hex,
                  "show_dialog": "true"}
    response = requests.get(f"https://accounts.spotify.com/authorize", params=parameters)
    logging.info(f"got {response.status_code} from POST {response.url}")
    response.raise_for_status()
    # Send the URL back to the user. All further requests from the user will need the token.
    return response.url


# Once the user has authenticated with Spotify, they will be redirected here with their authorization code.
@app.get("/exchange", status_code=status.HTTP_200_OK, response_model=models.Auth, name="get login info for spotlist")
async def get_token(
        code: Annotated[str, Query(description="Code received from Spotify to exchange for authorization token.")],
        state: Annotated[str, Query(description="String received from Spotify identifying the user to SpotList")]
        ):
    # Exchange the temporary authorization code for (semi-)permanent authorization credentials
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": cfg.auth_header}
    parameters = {"grant_type": "authorization_code",
                  "code": code,
                  "redirect_uri": f"{cfg.redirect_uri}"}
    response = requests.post(f"{cfg.auth_url}/api/token", params=parameters, headers=headers)
    logging.info(f"got {response.status_code} from POST {response.url}")
    response.raise_for_status()
    user_auth = response.json()

    # Call the /me endpoint to get the user's spotify ID to use as the primary key for the database
    headers = {'Authorization': f'Bearer {user_auth["access_token"]}', 'Content-Type': 'application/json'}
    response = requests.get(f'{cfg.api_url}/v1/me', headers=headers)
    logging.info(f"got {response.status_code} from GET {response.url}")
    response.raise_for_status()
    user_data = response.json()

    cfg.db.execute(f"""
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
        """)

    cfg.db.commit()

    return models.Auth(user_id=user_data['id'], token=state, display_name=user_data['display_name'])
