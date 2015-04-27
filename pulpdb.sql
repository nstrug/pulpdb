CREATE USER pulpdb WITH PASSWORD 'pulpdb';

CREATE DATABASE pulpdb;

GRANT ALL PRIVILEGES ON DATABASE pulpdb to pulpdb;

CREATE TABLE rpms (
    rpm_id      SERIAL PRIMARY KEY,
    name        char(100) NOT NULL,
    bigname     char(310) UNIQUE NOT NULL,
    ver         char(100) NOT NULL,
    rel         char(100) NOT NULL,
    arch        char(10) NOT NULL,
    path        char(400) NOT NULL,
    UNIQUE (name, ver, rel, arch)
);

CREATE TABLE repos (
    repo_id     SERIAL PRIMARY KEY,
    name        char(200) UNIQUE NOT NULL,
    repoid      char(100) UNIQUE NOT NULL
);

CREATE TABLE rpms_repos (
    rpm_id      integer NOT NULL REFERENCES rpms,
    repo_id     integer NOT NULL REFERENCES repos
);

CREATE TABLE cvs (
    cv_id       SERIAL PRIMARY KEY,
    name        char(100) NOT NULL,
    latest_ver  integer
);

CREATE TABLE cvvers (
    cvver_id    SERIAL PRIMARY KEY,
    cv_id       integer NOT NULL REFERENCES cvs,
    ver         integer NOT NULL
);   

CREATE TABLE repo_mvs (
    mat_view    char(100) PRIMARY KEY,
    cvver_id    integer NOT NULL REFERENCES cvvers
);

CREATE TABLE cvs_repos (
    cv_id       integer NOT NULL REFERENCES cvs,
    repo_id     integer NOT NULL REFERENCES repos
);


    
    

