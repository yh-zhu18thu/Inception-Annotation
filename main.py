from flask import Flask,render_template, redirect, url_for, request,session,jsonify
app = Flask(__name__,static_url_path='/static')
app.secret_key = "super secret key" #change to something more secure
from data_manager import DataManager
import json

data_manager = DataManager()

# Custom Jinja2 filter
@app.template_filter('zip')
def zip_lists(a, b):
    return zip(a, b)

@app.route('/login',methods=['POST'])
def login():
    user_id=request.form['user_id']
    password=request.form['password']
    if data_manager.validate_user(user_id,password):
        session['logged_in']=True
        session['user_id']=user_id
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))
    
@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/index')
def index():
    if 'logged_in' in session:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))

@app.route('/get_next_question',methods=['GET'])
def get_next_question():
    #TODO: reimplement to decide which pattern of question is next, and render the question accordingly
    current_user = session['user_id']
    question = data_manager.generate_next_question(current_user)
    print(f"generated new question {question}")
    if question["type"]=="1v1":
        question_set = {"example_instance":question['example_instance'],
                        "example_feasibility":question['feasibility'],
                            'instance':question['instance']}
        return render_template('index_1v1.html',question_set=question_set)
    elif question["type"]=="nv1":
        question_set = {"example_instances":question['example_instances'],
                        "feasibilities":question['feasibilities'],
                            'instance':question['instance']}
        return render_template('index_nv1.html',question_set=question_set)
    elif question["type"]=="1":
        question_set = {"instance":question['instance']}
        return render_template('index_1.html',question_set=question_set)
    elif question["type"]=="finished":
        return render_template('index_finished.html')
    else:
        return "UNDEFINED",400

@app.route('/save_current_selection',methods=['POST'])
def save_current_selection():
    '''
    data: JSON.stringify({
                    'question_id': question_id,
                    'belief_rating': belief_rating,
                    'belief_change_rating': belief_change_rating,
                    'statements': statements
                })
    '''
    data = request.get_json()
    print(data)
    data_manager.save_current_selection(session['user_id'],data)
    return "success"

@app.route('/get_user_finished_annotation_cnt',methods=['GET'])
def get_user_finished_annotation_cnt():
    return jsonify(data_manager.get_user_finished_annotation_cnt(session['user_id']))

@app.route('/')
def hello_world():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=4820,debug=True)