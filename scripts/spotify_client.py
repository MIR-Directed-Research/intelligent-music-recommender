import requests
from base64 import b64encode
from sys import argv

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

    def search_artist(self, artist):
        """Retrieves data summary of specified artist.

        Params:
            artist (string): e.g. "Justin Bieber"

        Returns:
            (dict): data summary; None if search failed or rendered no results.
                e.g. {
                    "genres": ['canadian pop', 'dance pop', 'pop', 'post-teen pop']
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
            print("ERROR: Request for finding '{}' failed. Received HTTP code:{}".format(artist, resp.status_code))
            print(body)
            return None

        num_hits = len(body["artists"]["items"])
        if num_hits == 0:
            print("Could not find info for artist '{}'".format(artist))
            return None

        print("Returning top match out of total {}.".format(num_hits))
        return dict(
            genres=body["artists"]["items"][0]["genres"]
        )


def main():
    if len(argv) < 2:
        print("Usage: python my_spotify_client.py path_to_file_containing_spotify_creds")
        sys.exit(1)

    # Input file is assumed to contain at least two lines
    # 1st line ends with the client id
    # 2nd line ends with the secret key
    with open(argv[1], "r", encoding="utf-8") as f:
        client_id = f.readline().split(" ")[-1].strip("\n")
        secret_key = f.readline().split(" ")[-1].strip("\n")

    spotify = SpotifyClient(client_id, secret_key)
    print(spotify.search_artist("Justin Bieber"))


if __name__ == "__main__":
    main()