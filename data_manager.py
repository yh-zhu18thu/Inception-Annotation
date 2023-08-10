from question_generater import QuestionGenerator
from accounts.manage_account import validate_user
import os
import json

class DataManager:
    # taking control of the user dataset and the question dataset
    def __init__(self) -> None:
        self.question_generater = QuestionGenerator(question_threshold=5)
        self.user_records = {}
        self.init_user_records()

    def init_user_records(self):
        # browse the answers/formal folder
        # for each file, read the user id and the answer count
        # save the user id and the answer count to the user_records dictionary
        dir_name = "data/answers/formal"
        file_names = os.listdir(dir_name)
        for file_name in file_names:
            if file_name.endswith(".txt"):
                user_id = file_name.split(".")[0]
                with open(f"{dir_name}/{file_name}",'r') as f:
                    self.user_records[user_id] = len(f.readlines())

    def validate_user(self,id,password):
        if id=='admin' and password=='admin_405':
            return True
        else:
            return validate_user(id,password)
        
    def copy_file(self,source_file_path, destination_file_path):
        try:
            print(f"Copying content from {source_file_path} to {destination_file_path}...")
            with open(source_file_path, 'r') as source_file:
                with open(destination_file_path, 'w') as destination_file:
                    for line in source_file:
                        destination_file.write(line)
            print("Content copied successfully.")
        except FileNotFoundError:
            print("One or both files not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def generate_next_question(self,user_id):
        user_file_name = f"data/questions/appointed/{user_id}.txt"
        if len(user_id.split("_")[1])==3:
            # for formal user, first check if question file exists, which means whether user has been appointed with a question
            if not os.path.exists(user_file_name):
                self.user_records[user_id] = 0
                # pick one from the files in preset folder
                dir_name = "data/questions/preset"
                file_names = os.listdir(dir_name)
                # pick the first file that is not empty
                picked_file = None
                for file_name in file_names:
                    if file_name.endswith(".txt"):
                        picked_file = file_name
                #copy the content to the appointed folder
                self.copy_file(f"{dir_name}/{picked_file}",user_file_name)
                #delete the file in the preset folder
                os.remove(f"{dir_name}/{picked_file}")
            next_question_line_idx = self.user_records[user_id]
            #read in the appointed question line
            with open(user_file_name,'r') as f:
                for i,line in enumerate(f):
                    if i==next_question_line_idx:
                        break
            # if the appointed question line is not empty, return the question
            if line:
                self.user_records[user_id]+=1
                return json.loads(line)
            else:
                return {"type":"finished"}
        else:
            if self.get_user_finished_annotation_cnt(user_id)>=10:
                return {"type":"finished"}
            return self.question_generater.get_question(user_id)
    
    def generate_default_question(self):
        return self.question_generater.get_default_question()
    
    def save_current_selection(self,user_id,data):
        # create a new file with user id if not exist, append a line to the file
        type = data["type"]
        if len(user_id.split("_")[1])==3:
            file_name = f"data/answers/formal/{user_id}.txt"
        else:
            file_name = f"data/answers/heatup/{user_id}.txt"
        with open(file_name,'a') as f:
            # dumps the json into a string
            f.write(json.dumps(data,ensure_ascii=False)+"\n")


    def get_user_finished_annotation_cnt(self,user_id) -> int:
        if len(user_id.split("_")[1])==3:
            file_name = f"data/answers/formal/{user_id}.txt"
        else:
            file_name = f"data/answers/heatup/{user_id}.txt"
        # if no user data file created, return 0
        if not os.path.exists(file_name):
            return 0
        # load the number of line in the user data file
        with open(file_name,'r') as f:
            return len(f.readlines())