import base64
import sqlite3
from pathlib import Path

import yaml

# ID and Secret to communicate to Spotify's API with
client_id: str
client_secret: str

# Address you specified in the callback address in the Spotify dashboard. Using ports other than 443 is not recommended.
redirect_uri: int
db: sqlite3.Connection

# Base64 encoded client id and secret. Used to refresh a user's access token.
auth_header: str

# Spotify authorization url, for authenticating users
auth_url = "https://accounts.spotify.com"

# Spotify url, for making api calls
api_url = "https://api.spotify.com"


def __setup__(config_file: Path) -> None:
    """
    Do all the setup in a function to avoid populating the module with variables
    Do *NOT* call this outside of cfg/__init__.py
    :param config_file: file that holds the yaml-formatted configuration file
    """
    if not config_file.exists():
        raise FileNotFoundError(f'config file "{config_file}" not found')

    config_data: dict = yaml.safe_load(config_file.read_text())

    global client_id
    global client_secret
    global redirect_uri
    global db
    global auth_header

    # Load everything from the config file
    try:
        client_id_file = Path(*config_data['client_id_file'])
        client_secret_file = Path(*config_data['client_secret_file'])
        redirect_uri = config_data['redirect_uri']
        db_file = Path(*config_data['database_file'])
        create_db = config_data['create_database_if_missing']
    except KeyError as e:
        raise KeyError(f'Missing key "{e}" from config file "{config_file}"')

    if not client_id_file.exists():
        raise FileNotFoundError("Client ID file not found")

    if not client_secret_file.exists():
        raise FileNotFoundError("Client Secret file not found")

    client_id = client_id_file.read_text()
    client_secret = client_secret_file.read_text()

    # Encode the client ID and secret into a base64 string
    auth_header = f'Basic {base64.b64encode(f"{client_id}:{client_secret}".encode("ascii")).decode("ascii")}'

    # If create_db is `false`, we need to check if the database is correctly configured before continuing
    if not create_db:
        if not db_file.exists():
            raise FileNotFoundError(f'database file {db_file} does not exist and "create_database_if_missing" is false')

        db = sqlite3.connect(db_file)
        # Check if the tables exist in the database. We only check that tables with the correct names exist,
        # and don't bother to validate if the tables are configured correctly.
        for table in ['users', 'playlists', 'rules']:
            # If a table exists in the database, it will have an entry in the `sqlite_master` table.
            # We can SELECT our table name and check if the result is `None` to see if it does not exist
            reply = db.execute(f"select name from sqlite_master where type = 'table' and name = '{table}'")
            if not reply.fetchone():
                raise sqlite3.DatabaseError(f'table {table} does not exist and "create_database_if_missing" is false')

    # If create_db is `true`, we can just call the database creation commands,
    # as they do not override and will do noting if the database/tables already exists
    if create_db:
        db = sqlite3.connect(db_file)
        db.execute('''
            create table if not exists users(
                spotify_id    TEXT not null
                    constraint user_pk
                        primary key on conflict replace,
                access_token  TEXT not null,
                refresh_token TEXT not null,
                expires_at    INT  not null,
                app_password  TEXT not null
            );
    ''')

        db.execute('''
            create table if not exists playlists(
                playlist_id TEXT not null
                    constraint playlist_pk
                        primary key,
                last_built  INT,
                owner       TEXT not null
                    constraint user_fk
                        references users
            )    
    ''')

        db.execute('''
            create table if not exists rules(
                playlist   TEXT    not null
                    constraint playlist_fk
                        references playlists,
                rule_id    TEXT    not null,
                data_json  TEXT    not null,
                exec_order INTEGER not null
            );
        ''')
        db.commit()


__setup__(Path("cfg", "cfg.yml"))
