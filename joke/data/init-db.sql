CREATE TABLE
IF NOT EXISTS joke (
    id              integer PRIMARY KEY AUTOINCREMENT,
    title           text    NOT NULL,
    content         text,
    jpg             text,
    gif             text,
    origin_id       text,
    origin          text,
    origin_name     text,
    origin_uri      text,
    author_id       integer    NOT NULL,
    joke_topic      text,
    comment_count   integer,
    create_date     text    NOT NULL,
    is_delete       integer
);

CREATE TABLE
IF NOT EXISTS author (
    id          integer     PRIMARY KEY AUTOINCREMENT,
    name        text        NOT NULL,
    avatar      text,
    origin_id   text,
    joke_count  integer,
    user_id     integer     NOT NULL,
    is_delete   integer
);

CREATE TABLE
IF NOT EXISTS comment (
    id          integer     PRIMARY KEY AUTOINCREMENT,
    content     text        NOT NULL,
    author_id   integer     NOT NULL,
    create_date text        NOT NULL,
    is_delete   integer
);

CREATE TABLE
IF NOT EXISTS tag (
    id          integer     PRIMARY KEY AUTOINCREMENT,
    name        text        NOT NULL,
    create_date text        NOT NULL,
    is_delete   integer
);

CREATE TABLE
IF NOT EXISTS joke_tag (
    id          integer     PRIMARY KEY AUTOINCREMENT,
    joke_id     integer     NOT NULL,
    tag_id      integer     NOT NULL,
    create_date text        NOT NULL,
    is_delete   integer
);
