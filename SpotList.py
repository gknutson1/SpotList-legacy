import json
import logging
import time
import uuid
from typing import Annotated

import requests
from fastapi import FastAPI, HTTPException, Header, status, Query, Path, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import Field

import cfg
import models
import rules
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


# @app.post("/temp/from_artist", status_code=status.HTTP_201_CREATED, name="Create a playlist of an artist's songs")
# async def temp_create_artist_playlist(
#         user_id: Annotated[str, Header(title="User ID", description="User ID of the active user.")],
#         token: Annotated[str, Header(description="Token of the active user.")],
#         artist_id: Annotated[str, Query(description="Spotify ID of the artist to use to create the playlist")],
#         name: Annotated[str, Body(description="The name for the new playlist. Does *not* need to be unique.")],
#         public: Annotated[bool, Body(description="Determines if the playlist is public or private. Defaults to private.")] = False,
#         description: Annotated[str, Body(description="Description of the playlist, as seen in Spotify.")] = None
#         ):
#     user = User(user_id, token)
#
#     albums: list[str] = []
#     request = user.get(f"/artists/{artist_id}/albums", {"limit": 50})
#
#     while True:
#         albums += (i["id"] for i in request["items"])
#         if not request["next"]: break
#         request = user.get(request["next"], raw_url=True)
#
#     songs: list[str] = []
#
#     # Spotify's /albums endpoint only supports getting details for 20 albums at a time, so we need to split the list of
#     # albums into chunks of 20 and do an API call for each chunk
#     for offset in range(0, len(albums), 20):
#         # the ids parameter requires comma seperated ids, so we need to run the list through .join
#         request = user.get("/albums", {"ids": ",".join(albums[offset:offset+20])})
#         for album in request['albums']:
#             tracks = album['tracks']
#             while True:
#                 # If an artist guest stars on one track on an album, every song on the album will be gathered by
#                 # /albums, so we need to check every track to make sure that the target artist preformed on the track.
#                 songs += (i['uri'] for i in tracks['items'] if any(artist_id == j['id'] for j in i['artists']))
#                 if not tracks["next"]: break
#                 tracks = user.get(tracks["next"], raw_url=True)
#
#     body = {"name": name, "public": public, "description": description}
#     request = user.post(f"/users/{user.spotify_id}/playlists", body=body)
#
#     playlist_id = request['id']
#     playlist_url = request['external_urls']['spotify']
#
#     # Similar to /albums, /playlists/.*/tracks accepts at most 100 tracks, requiring us to chunk our tracklist.
#     for offset in range(0, len(songs), 100):
#         user.post(f"/playlists/{playlist_id}/tracks", body={"uris": songs[offset:offset+100]})
#
#     return playlist_url


@app.get("/playlists", status_code=status.HTTP_200_OK, name="get list of a user's playlists", response_model=list[models.Playlist])
async def get_playlists(
        user_id: Annotated[str, Header(title="User ID", description="User ID of the active user.")],
        token: Annotated[str, Header(description="Token of the active user.")],
        limit: Annotated[int, Query(ge=0, le=50, description="The maximum number of results to return.")] = 20,
        offset: Annotated[int, Query(ge=0, le=1000, description="The index of the first result to return. Use with `limit` to get the next page of search results.")] = 0
        ):
    return User(user_id, token).get_playlists()


@app.get("/rules", status_code=status.HTTP_200_OK, name="get a list of the currenly available rules", response_model=list[rules.RuleDescription])
async def get_rules():
        return (i.describe() for i in [rules.AfterDate, rules.Album, rules.Artist, rules.BeforeDate, rules.Genre, rules.LessPopular, rules.MorePopular])


@app.post("/playlist", status_code=status.HTTP_200_OK, name="Create a new playlist", response_model=models.PlaylistCreationData)
async def create_playlist(
        user_id: Annotated[str, Header(title="User ID", description="User ID of the active user.")],
        token: Annotated[str, Header(description="Token of the active user.")],
        name: Annotated[str, Body(description="The name for the new playlist. Does *not* need to be unique.")],
        public: Annotated[bool, Body(description="Determines if the playlist is public or private. Defaults to private.")] = False,
        description: Annotated[str, Body(description="Description of the playlist, as seen in Spotify.")] = None
        ):
    user = User(user_id, token)

    body = {"name": name, "public": public, "description": description}
    request = user.post(f"/users/{user.spotify_id}/playlists", body=body)

    playlist_id = request['id']
    playlist_url = request['external_urls']['spotify']

    cfg.db.execute(f"""
        insert into playlists
            (playlist_id, name, description, created, owner)
        values ('{playlist_id}', '{name}', '{description}', '{time.time()}', '{user_id}')
    """)

    cfg.db.commit()

    return models.PlaylistCreationData(playlist_id=playlist_id, url=playlist_url)


@app.get("/playlist/{playlist_id}", status_code=status.HTTP_200_OK, name="get details of a playlist", response_model=models.Playlist)
async def get_playlist_details(
        user_id: Annotated[str, Header(title="User ID", description="User ID of the active user.")],
        token: Annotated[str, Header(description="Token of the active user.")],
        playlist_id: Annotated[str, Path(description="ID of the playlist to fetch")]
        ):
    user = User(user_id, token)
    playlist = user.get_playlist(playlist_id)
    return playlist if playlist else HTTPException(status.HTTP_404_NOT_FOUND)


@app.put("/playlist/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT, name="set details of a playlist")
async def set_playlist_details(
        user_id: Annotated[str, Header(title="User ID", description="User ID of the active user.")],
        token: Annotated[str, Header(description="Token of the active user.")],
        playlist_id: Annotated[str, Path(description="ID of the playlist to update")],
        name: Annotated[str, Body(description="The name for the new playlist. Does *not* need to be unique.")],
        public: Annotated[bool, Body(description="Determines if the playlist is public or private. Defaults to private.")] = False,
        description: Annotated[str, Body(description="Description of the playlist, as seen in Spotify.")] = None
        ):
    user = User(user_id, token)
    playlist = user.get_playlist(playlist_id)
    if not playlist:
        return HTTPException(status.HTTP_404_NOT_FOUND)

    user.put(f"playlists/{playlist_id}", body={"name": name, "public": public, "description": description})
    return


@app.get("/playlist/{playlist_id}/rules", status_code=status.HTTP_200_OK, name="get rules of a playlist", response_model=list[rules.RuleDescription])
async def get_playlist_rules(
        user_id: Annotated[str, Header(title="User ID", description="User ID of the active user.")],
        token: Annotated[str, Header(description="Token of the active user.")],
        playlist_id: Annotated[str, Path(description="ID of the playlist to fetch rules for")]
        ):
    user = User(user_id, token)
    playlist = user.get_playlist_rules(playlist_id)
    return playlist if playlist else HTTPException(status.HTTP_404_NOT_FOUND)


@app.put("/playlist/{playlist_id}/rules", status_code=status.HTTP_204_NO_CONTENT, name="set rules of a playlist")
async def set_playlist_rules(
        user_id: Annotated[str, Header(title="User ID", description="User ID of the active user.")],
        token: Annotated[str, Header(description="Token of the active user.")],
        playlist_id: Annotated[str, Path(description="ID of the playlist to set rules for")],
        rule_list: Annotated[list[rules.RuleData], Body(description="List of rules to apply")],
        ):
    user = User(user_id, token)
    query = cfg.db.execute(f"SELECT EXISTS(SELECT true FROM playlists WHERE playlist_id = '{playlist_id}' AND owner = '{user_id}')")
    if not query.fetchone()[0]:
        return HTTPException(status.HTTP_404_NOT_FOUND)

    print([i.json() for i in rule_list])

    cfg.db.execute(f"UPDATE playlists SET rules = '{json.dumps([i.json() for i in rule_list])}' WHERE playlist_id = '{playlist_id}' AND owner = '{user_id}'")
    cfg.db.commit()
    return


@app.put("/build/{playlist_id}", status_code=status.HTTP_201_CREATED, name="Compile a playlist and push to spotify")
async def build_playlist(
        user_id: Annotated[str, Header(title="User ID", description="User ID of the active user.")],
        token: Annotated[str, Header(description="Token of the active user.")],
        playlist_id: Annotated[str, Path(description="ID of the playlist to build")]
        ):
    user = User(user_id, token)
    rule_list = user.get_playlist_rules(playlist_id)
    tracks: list[models.track] = []
    for i in rule_list:
        rule_type = rules.RuleType[i.type]

        match rule_type:
            case rules.RuleType.Artist: rule = rules.Artist
            case rules.RuleType.Album: rule = rules.Album
            case rules.RuleType.Genre: rule = rules.Genre
            case rules.RuleType.MorePopular: rule = rules.MorePopular
            case rules.RuleType.LessPopular: rule = rules.LessPopular
            case rules.RuleType.BeforeDate: rule = rules.BeforeDate
            case rules.RuleType.AfterDate: rule = rules.AfterDate
        if i.is_add:
            rule.add_tracks(user, tracks, i.data)
        else:
            rule.remove_tracks(user, tracks, i.data)

    # user.put(f"/playlists/{playlist_id}/tracks", params={"uris": None})

    for offset in range(0, len(tracks), 100):
        user.post(f"/playlists/{playlist_id}/tracks", body={"uris": [f"spotify:track:{i['uri']}" for i in tracks[offset:offset + 100]]})
    return


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
