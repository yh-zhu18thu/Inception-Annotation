import pandas as pd
import random
import bisect
import itertools
import numpy as np
import os
import pickle
import json

class QuestionGenerater:
    def __init__(self) -> None:
        self.instance_dataset_path = "src/instances_with_similarity_Robuddy.csv"
        self.user_data_path = "data/formal"
        self.statistics_path = "statistics/"
        self.load_instance_dataset()
        self.user_question_statistic = {}
        self.overall_statistic = {}

    def init_statistics(self):
        instance_freq = np.zeros(self.instance_cnt,dtype=np.int32)
        np.zeros((self.instance_cnt,self.instance_cnt),dtype=np.int32)
    
    def init_instance_freq(self):
        if not os.path.exists("statistics/instance_freq.pkl"):
            self.instance_freq = np.zeros(self.instance_cnt,dtype=np.int32)
            with open("statistics/instance_freq.pkl",'wb') as f:
                pickle.dump(self.instance_freq,f)
        else:
            with open("statistics/instance_freq.pkl",'rb') as f:
                self.instance_freq = pickle.load(f)

    def init_ability_index(self):
        self.ability_index_dict = {}
        ability_json_file = "src/ability_mindmap.json"
        with open(ability_json_file,'r') as f:
            self.ability_tree = json.load(f)
        self.index = 0
        def traverse_ability_tree(node):
            self.ability_index_dict[node["name"]] = self.index
            self.index+=1
            if "children" in node:
                for child in node["children"]:
                    traverse_ability_tree(child)
        traverse_ability_tree(self.ability_tree)

    def get_ancestor_list(self,ability_name):
        ancestor_list = []
        def traverse_tree(node):
            if node["name"]==ability_name:
                return True
            if "children" in node:
                for child in node["children"]:
                    if traverse_tree(child):
                        ancestor_list.append(child["name"])
                        return True
            return False
        traverse_tree(self.ability_tree)
        return ancestor_list

    def init_ability_pair_ref(self):
        with open("statistics/ability_pair_ref.pickle",'rb') as f:
            self.ability_pair_ref = pickle.load(f)

    def init_ability_pair_freq(self):
        if os.path.exists("statistics/ability_pair_freq.pickle"):
            with open("statistics/ability_pair_freq.pickle",'rb') as f:
                self.ability_pair_freq = pickle.load(f)
        else:
            self.ability_pair_freq = np.zeros((len(self.ability_index_dict),len(self.ability_index_dict)),dtype=np.int32)
            with open("statistics/ability_pair_freq.pickle",'wb') as f:
                pickle.dump(self.ability_pair_freq,f)


    def load_instance_dataset(self):
        self.df = pd.read_csv(self.instance_dataset_path)
        self.instance_cnt = len(self.df)

    
    def pick_random_example_id(self):
        # randomly pick to make the instance freq uniform
        # pick according to current picked times versus uniform distribution
        temp_instance_freq = self.instance_freq.copy()
        probability = 1-temp_instance_freq/sum(temp_instance_freq)
        probability = probability/sum(probability)
        cumulative_probability = list(itertools.accumulate(probability))
        random_number = random.random()
        index = bisect.bisect(cumulative_probability,random_number)
        return index


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
        # randomly pick one instance as example according to current picked times versus uniform distribution
        instance_id = self.pick_random_example_id()
        instance_row = self.df.iloc[instance_id]
        instance_expression = instance_row.loc["expression"]
        # get a list of semantically similar instances using reverse distribution
        similarity_dict = {}
        for i in range(self.instance_cnt):
            similarity = float(instance_row.loc[f"similarity_{i}"])
            similarity_dict[i] = similarity
        sorted_similarity_list = sorted(similarity_dict.items(),key=lambda x:x[1],reverse=True)[1:]
        picked_list = self.priorized_pick_from_sorted_list(sorted_similarity_list,item_cnt=10)
        picked_index_list = [sorted_similarity_list[rank][0] for rank in picked_list]
        expression_list = [self.df.iloc[id].loc["expression"] for id in picked_index_list]
        # score the list according to ability pair frequency and ability pair ref
        score_list = []
        instance_ability_list = self.get_ancestor_list(instance_expression)
        for expression in expression_list:
            expression_ability_list = self.get_ancestor_list(expression)
            score = 0
            temp_ability_pair_freq = self.ability_pair_freq.copy()
            for instance_ability in instance_ability_list:
                for expression_ability in expression_ability_list:
                    temp_ability_pair_freq[self.ability_index_dict[instance_ability]][self.ability_index_dict[expression_ability]]+=1
            # normalize the ability pair freq
            temp_ability_pair_freq = temp_ability_pair_freq/np.sum(temp_ability_pair_freq)
            # calculate the difference between the ability pair freq and ability pair ref
            score = np.sum(np.abs(temp_ability_pair_freq-self.ability_pair_ref))
            score_list.append(score)
        # pick probability according to the score
        probs = self.get_distribution_from_sorted_list(score_list)
        cumulative_probs = list(itertools.accumulate(probs))
        random_number = random.random()
        index = bisect.bisect(cumulative_probs,random_number)
        picked_expression = expression_list[index]
        correct=self.pick_positive_or_negative()
        self.update_statistics(user_id,instance_expression,picked_expression)
        return {"type":"1v1","example_instance":instance_expression,"feasibility":correct,"instance":picked_expression}
    
    def update_statistics(self,user_id,example_instance,picked_expression):
        self.user_question_statistic[user_id]["single_commands"].add(picked_expression)
        # update ability pair freq
        instance_ability_list = self.get_ancestor_list(example_instance)
        expression_ability_list = self.get_ancestor_list(picked_expression)
        for instance_ability in instance_ability_list:
            for expression_ability in expression_ability_list:
                self.ability_pair_freq[self.ability_index_dict[instance_ability]][self.ability_index_dict[expression_ability]]+=1
        # update instance freq
        self.instance_freq[example_instance]+=1
        
    
    def get_nv1_question(self,user_id,n):
        # randomly pick an instance uniformly
        instance_id = random.randint(0,self.instance_cnt-1)
        instance_row = self.df.iloc[instance_id]
        instance_expression = instance_row.loc["expression"]
        #randomly picked several other instances according to the reverse square distribution
        similarity_dict = {}
        for i in range(self.instance_cnt):
            similarity = float(instance_row.loc[f"similarity_{i}"])
            similarity_dict[i] = similarity
        sorted_similarity_list = sorted(similarity_dict.items(),key=lambda x:x[1],reverse=True)[1:]
        picked_list = self.priorized_pick_from_sorted_list(sorted_similarity_list,item_cnt=n)
        picked_index_list = [sorted_similarity_list[rank][0] for rank in picked_list]
        expression_list = [self.df.iloc[id].loc["expression"] for id in picked_index_list]
        # generate a list of feasibilities
        feasibility_list = []
        for i in range(n):
            feasibility_list.append(self.pick_positive_or_negative())
        return {"type":"nv1","example_instances":expression_list,"instance":instance_expression,"feasibilities":feasibility_list}
        

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