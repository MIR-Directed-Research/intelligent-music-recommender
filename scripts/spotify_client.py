import requests
from base64 import b64encode
from sys import argv

class SpotifyClient():

    def __init__(self, client_id, secret_key):
        self.client_id = client_id
        self.secret_key = secret_key

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
    print("Created Spotify with token: {}".format(spotify.token))

if __name__ == "__main__":
    main()