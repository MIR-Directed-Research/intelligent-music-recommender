import requests
from base64 import b64encode
import sys

class SpotifyClient():

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

        return body["access_token"]

    def set_token_in_auth_header(self, headers):
        if "Authorization" in headers:
            print("WARN: Overwriting existing 'Authorization' header: {}".format(headers.get("Authorization")))

        headers["Authorization"] = "Bearer {}".format(self.token)
        return headers

    def get_artist_id(self, artist):
        """Retrieves the Spotify ID of specified artist.

        Params:
            artist (string): e.g. "Justin Bieber"

        Returns:
            (string): Spotify's artist ID; None if search failed or rendered no results.
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
            print("ERROR: Request for finding '{}' failed. Received HTTP code:{}".format(artist, resp.status_code))
            print(body)
            return None

        num_hits = len(body["artists"]["items"])
        if num_hits == 0:
            print("Could not find info for artist '{}'".format(artist))
            return None

        print("Returning top match out of total {}.".format(num_hits))
        return body["artists"]["items"][0]["id"]


def get_artist_IDs(spotify, f):
    artist_by_id = dict()
    for line in f:
        tmp_artist_name = line.strip()
        tmp_ID = spotify.get_artist_id(tmp_artist_name)
        if tmp_ID is not None:
            print("Found ID for:", tmp_artist_name, ":", tmp_ID)
            artist_by_id[tmp_artist_name] = tmp_ID
    return artist_by_id


def main():
    print("Enter Spotify client ID:")
    client_id = sys.stdin.readline().split(" ")[-1].strip("\n")
    print("Enter Spotify secret key:")
    secret_key = sys.stdin.readline().split(" ")[-1].strip("\n")

    print("Enter names of artists, separated by new-lines:")
    spotify = SpotifyClient(client_id, secret_key)
    print(get_artist_IDs(spotify, sys.stdin))

if __name__ == "__main__":
    main()