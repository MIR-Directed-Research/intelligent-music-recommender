-- This schema is used to setup a Database to run the tests.
-- It represents a semantic network: a labeled, directed graph

CREATE TABLE nodes(
    -- e.g. "Despacito", "Justin Bieber", "Pop", etc.
    name varchar(50) NOT NULL,

    -- e.g. "song", "artist", "genre", etc.
    type varchar(50) NOT NULL,

    -- NOTE: this field is an alias for SQLite's "row_id" column
    -- Setting this column to NULL at insert, will automatically populate it
    id INTEGER PRIMARY KEY
);

CREATE TABLE relations(
    -- e.g. "similar to"
    type        varchar(40) NOT NULL PRIMARY KEY,
    -- e.g. false for "similar to" relations, but true for
    is_directed boolean NOT NULL
);

-- TODO: add constraints about node type (probably in a trigger function)
CREATE TABLE edges(
    source  int NOT NULL REFERENCES nodes(id),
    dest    int NOT NULL REFERENCES nodes(id),
    rel     varchar(40) NOT NULL REFERENCES relations(type),
    score   real NOT NULL CHECK (score >= 0 AND score <= 100),
    PRIMARY KEY (source, dest, rel)
);

-- TODO: Create trigger functions to add to nodes + edges table
CREATE TABLE artists(
    node_id int PRIMARY KEY REFERENCES nodes(id) NOT NULL
);

-- TODO: Create trigger functions to add to nodes + edges table
CREATE TABLE songs(
    main_artist_id  int REFERENCES artists(node_id) NOT NULL,
    node_id         int REFERENCES nodes(id) NOT NULL
);

INSERT INTO relations (type, is_directed) VALUES ("similar to", false);