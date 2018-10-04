CREATE TABLE artists(
    name varchar(40) primary key
);

CREATE TABLE songs(
    name varchar(40) primary key,
    mainArtist varchar(40) references artists(name)
);

/* insert dummy values */
INSERT INTO artists VALUES ("Justin Bieber");
INSERT INTO artists VALUES ("U2");

INSERT INTO songs VALUES ("Despacito", "Justin Bieber");
INSERT INTO songs VALUES ("Beautiful Day", "U2");