#
# Intelligent Music Recommender
A conversational music retrieval search engine.

## Prerequisites
Before you can run the alpha version of our app or the tests, you must:
* [Install SQLite 3](https://www.sqlite.org/download.html)
* Install Python 3.5
* Install the project dependencies: `pip install -r requirements.txt`

## Running the Alpha App
First, follow the instructions in the prerequisites section. Then, from the project root, run `python view/cli.py`, which will open a simple command line interface that behaves like a primitive conversational agent. It demonstrates the basic functionality that we've implemented so far, which includes:
* Parsing and interpreting natural language input from a user
* Collecting answers to user requests from our database via API calls to our Knowledge Representation system
* Fulfilling a user's request by providing answers or taking some action (e.g. "playing" a song)

For example:
```
$ python view/cli.py
Hello
Response: Hi there! Ask me to play artists or songs. I can also find songs that are similar to other artists.

Can you play Justin Bieber?
Playing: ['Justin Bieber']

Can you play U2?
Playing: ['U2']

Can you play Mozart?
Response: I'm sorry, I couldn't find that for you.

Can you play songs like Despacito?
Playing: ['Rock Your Body']

Can you play artists like Justin Bieber?
Playing: ['Justin Timberlake', 'Shawn Mendes']
```

## Test Environment
First, follow the instructions in the prerequisites section. From the project root directory: `python run_tests.py`.

## Contributing
Please [see wiki](https://github.com/MIR-Directed-Research/intelligent-music-recommender/wiki/Contributing) for info on:
* git branching workflow
* virtual environments
