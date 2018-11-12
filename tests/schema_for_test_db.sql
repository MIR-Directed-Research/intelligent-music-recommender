-- This schema is used to setup a Database to run the tests.
-- It represents a semantic network: a labeled, directed graph

CREATE TABLE nodes(
    -- e.g. "Despacito", "Justin Bieber", "Pop", etc.
    name varchar(50),

    -- e.g. "song", "artist", "genre", etc.
    type varchar(50),

    -- NOTE: this field is an alias for SQLite's "row_id" column
    -- Setting this column to NULL at insert, will automatically populate it
    id INTEGER PRIMARY KEY
);

CREATE TABLE relations(
    -- e.g. "similar to"
    type varchar(40) PRIMARY KEY,
    -- e.g. false for "similar to" relations, but true for
    is_directed boolean
);

-- TODO: add constraints about node type (probably in a trigger function)
CREATE TABLE edges(
    source int REFERENCES nodes(id),
    dest int REFERENCES nodes(id),
    rel varchar(40) REFERENCES relations(type),
    score real CHECK (score >= 0 AND score <= 100),
    PRIMARY KEY (source, dest, rel)
);

-- TODO: Create trigger functions to add to nodes + edges table
CREATE TABLE artists(
    node_id int PRIMARY KEY REFERENCES nodes(id)
);

-- TODO: Create trigger functions to add to nodes + edges table
CREATE TABLE songs(
    main_artist_id int REFERENCES artists(node_id),
    node_id int REFERENCES nodes(id)
);

-- insert dummy values
INSERT INTO nodes VALUES ("Justin Bieber", "artist", 1);
INSERT INTO nodes VALUES ("Justin Timberlake", "artist", 2);
INSERT INTO nodes VALUES ("U2", "artist", 3);
INSERT INTO nodes VALUES ("Shawn Mendes", "artist", 4);

INSERT INTO artists VALUES (1);
INSERT INTO artists VALUES (2);
INSERT INTO artists VALUES (3);
INSERT INTO artists VALUES (4);

INSERT INTO nodes VALUES ("Despacito", "song", 10);
INSERT INTO nodes VALUES ("Rock Your Body", "song", 11);
INSERT INTO nodes VALUES ("Beautiful Day", "song", 12);
INSERT INTO nodes VALUES ("In My Blood", "song", 13);

INSERT INTO songs VALUES (1, 10);
INSERT INTO songs VALUES (2, 11);
INSERT INTO songs VALUES (3, 12);
INSERT INTO songs VALUES (4, 13);

-- * Define some edges+relations for testing
-- -------------------------------
INSERT INTO relations VALUES ("similar to", false);
-- Justin Bieber is similar to Justin Timberlake and Shawn Mendes
INSERT INTO edges VALUES (1, 2, "similar to", 75);
INSERT INTO edges VALUES (1, 4, "similar to", 100);

-- "Despacito" is similar to "Rock Your Body"
INSERT INTO edges VALUES (10, 11, "similar to", 100);

INSERT INTO relations VALUES ("other relation", false);
-- Justin Bieber and U2 are related in some unimportant way
INSERT INTO edges VALUES (1, 3, "other relation", 50);
-- "Despacito" and "Beautiful Day" are related in some unimportant way
INSERT INTO edges VALUES (10, 12, "other relation", 50);
