from flask import Flask,render_template, redirect, url_for, request,session,jsonify
app = Flask(__name__)
app.secret_key = "super secret key" #change to something more secure
from data_manager import DataManager
import json

temp_user_question_dict = {}
data_manager = DataManager()

@app.route('/login',methods=['POST'])
def login():
    user_id=request.form['user_id']
    password=request.form['password']
    if data_manager.validate_user(user_id,password):
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
    test = list()
    current_user = session['user_id']
    if current_user not in temp_user_question_dict:
        temp_user_question_dict[current_user] = data_manager.generate_next_question()
    if len(temp_user_question_dict[current_user]['instances'])==0:
        temp_user_question_dict[current_user] = data_manager.generate_next_question()
        print(f"generated new question {temp_user_question_dict[current_user]}")
    quesiton_set = {"example_instance":temp_user_question_dict[current_user]['example_instance'],
                    'feasibility':temp_user_question_dict[current_user]['feasibility'],
                    'instance':temp_user_question_dict[current_user]['instances'].pop()}
    return jsonify(quesiton_set)

@app.route('/')
def hello_world():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=4820,debug=True)