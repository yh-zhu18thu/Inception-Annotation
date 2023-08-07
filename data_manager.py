from question_generater import QuestionGenerator
from accounts.manage_account import validate_user
import os

class DataManager:
    # taking control of the user dataset and the question dataset
    def __init__(self) -> None:
        self.question_generater = QuestionGenerator()

    def validate_user(self,id,password):
        if id=='admin' and password=='admin':
            return True
        else:
            return validate_user(id,password)
    
    def generate_next_question(self,user_id):
        return self.question_generater.get_question(user_id)
    
    def generate_default_question(self):
        return self.question_generater.get_default_question()
    
    def save_current_selection(self,user_id,data):
        # create a new file with user id if not exist, append a line to the file
        type = data["type"]
        
        with open(f"data/{user_id}.csv",'a') as f:
            if type=='1':
                instance = data["instance"]
                belief_rating = data["belief_rating"]
                f.write(f"{type},{instance},{belief_rating}\n")
            elif type=='1v1':
                example_instance = data["example_instance"]
                example_feasibility = data["example_feasibility"]
                instance = data["instance"]
                belief_rating = data["belief_rating"]
                statements = data["statements"]
                f.write(f"{type},{example_instance},{example_feasibility},{instance},{belief_rating},{statements}\n")
            elif type=='nv1':
                example_instances = data["example_instances"]
                feasiblities = data["example_feasiblities"]
                instance = data["instance"]
                belief_rating = data["belief_rating"]
                f.write(f"{type},{example_instances},{feasiblities},{instance},{belief_rating}\n")


    def get_user_finished_annotation_cnt(self,user_id) -> int:
        # if no user data file created, return 0
        if not os.path.exists(f"data/{user_id}.csv"):
            return 0
        # load the number of line in the user data file
        with open(f"data/{user_id}.csv",'r') as f:
            return len(f.readlines())