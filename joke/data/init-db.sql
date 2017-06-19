CREATE TABLE
IF NOT EXISTS joke (
    id              real    PRIMARY KEY,
    title           text    NOT NULL,
    content         text,
    jpg             text,
    gif             text,
    origin_id       text,
    origin          text,
    origin_name     text,
    origin_uri      text,
    author_id       real,
    joke_topic      text,
    comment_count   integer,
    create_date     text,
    is_delete       integer
);

CREATE TABLE
IF NOT EXISTS author (
    id          real    PRIMARY KEY,
    name        text    NOT NULL,
    avatar      text,
    origin_id   text,
    joke_count  integer,
    user_id     real,
    is_delete   integer
);

CREATE TABLE
IF NOT EXISTS comment (
    id          real    PRIMARY KEY,
    content     text,
    author_id   real,
    create_date text,
    is_delete   integer
);

CREATE TABLE
IF NOT EXISTS tag (
    id          real    PRIMARY KEY,
    name        text    NOT NULL,
    create_date text,
    is_delete   integer
);

CREATE TABLE
IF NOT EXISTS joke_tag (
    id          real    PRIMARY KEY,
    joke_id     real    NOT NULL,
    tag_id      real    NOT NULL,
    create_date text,
    is_delete   integer
);
