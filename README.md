#
# Intelligent Music Recommender
A conversational music retrieval search engine.

## Prerequisites
Before you can run the alpha version of our app or the tests, you must:
* [Install SQLite 3](https://www.sqlite.org/download.html)
* Install Python 3.5
* Install the project dependencies: `pip install -r requirements.txt`

For a detailed description of setup for development purposes, please
see the [wiki page](https://github.com/MIR-Directed-Research/intelligent-music-recommender/wiki/Contributing.).

## Running the Alpha App
First, follow the instructions in the prerequisites section. Then, from the project root, run `python view/cli.py`, which will open a simple command line interface that behaves like a primitive conversational agent. It demonstrates the basic functionality that we've implemented so far, which includes:
* Parsing and interpreting natural language input from a user
* Collecting answers to user requests from our database via API calls to our Knowledge Representation system
* Fulfilling a user's request by providing answers or taking some action (e.g. "playing" a song)

For example:
```
$ python view/cli.py
Initializing app...
Running app...
Welcome!

Hello
Response: Hi there! Ask me to play artists or songs. I can also find songs that are similar to other artists.

Play Ariana Grande
Playing: ['Ariana Grande']

Play Mozart
Response: I'm sorry, I couldn't find that for you.

What are some songs by Ariana Grande?
Response: ['Santa Baby', 'Santa Tell Me', 'thank u, next']

What are some songs by Ariana Grande and Justin Bieber?
Response: ['Santa Baby', 'Santa Tell Me', 'thank u, next', 'Friends (with BloodPop®)', 'No Brainer']

Who is the artist of the song thank u, next?
Response: ['Ariana Grande']

What are some artists similar to Ariana Grande?
Response: ['Halsey', 'DNCE', 'Selena Gomez', 'Alessia Cara', 'ZAYN', 'Rita Ora', 'Zara Larsson', 'Dua Lipa', 'Demi Lovato', 'Tinashe', 'Taylor Swift', 'Miley Cyrus', 'Troye Sivan', 'Camila Cabello', 'Julia Michaels', 'Little Mix', 'Hailee Steinfeld', 'Madison Beer', 'Carly Rae Jepsen', 'Fifth Harmony']

Play artists like Justin Bieber
Playing: ['DNCE', 'Selena Gomez', 'Alessia Cara', 'ZAYN', 'Zara Larsson', 'Demi Lovato', 'Taylor Swift', 'Miley Cyrus', 'Camila Cabello', 'Madison Beer', 'Fifth Harmony', 'Shawn Mendes', 'Niall Horan', 'Liam Payne', 'One Direction', 'Austin Mahone', 'Selena Gomez & The Scene', 'Nick Jonas', 'Jonas Brothers', 'Cody Simpson']
```

More information about configuring the CLI can be found in the [wiki](https://github.com/MIR-Directed-Research/intelligent-music-recommender/wiki/Contributing).

## Running The Tests
First, follow the instructions in the prerequisites section. From the project root directory: `python run_tests.py`.

## Contributing
Please [see wiki](https://github.com/MIR-Directed-Research/intelligent-music-recommender/wiki/Contributing) for info on:
* [git branching workflow](https://github.com/MIR-Directed-Research/intelligent-music-recommender/wiki/Contributing#git-workflow)
* [virtual environments](https://github.com/MIR-Directed-Research/intelligent-music-recommender/wiki/Contributing#virtualenv)
