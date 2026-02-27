import flask 
from flask_cors import cross_origin;
from flask import request;
from flask_mysqldb import MySQL;

# 初始化
app = flask.Flask(__name__)
app.debug = True;
app.secret_key = 'taco-ice-cream';

app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "123456qwerty"
app.config["MYSQL_DB"] = "t1"

mysql = MySQL(app);

@app.route("/login/submitform", methods=["GET", "POST"])
@cross_origin(origins='http://localhost:5173', methods=['GET','POST'])
def login():
    #if flask.reqest.method =="GET"
    if flask.request.method == 'POST':
        flask.session['login'] = ''
        user = flask.request.form.get("user", "")
        pwd = flask.request.form.get("pwd", "");
        sql1 = "select * from user7 where uname='" + \
                user + "' and pwd='" + pwd + "';"
        cursor = mysql.connection.cursor()
        cursor.execute(sql1)
        result = cursor.fetchone()
            # 匹配得到结果即管理员数据库中存在此管理员
        if result:
            return 'log_in_success' #flask.redirect(flask.url_for('firstpage'))  #登录成功则到首页
        else:  # 输入验证不通过
            msg = '账号或者密码错误！请重新输入'
    else:
        msg = ''
    print(msg);
    return 'log_in_fail'