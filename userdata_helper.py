import uuid;
from flask_mysqldb import MySQL;

import os;

# 用户数据管理相关

# 路径常量。指定用户数据保存的根目录
PATH = './ugc';

# 生成一个用户的唯一uuid。在用户注册时调用
def get_user_uuid():
    return uuid.uuid4();

# 生成一个自定义角色的唯一uuid。在创建自定义角色时调用
def get_character_uuid():
    return uuid.uuid4();

# 注册新用户。已弃用
def register_account(mySql: MySQL):
    pass;

# 获取路径常量
def get_store_path():
    return PATH;

# 当用户创建一个新的数字人时调用, 用于生成属于该数字人的文件夹, 提供目标数字人的uuid
def initialize_character_folder(uuid: uuid.UUID):
    uuid_dir = uuid.__str__();
    path = os.path.join(PATH, uuid_dir);
    if not os.path.exists(path):
        os.makedirs(path);
    return path;

# 删除自定义数字人时调用, 提供目标数字人的uuid。
def delete_character(uuid: str):
    path_folder = os.path.join(PATH, uuid);
    path = os.path.join(PATH, uuid, 'refer.wav');

    try:
        if os.path.exists(path):
            os.remove(path);
            os.rmdir(path_folder);
            return True;
        else:
            return False;
    except FileNotFoundError:
        return False;

# 处理用户登录请求
def auth(mysql, email):
    cursor = mysql.connection.cursor();
    auth_sql = "select uname from users where email='"+email+"';";
    result = cursor.execute(auth_sql);

    if result:
        return True;
    else:
        return False;