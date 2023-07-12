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
        

