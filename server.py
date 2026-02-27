import os;
import flask;
from flask import Flask;
from flask import request;
from flask_cors import cross_origin;
from flask_mysqldb import MySQL;
from flask import jsonify;
from flask import Response;
from flask import stream_with_context;
import redis;
from datetime import datetime;

from werkzeug.utils import secure_filename;

import wave;

from app.pipeline import DEFAULT_REFER_AUDIO_PATH, DHPipeline;
from userdata_helper import auth, get_character_uuid, get_user_uuid, initialize_character_folder, delete_character, PATH;
from app.utils import chat_util;
import env;

app = Flask(__name__);
app.secret_key = 'taco-ice-cream';
app.debug = True;

app.config["MYSQL_USER"] = env.MYSQL_CONFIGS["MYSQL_USER"];
app.config["MYSQL_PASSWORD"] = env.MYSQL_CONFIGS["MYSQL_PASSWORD"];
app.config["MYSQL_DB"] = env.MYSQL_CONFIGS["MYSQL_DATABASE"];

# 初始化redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0);

mysql = MySQL(app);

pipeline = DHPipeline();

'''
以下为所有服务器api
'''

RESPONSE_CODE_ENUMS = {
    "SUCCESS": "请求成功",
    "INCORRECT_REQUEST_ARGS": "请求参数有误",
    "INCORRECT_REQUEST_METHOD": "请求方法有误",
    "REQUEST_TARGET_NOT_FOUND": "请求的目标资源未找到",
    "MISSING_FILE": "请求中缺少文件",
    "INCORRECT_FILE_CONTENT": "请求中的文件内容有误",
    "SERVER_ERROR": "服务器内部错误"
}

#获取一次数字人回复。数据包括回复的文字，情感参数
@app.route("/get_response", methods=['POST'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:4173'], methods=['POST'])
def get_digital_human_response():
    status = None;
    if request.method == 'POST':

        print(request);
        data = request.get_json();
        print(data);
    
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Prompt is required'}), 400

        prompt = data['prompt']
        response_data = pipeline.generate_response(prompt);

        status = "SUCCESS";
        response = app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status], "data": response_data});
        
        return response;
    else:
        status = "INCORRECT_REQUEST_METHOD";
        return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status]}); #TODO

# @deprecated 即将弃用
#获取一次流式补全。数据包括回复的文字，情感参数
@app.route("/get_stream_response", methods=['POST'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:4173', 'http://localhost:3000'], methods=['POST'])
def get_digital_human_streamed_response():
    status = None;
    if request.method == 'POST':

        print(request);
        data = request.get_json();
        print(data);
    
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Prompt is required'}), 400

        prompt = data['prompt']
        response_data = pipeline.generate_response_streamed(prompt)


        '''
        def generate_stream():
            try:
                yield json.dumps({"status": "SUCCESS", "data": ""}) + '\n'
                for chunk in response_data:
                    yield json.dumps({"status": "STREAM", "data": chunk}) + '\n'
            except Exception as e:
                yield json.dumps({'status': 'ERROR', 'error': str(e)}) + '\n'
        '''

        def unwrap_nested_generator(nested_gen):
            for gen in nested_gen:
                yield from gen

        unwrapped_response = unwrap_nested_generator(response_data)

        status = "SUCCESS";
        return Response(stream_with_context(unwrapped_response), content_type='application/json')
    else:
        status = "INCORRECT_REQUEST_METHOD";
        return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status]}); #TODO

# 获取一次聊天回复(非流式传输)
@app.route("/chat", methods=['POST'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:4173', 'http://localhost:3000'], methods=['POST'])
def chat():
    request_json = request.get_json();
    if not request_json or 'message' not in request_json or 'user_id' not in request_json:
        return jsonify({'error': 'message or user_id is required'}), 400
    
    user_message = request_json['message'];
    model_id = request_json['model_id'];

     # 从Redis获取上下文
    context = redis_client.get(f"chat_context:{model_id}")
    if context:
        context = context.decode('utf-8');
    else:
        context = ""

    system_prompt = chat_util.get_system_prompt(mysql.connection, model_id);
    history = chat_util.create_chat_history(context, user_message, system_prompt);
    #print(history);
    chat_data = pipeline.generate_chat_data(history);
    chat_object = chat_data[0];   # 聊天信息对象, 例如: {"role": "user", "content": "Hello"}
    emotion_score = chat_data[1][0];   # 情感参数

    new_context = chat_util.create_redis_cache(context, user_message, chat_object["content"]);
    redis_client.set(f"chat_context:{model_id}", new_context, ex=3600);

    cursor = mysql.connection.cursor();
    cursor.execute(
        "INSERT INTO chat_context (model_id, timestamp, message, response) VALUES (%s, %s, %s, %s)",
        (model_id, datetime.now(), user_message, chat_object)
    );
    mysql.connection.commit();
    cursor.close();

    return jsonify({'response': chat_object, 'emotion_score': emotion_score});

#获取一次数字人的语音回复
#已弃用, 将在下一个版本删除
@DeprecationWarning
@app.route("/get_response_sound", methods=['POST'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:4173'], methods=['POST'])
def get_digital_human_sound_response():
    error = None;

    if request.method == 'POST':
        data = request.get_json();
        char_id = data['char_id'];


        print("char_id:", char_id);

        cursor = mysql.connection.cursor();
        fetch_sql = "select audio_refer_text from characters where cha_uid='"+char_id+"'";
        cursor.execute(fetch_sql);
        refer_audio_path = os.path.join(PATH, char_id, "refer.wav");
        refer_text = cursor.fetchone()[0];

        print(refer_text);
        print(refer_audio_path);
        if(char_id.startswith("preset-avatar")):
            refer_audio_path = DEFAULT_REFER_AUDIO_PATH;

        response, lip_sync_data = pipeline.generate_sound_response_with_lip_sync(refer_wav_path=refer_audio_path, refer_text=refer_text, text=data['text']);
        return response, {"Content-Type": "audio/mpeg"};
    else:
        return 'error';  #TODO

#获取一次数字人的语音回复+嘴型同步数据
@app.route("/get_response_sound_with_lip_sync", methods=['POST'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:4173'], methods=['POST'])
def get_digital_human_sound_response_with_lip_sync():
    status = None;

    if request.method == 'POST':
        data = request.get_json();
        char_id = data['char_id'];

        print("char_id:", char_id);

        cursor = mysql.connection.cursor();
        fetch_sql = "select audio_refer_text from characters where cha_uid='"+char_id+"'";
        cursor.execute(fetch_sql);
        refer_audio_path = os.path.join(PATH, char_id, "refer.wav");
        refer_text = cursor.fetchone()[0];

        print(refer_text);
        print(refer_audio_path);
        if(char_id.startswith("preset-avatar")):
            refer_audio_path = DEFAULT_REFER_AUDIO_PATH;

        response_sound_base64, lip_sync_data, duration = pipeline.generate_sound_response_with_lip_sync(refer_wav_path=refer_audio_path, refer_text=refer_text, text=data['text']);
        lip_sync_data = lip_sync_data.tolist();
        status = "SUCCESS";
        combined_data = {
            "status": status,
            "msg": RESPONSE_CODE_ENUMS[status],
            "audio": response_sound_base64,
            "lip_sync_data": lip_sync_data,
            "duration": duration
        };
        return jsonify(combined_data), {"Content-Type": "application/json"};
    else:
        status = "INCORRECT_REQUEST_METHOD";
        return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status]});  #TODO

#获取预设角色列表。返回一个JSON数组
@app.route("/data/fetch_preset_characters", methods=["GET"])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:4173'], methods=['GET'])
def fetch_preset_characters():
    status = None;

    if request.method == 'GET':

        cursor = mysql.connection.cursor();

        fetch_sql="select * from preset_characters;";
        cursor.execute(fetch_sql);

        status = "SUCCESS";

        response_data = cursor.fetchall();
        return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status], "data": response_data});

    else:
        status = "INCORRECT_REQUEST_METHOD";
        return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status]});

#获取预设形象名称列表。返回一个JSON数组
@app.route("/data/fetch_preset_avatars", methods=['GET'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:4173'], methods=['GET'])
def fetch_preset_avatars():
    status = None;

    if request.method == 'GET':
        cursor = mysql.connection.cursor();

        fetch_sql="select * from preset_avatars;";
        cursor.execute(fetch_sql);

        response_data = cursor.fetchall();
        status = "SUCCESS";

        return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status], "data": response_data});

    else:
        status = "INCORRECT_REQUEST_METHOD";
        return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status]});

#获取当前用户创建的所有角色列表。返回一个JSON数组
@app.route("/data/fetch_user_characters", methods=['POST'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:4173'], methods=['GET'])
def fetch_user_characters():
    status = None;

    if request.method == 'POST':
        user_email = request.form.get('user_email');

        cursor = mysql.connection.cursor();

        match_uid_sql = "select id from users where email='"+user_email+"'";

        cursor.execute(match_uid_sql);
        uid = cursor.fetchone()[0];

        fetch_sql="select cha_uid, avatar_type, cha_name from characters where user_uid='"+uid+"' or user_uid='all';";
        cursor.execute(fetch_sql);

        response_data = cursor.fetchall();

        status = "SUCCESS";
        return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status], "data": response_data});
    else:
        status = "INCORRECT_REQUEST_METHOD";
        return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status]});

#上传参考音频前的验证API, 用于验证音频文件是否合理(格式正确，长度正确等)
@app.route("/validate_audio_length", methods=['POST'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:4173'], methods=['POST'])
def validate_audio_length():
    status = None;

    if request.method == 'POST':
        
        if 'file' not in request.files:
            status = "MISSING_FILE";
            return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status]});

        file = request.files['file'];

        with wave.open(file, 'rb') as audio:
            frames = audio.getnframes();
            rate = audio.getframerate();
            duration = frames / float(rate);
            if duration < 3 or duration > 10:
                status = "INCORRECT_FILE_CONTENT";
                return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status], "data": "音频长度需在3~10秒之间"});
        
        status = "SUCCESS";
        return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status]});

    else:
        status = "INCORRECT_REQUEST_METHOD";
        return app.hson.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status]});

#创建新的用户角色。返回成功或失败信息
@app.route("/create_custom_character", methods=["POST"])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:4173'], methods=['POST'])
def create_custom_character():
    status = None;

    if request.method == 'POST':
        # 检查是否包含文件部分, 防止恶意上传
        if 'file' not in request.files:
            status = "MISSING_FILE";
            return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status], "data": "上传的表单需要包含音频文件"}), 400;

        file = request.files['file'];
        email = request.form.get('email');
        avatar_type = request.form.get('avatar_type');
        lang_style_type = request.form.get('lang_style_type');
        audio_text = request.form.get('audio_text');
        cha_name = request.form.get('character_name');

        filename = secure_filename(file.filename);

        # 检查是否上传了一个空文件
        if filename == '':
            status = "INCORRECT_FILE_CONTENT";
            return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status], "data": "没有选择文件或上传的文件名含有异常字符"});

        if file and filename.endswith('.wav'):
            try:
                cursor = mysql.connection.cursor();
                fetch_user_sql="select id from users where email='"+email+ "';"
                cursor.execute(fetch_user_sql);
                user_id = cursor.fetchone()[0];

                char_uid = get_character_uuid().__str__();
                character_save_path = initialize_character_folder(char_uid);
            
                if(user_id != None):  #存在该用户
                    #保存音频文件
                    file.save(os.path.join(character_save_path, "refer.wav"));
                    #写入数据库记录
                    cursor = mysql.connection.cursor();
                    save_audio_sql = "insert into characters(cha_uid,avatar_type,lang_style_type,cha_name,user_uid,audio_refer_text) values ('"+char_uid+"','"+avatar_type+"','"+lang_style_type+"','"+cha_name+"','"+user_id+"','"+audio_text+"');";
                    cursor.execute(save_audio_sql);
                    mysql.connection.commit();
                    cursor.close();
                    
                    status = "SUCCESS";
                    return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status], "data": char_uid});
            except wave.Error as e:
                status = "INCORRECT_FILE_CONTENT";
                return app.json.response({"status": status, "msg":RESPONSE_CODE_ENUMS[status], "data": str(e)});
        else:
            status = "INCORRECT_FILE_CONTENT";
            return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status], "data": "错误的文件格式, 只允许上传wav格式文件"});
    else:
        status = "INCORRECT_REQUEST_METHOD";
        return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status], "data": f"请求方式有误: 请使用'POST'而不是{request.method}"});

#删除用户角色。返回成功或失败信息
@app.route("/delete_custom_character", methods=['POST'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:4173'], methods=['POST'])
def delete_custom_character():
    status = None;

    if request.method == 'POST':
        email = request.form.get('email');
        char_id = request.form.get('char_id');

        if email == None or char_id == None:
            status = "REQUEST_TARGET_NOT_FOUND";
            return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status], "data": "不存在用户或数字人id"});

        result = auth(mysql, email);

        if result:
            cursor = mysql.connection.cursor();
            delete_sql = "delete from characters where cha_uid='"+char_id+"';";
            cursor.execute(delete_sql);
            mysql.connection.commit();

            delete_result = delete_character(char_id);

            if(delete_result):
                status = "SUCCESS";
                response_msg = {"status": status, "msg": RESPONSE_CODE_ENUMS[status], "data": "已删除数字人"};
            else:
                response_msg = {"status": status, "msg": RESPONSE_CODE_ENUMS[status], "data": "无法删除数字人, 可能是ID有误"};
            
            return app.json.response(response_msg), 200;
    
    else:
        status = "INCORRECT_REQUEST_METHOD";
        return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status]});

#重命名一个用户角色。返回成功或失败信息
@app.route("/rename_custom_character", methods=['POST'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:4173'], methods=['POST'])
def rename_custom_character():
    status = None;

    if request.method == 'POST':
        email = request.form.get('email');
        char_id = request.form.get('char_id');
        new_name = request.form.get('new_name');

        if email == None or char_id == None:
            status = "REQUEST_TARGET_NOT_FOUND";
            return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status], "data": "不存在用户或数字人id"});
    
        if new_name == '' or new_name == None:
            status = "INCORRECT_REQUEST_ARGS";
            return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status], "data": "新名字不能为空"});

        result = auth(mysql, email);

        if result:
            try:
                cursor = mysql.connection.cursor();
                rename_sql = "update characters set cha_name = '"+new_name+"' where cha_uid = '"+char_id+"';";
                cursor.execute(rename_sql);

                mysql.connection.commit();
            except TypeError as e:
                status = "SERVER_ERROR";
                return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status], "data": "服务器内部错误"});

            status = "SUCCESS";
            return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status], "data": "更新名字成功"});

    else:
        status = "INCORRECT_REQUEST_METHOD";
        return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status]});

#用户请求登录系统。返回成功或失败信息
@app.route("/login/submitform", methods=["GET", "POST"])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:4173'], methods=['GET','POST'])
def login():
    status = None;
    #if flask.reqest.method =="GET"
    if flask.request.method == 'POST':
        response_msg = None;
        flask.session['login'] = ''
        email = flask.request.form.get("email", "")
        pwd = flask.request.form.get("pwd", "");
        query_user_sql = "select * from users where email='" + \
                email + "' and pwd='" + pwd + "';"
        cursor = mysql.connection.cursor();
        cursor.execute(query_user_sql);
        result = cursor.fetchone();
        if result:
            status = "SUCCESS";
            response_msg = {"status": status, "msg": RESPONSE_CODE_ENUMS[status]};
        else:  # 输入验证不通过
            status = "INCORRECT_REQUEST_ARGS";
            response_msg = {"status": status, "msg": RESPONSE_CODE_ENUMS[status], "data": "登录失败, 请检查账号或密码"};
    else:
        status = "INCORRECT_REQUEST_METHOD";
        response_msg = {"status": status, "msg": RESPONSE_CODE_ENUMS[status]};
    #print(response_msg);
    return response_msg;

#获取用户名。返回用户名或空字符串(未找到)
@app.route("/get_user_name", methods=['POST'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:4173'], methods=['POST'])
def get_user_name():
    status = None;
    if flask.request.method == 'POST':

        email = request.form.get("email");

        cursor = mysql.connection.cursor();
        fetch_sql = "select uname from users where email='"+email+"';";
        
        result = cursor.execute(fetch_sql);

        if result:
            user_name = cursor.fetchone();
            status = "SUCCESS";
            return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status], "data": user_name});
        else:
            status = "REQUEST_TARGET_NOT_FOUND";
            return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status], "data": "未找到此用户, 请检查请求参数"});

#新用户注册。返回成功或用户已存在信息
@app.route('/register',methods=['GET','POST'])
@cross_origin(origins=['http://localhost:5173', 'http://localhost:4173'], methods=['GET','POST'])
def register():
    status = None;

    if request.method == 'POST':
        uname=flask.request.form.get("user");
        pwd=flask.request.form.get("pwd");
        em=flask.request.form.get("email");

        if uname == None or pwd == None or em == None:
            status = "INCORRECT_REQUEST_ARGS";
            return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status], "data": "请确保注册信息完整"});
    
        cursor = mysql.connection.cursor();

        sql1="select uname from users where email='"+em+ "';"
        result=cursor.execute(sql1);

        if result:
            status = "INCORRECT_REQUEST_ARGS";
            return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status], "data": "已存在该用户，请重新注册"});

        user_uuid = get_user_uuid();
        sql2="insert into users(id,uname,pwd,email) values(%s,%s,%s,%s)"
        cursor.execute(sql2,[user_uuid.__str__(),uname,pwd,em])
        mysql.connection.commit();
        
        status = "SUCCESS";
        return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status]});

    else:
        status = "INCORRECT_REQUEST_METHOD";
        return app.json.response({"status": status, "msg": RESPONSE_CODE_ENUMS[status]});