CREATE DATABASE digital_human_app_data;

use digital_human_app_data;

create table users (
    id varchar(64),
    uname varchar(30), 
    pwd varchar(30), 
    email varchar(30)
);

INSERT INTO
    users (id, uname, pwd, email)
values ('000000-231ab-234','admin', 'admin123456', '10086@163.com');


create table characters(
    cha_uid varchar(64),
    avatar_type varchar(16),
    lang_style_type varchar(16),
    cha_name varchar(32),
    user_uid varchar(64),
    audio_refer_text varchar(128),
    PRIMARY KEY (cha_uid)
);