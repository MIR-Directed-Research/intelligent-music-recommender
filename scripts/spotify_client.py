import requests
from base64 import b64encode
import pprint
import sys

class SpotifyClient():
    """A simple object for interacting with Spotify's public web API.

    Prequisities:
        - Spotify client ID and secret key
            - Necessary for obtaining a Bearer token for authorization
            - Can be obtained from Spotify simply by registering your app.

    This object does not support getting Spotify user-specific info, which requires a
    separate and distinct auth scheme.

    This client class strives to print helpful error messages when problems occur.
    This is why square bracket notation is used -- instead of .get() -- for accessing fields
    in Spotify's API objects: if the fields are not found, the error message should be quite clear.
    """

    def __init__(self, client_id, secret_key):
        self.client_id = client_id
        self.secret_key = secret_key
        self.api_base = "https://api.spotify.com"

    @property
    def token(self):
        encoded_auth_header = b64encode((self.client_id + ":" + self.secret_key).encode("UTF-8")).decode()
        post_headers = dict(Authorization="Basic {}".format(encoded_auth_header))
        post_body = dict(grant_type="client_credentials")
        resp = requests.post(
            "https://accounts.spotify.com/api/token",
            data=post_body,
            headers=post_headers,
        )
        if resp.status_code != 200:
            raise Exception("ERROR: failed to refresh token. HTTP status={}".format(resp.status_code))

        try:
            body = resp.json()
        except Exception as e:
            print("ERROR: Could not parse response body to request for token.")
            raise e

        token = body.get("access_token")
        if token is None:
            raise Exception("ERROR: Token not found in resp body: ", body)
        return token

    def set_token_in_auth_header(self, headers):
        """Adds 'Authorization' field to given headers object and returns it.

        Params:
            headers (dict): HTTP headers.

        Returns:
            headers (dict): HTTP headers, with the 'Authorization' header newly set.
        """
        if "Authorization" in headers:
            print("WARN: Overwriting existing 'Authorization' header: {}".format(headers.get("Authorization")))

        try:
            headers["Authorization"] = "Bearer {}".format(self.token)

        except Exception as e:
            print("ERROR: Failed to set header because token could not be retrieved")
            raise e

        return headers

    def get_related_artists(self, artist_ID):
        """Retrieves metadata of artists related to the specified artist.

        Specifically, metadata includes (1) name, (2) genres, and (3) number of followers of
        each related artist.

        Params:
            artist_ID (string): Spotify ID for relevant artist. e.g. "51Blml2LZPmy7TTiAg47vQ"

        Returns:
            related_artists (dict): key is ID of related artists, val is their metadata packaged in a dict.
                None if an error occurs.
        """
        headers = self.set_token_in_auth_header(dict())
        resp = requests.get(
            self.api_base + "/v1/artists/{}/related-artists".format(artist_ID),
            headers=headers,
        )

        try:
            body = resp.json()
        except Exception as e:
            print("ERROR: Could not parse response body for related artists request for artists with ID ", artist_ID)
            return None

        if resp.status_code != 200:
            print("ERROR: Request for finding related artists of artist with ID '{}' failed. Received HTTP code:{}".format(artist_ID, resp.status_code))
            print(body)
            return None

        related_artists = dict()
        for hit in body["artists"]:
            related_artists[hit["name"]] = dict(
                ID=hit["id"],
                genres=hit["genres"],
                num_followers=int(hit["followers"]["total"]),
            )
        return related_artists

    def get_artist_data(self, artist):
        """Retrieves summary data regarding specified artist.

        Naively resolves artist ambiguity by taking first result.

        Params:
            artist (string): e.g. "Justin Bieber"

        Returns:
            (dict): keys: id, num_followers, genres. None if search failed or rendered no results.
                e.g. {
                    id=1uNFoZAHBGtllmzznpCI3s,
                    num_followers=25683438,
                    genres=["canadian pop", "dance pop", "pop", "post-teen pop"]
                }
        """
        params = dict(q=artist, type="artist")
        headers = self.set_token_in_auth_header(dict())
        resp = requests.get(
            self.api_base + "/v1/search",
            params=params,
            headers=headers,
        )

        try:
            body = resp.json()
        except Exception as e:
            print("ERROR: Could not parse response body of search request for artist: ", artist)
            raise e

        if resp.status_code != 200:
            print("ERROR: Search request for artist '{}' failed. Received HTTP code:{}".format(artist, resp.status_code))
            print(body)
            return None

        num_hits = len(body["artists"]["items"])
        if num_hits == 0:
            print("Could not find info for artist '{}'".format(artist))
            return None

        return dict(
            id=body["artists"]["items"][0]["id"],
            num_followers=body["artists"]["items"][0]["followers"]["total"],
            genres=body["artists"]["items"][0]["genres"],
        )

    def get_top_songs(self, artist_ID, country_iso_code):
        """Retrieves metadata of the specified artist's top songs on Spotify.

        Params:
            artist_ID (string):

        Returns:
            top_songs (dict): key is song name, val is its metadata packaged in a dict. None if an error occurs.
        """
        headers = self.set_token_in_auth_header(dict())
        params = dict(country=country_iso_code)
        resp = requests.get(
            self.api_base + "/v1/artists/{}/top-tracks".format(artist_ID),
            headers=headers,
            params=params,
        )

        try:
            body = resp.json()
        except Exception as e:
            print("ERROR: Could not parse response body of top songs request for artist with ID: ", artist_ID)
            return None

        if resp.status_code != 200:
            print("ERROR: Request for finding top songs of '{}' failed. Received HTTP code:{}".format(artist_ID, resp.status_code))
            print(body)
            return None

        top_songs = dict()
        for track in body["tracks"]:
            # ignore entire albums for now
            if track["album"]["album_type"] == "album":
                continue

            top_songs[track["name"]] = dict(
                duration_ms=int(track["duration_ms"]),
                id=track["id"],
                popularity=int(track["popularity"]),
                uri=track["uri"],
            )
        return top_songs

