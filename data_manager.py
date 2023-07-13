from question_generater import QuestionGenerater

class DataManager:
    # taking control of the user dataset and the question dataset
    def __init__(self) -> None:
        self.question_generater = QuestionGenerater()

    def validate_user(self,id,password):
        if id=='admin' and password=='admin':
            return True
        else:
            return False
    
    def generate_next_question(self):
        return self.question_generater.get_1v3_question()
    
    def save_current_selection(self,user_id,question_id,belief_rating,belief_change_rating,statements):
        # create a new file with user id if not exist, append a line to the file
        with open(f"data/{user_id}.csv",'a') as f:
            f.write(f"{question_id},{belief_rating},{belief_change_rating},{statements}\n")

