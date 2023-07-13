from question_generater import QuestionGenerater
from accounts.manage_account import validate_user
import os

class DataManager:
    # taking control of the user dataset and the question dataset
    def __init__(self) -> None:
        self.question_generater = QuestionGenerater()

    def validate_user(self,id,password):
        if id=='admin' and password=='admin':
            return True
        else:
            return validate_user(id,password)
    
    def generate_next_question(self):
        return self.question_generater.get_1v3_question()
    
    def save_current_selection(self,user_id,example_instance,example_feasibility,belief_rating,belief_change_rating,statements):
        # create a new file with user id if not exist, append a line to the file
        with open(f"data/{user_id}.csv",'a') as f:
            f.write(f"{example_instance},{example_feasibility},{belief_rating},{belief_change_rating},{statements}\n")

    def get_user_finished_annotation_cnt(self,user_id) -> int:
        # if no user data file created, return 0
        if not os.path.exists(f"data/{user_id}.csv"):
            return 0
        # load the number of line in the user data file
        with open(f"data/{user_id}.csv",'r') as f:
            return len(f.readlines())