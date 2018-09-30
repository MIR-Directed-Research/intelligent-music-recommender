# 
# Intelligent Music Recommender
A conversational music retrieval search engine.

## Contributing
Please [see wiki](https://github.com/MIR-Directed-Research/intelligent-music-recommender/wiki/Contributing) for info on:
* git branching workflow
* virtual environments

## Set up
* [Download SQLite 3](https://www.sqlite.org/download.html) if not already installed


## Test Environment
### Database Setup
For the MVP phase of the project, we are using SQLite because it is a simple RDBMS.
```
# Create a new database called "test.db" for local testing
$ sqlite3 test.db < schema.sql
```
