create table if not exists Users (
    id integer primary key,
    tg_internal_id integer,
    username text not null
);

create table if not exists Admins (
    id integer primary key,
    user_id integer,
    foreign key(user_id) references Users(id)
);

create table if not exists Contexts (
    id integer primary key,
    user_id integer,
    name text,
    foreign key(user_id) references Users(id)
);

create table if not exists ContextMessages (
    id integer primary key,
    context_id integer,
    role text not null,
    content text not null,
    foreign key(context_id) references Contexts(id)
);

create table if not exists StandaloneMessages (
    id integer primary key,
    user_id integer,
    content text not null,
    foreign key(user_id) references Users(id)
);

create unique index if not exists users_tg_internal_id_index
on Users(tg_internal_id);

create unique index if not exists users_username_index
on Users(username);
