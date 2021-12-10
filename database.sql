CREATE DATABASE beanbefore;

USE beanbefore

CREATE TABLE users (
    userid int,
    username varchar(255),
	email varchar(255),
    hash varchar(255),
	salt varchar(255)
);
ALTER TABLE `users` ADD UNIQUE(`userid`);
ALTER TABLE `users` ADD PRIMARY KEY(`userid`);

CREATE TABLE auth_tokens (
    userid int,
	expiration varchar(255),
    token varchar(255)
);
ALTER TABLE `auth_tokens` ADD PRIMARY KEY(`token`);

CREATE TABLE posts (
    postid int,
	authorid int,
	time varchar(255),
    heading varchar(255),
	caption varchar(255),
	media varchar(255)
);
ALTER TABLE `posts` ADD PRIMARY KEY(`postid`);


