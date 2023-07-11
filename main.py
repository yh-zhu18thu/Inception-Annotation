from flask import Flask,render_template, redirect, url_for, request,session,jsonify
app = Flask(__name__)
app.secret_key = "super secret key" #change to something more secure
from data import validate_user
import json

@app.route('/login',methods=['POST'])
def login():
    user_id=request.form['user_id']
    password=request.form['password']
    if validate_user(user_id,password):
        session['logged_in']=True
        session['user_id']=user_id
        return redirect(url_for('index',user_id=user_id))
    else:
        return redirect(url_for('login'))
    
@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/index')
def index():
    if 'logged_in' in session:
        return render_template('index.html',user_id=session['user_id'])
    else:
        return redirect(url_for('login'))

@app.route('/get_next_question',methods=['GET'])
def get_next_question():
    print("get next question")
    question_set = {"example_instance":"能帮我规划下记事本中列的待办事项吗","feasibility":True,
                    "instance1":"帮我整理下昨天的课堂笔记",
                    "instance2":"我明天的日程安排是什么？",
                    "instance3":"提醒我开启待会的会议的录屏"}
    return jsonify(question_set)

@app.route('/')
def hello_world():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=4820,debug=True)