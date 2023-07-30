import pandas as pd
import random
import bisect
import itertools

class QuestionGenerater:
    def __init__(self) -> None:
        self.instance_dataset_path = "src/instances_with_similarity_Robuddy.csv"
        self.load_instance_dataset()
        self.instance_cnt = len(self.df)
        self.user_question_statistic = {}
        

    def load_instance_dataset(self):
        self.df = pd.read_csv(self.instance_dataset_path)
    
    def pick_random_example_id(self):
        random_number = random.randint(0,self.instance_cnt)
        return random_number

    def pick_positive_or_negative(self):
        choice = random.choices([True,False],weights=[0.7,0.3],k=1)[0]
        return choice

    def get_distribution_from_sorted_list(self,sorted_list):
        inverse_probs = [1/(rank*rank) for rank in range(1,len(sorted_list)+1)]
        total_inverse_probs = sum(inverse_probs)
        discounted_inverse_probs = [inv_prob/total_inverse_probs for inv_prob in inverse_probs]
        return discounted_inverse_probs

    def priorized_pick_from_sorted_list(self,sorted_list,item_cnt=1):
        probs = self.get_distribution_from_sorted_list(sorted_list)
        cumulative_probs = list(itertools.accumulate(probs))
        picked_list = []
        while len(picked_list)<item_cnt:
            random_number = random.random()
            index = bisect.bisect(cumulative_probs,random_number)
            if index not in picked_list:
                picked_list.append(index)
        return picked_list

    def get_default_question(self):
        return {"type":"1v1","example_instance":"","feasibility":True,"instance":[""]}
    
    def get_1v1_question(self,user_id):
        instance_id = self.pick_random_example_id()
        #print(df.iloc[instance_id])
        instance_row = self.df.iloc[instance_id]
        instance_expression = instance_row.loc["expression"]
        similarity_dict = {}
        correct=self.pick_positive_or_negative()
        for i in range(self.instance_cnt):
            similarity = float(instance_row.loc[f"similarity_{i}"])
            similarity_dict[i] = similarity
        sorted_similarity_list = sorted(similarity_dict.items(),key=lambda x:x[1],reverse=True)[1:]
        picked_list = self.priorized_pick_from_sorted_list(sorted_similarity_list)
        picked_index_list = [sorted_similarity_list[rank][0] for rank in picked_list]
        expression_list = [self.df.iloc[id].loc["expression"] for id in picked_index_list]
        self.user_question_statistic[user_id]["single_commands"].add(expression_list[0])
        return {"type":"1v1","example_instance":instance_expression,"feasibility":correct,"instance":expression_list[0]}
    
    def get_1_question(self,user_id):
        # randomly pick one from single commands and delete it from the set
        single_commands = self.user_question_statistic[user_id]["single_commands"]
        single_commands = list(single_commands)
        picked_index = random.randint(0,len(single_commands)-1)
        picked_command = single_commands[picked_index]
        single_commands.remove(picked_command)
        self.user_question_statistic[user_id]["single_commands"] = set(single_commands)
        return {"type":"1","instance":picked_command}

    
    def get_question(self,user_id):
        if user_id not in self.user_question_statistic:
            self.user_question_statistic[user_id] = {"single_commands":set()}
        #0.5 true 0.5 false
        random_number = random.random()
        if random_number<0.5 and len(self.user_question_statistic[user_id]["single_commands"])>0:
            return self.get_1_question(user_id)
        else:
            return self.get_1v1_question(user_id)