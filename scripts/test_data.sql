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
INSERT INTO nodes VALUES ("Sorry", "song", 14);

INSERT INTO songs VALUES (1, 10);
INSERT INTO songs VALUES (1, 14);
INSERT INTO songs VALUES (2, 11);
INSERT INTO songs VALUES (3, 12);
INSERT INTO songs VALUES (4, 13);

-- * Define some edges for testing
-- -------------------------------
-- Justin Bieber is similar to Justin Timberlake and Shawn Mendes
INSERT INTO edges VALUES (1, 2, "similar to", 75);
INSERT INTO edges VALUES (1, 4, "similar to", 100);

-- "Despacito" is similar to "Rock Your Body"
INSERT INTO edges VALUES (10, 11, "similar to", 100);

-- Justin Bieber and U2 are related in some unimportant way
INSERT INTO edges VALUES (1, 3, "other relation", 50);
-- "Despacito" and "Beautiful Day" are related in some unimportant way
INSERT INTO edges VALUES (10, 12, "other relation", 50);