-- Active: 1712661125702@@127.0.0.1@3306@digital_human_app_data
use digital_human_app_data;

create table preset_characters (
    name VARCHAR(16), description VARCHAR(64)
);

create table preset_avatars (
    name VARCHAR(16), img_src VARCHAR(32)
);

insert into
    preset_characters (name, description)
values ('旅游信息向导', '可以和他交流一些旅游信息哦'),
    ('职业陪聊', '有什么事情要分享? 可以找TA哦'),
    ('影评家', '可以和他聊聊对电影行业的看法'),
    ('金融', '对理财有疑问? 可以问问他金融相关的信息');

insert into
    preset_avatars (name, img_src)
values ('avatar1', '/models/avatar1.png'),
    ('avatar2', '/models/avatar2.png'),
    ('avatar3', '/models/avatar3.png'),
    ('avatar4', '/models/avatar4.png');

insert into
    characters (
        cha_uid, avatar_type, lang_style_type, cha_name, user_uid, audio_refer_text
    )
values (
        "preset-avatar-1", "avatar1", "职业陪聊", "预设角色1", "all", "你说得对,但是原神是由米哈游开发的一款全新开放世界冒险游戏。"
    ),
    (
        "preset-avatar-2", "avatar2", "职业陪聊", "预设角色2", "all", "你说得对,但是原神是由米哈游开发的一款全新开放世界冒险游戏。"
    ),
    (
        "preset-avatar-3", "avatar3", "职业陪聊", "预设角色3", "all", "你说得对,但是原神是由米哈游开发的一款全新开放世界冒险游戏。"
    ),
    (
        "preset-avatar-4", "avatar4", "职业陪聊", "预设角色4", "all", "你说得对,但是原神是由米哈游开发的一款全新开放世界冒险游戏。"
    );