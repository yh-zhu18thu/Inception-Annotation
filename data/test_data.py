import pandas as pd 
import sys
import json

# read in tagged data file:
df_600 = pd.read_csv("../src/instances_Inception_600_with_tag.csv")
df_150 = pd.read_csv("../src/instances_Inception_150_with_tag.csv")

# read in ability_mindmap.json
with open("../src/ability_mindmap.json",'r') as f:
    ability_mindmap = json.load(f)

# return the subtree json of the certain ability tree node
def get_node_by_name(root,node_name):
    if root['name'] == node_name:
        return root
    else:
        if 'children' in root:
            for child in root['children']:
                if get_node_by_name(child,node_name) is not None:
                    return get_node_by_name(child,node_name)
    return None


# get the children list of the certain ability tree node
def get_children_list(node_name):
    subtree_root = get_node_by_name(ability_mindmap,node_name)
    subtree_list = []
    #get the children name list recursively
    def get_children_name(node):
        if 'children' in node:
            for child in node['children']:
                subtree_list.append(child['name'])
                get_children_name(child)
    get_children_name(subtree_root)
    return subtree_list

def get_example_related_ability(statement):
    ability =[]
    if statement["option"]=="option1":
        ability.append(statement["expression"][0])
    elif statement["option"]=="option2":
        ability.append(statement["expression"][0])
    elif statement["option"]=="option3":
        if statement["expression"][0]=="样例指令":
            ability.append(statement["expression"][1])
    return ability

def get_instance_related_ability(statement):
    ability =[]
    if statement["option"]=="option1":
        ability.append(statement["expression"][0])
    elif statement["option"]=="option2":
        ability.append(statement["expression"][2])
    elif statement["option"]=="option3":
        if statement["expression"][0]=="当前指令":
            ability.append(statement["expression"][1])
    return ability

def check_data(command,user_id):
    if command=="heatup":
        file_name = f"answers/heatup/{user_id}.txt"
    elif command=="formal":
        file_name = f"answers/formal/{user_id}.txt"
        return
    else:
        return
    cnt = 0
    score = 0

    with open(file_name,'r') as f ,open("log.txt",'w') as log:
        lines = f.readlines()
        single_rating_dict = {}
        for line in lines:
            data = json.loads(line)
            if data["type"]=="1":
                instance = data["instance"]
                rating = data["belief_rating"]
                single_rating_dict[instance] = rating
        for line in lines:
            data = json.loads(line)
            if data["type"]=="1v1":
                example_instance = data["example_instance"]
                instance = data["instance"]
                rating = data["belief_rating"]
                feasiblity = data["example_feasibility"]
                #print(f"example_instance:{example_instance},instance:{instance},rating:{rating},feasiblity:{feasiblity}")
                if feasiblity=="能够稳定":
                    if rating>=single_rating_dict[instance]:
                        score+=1
                    else:
                        log.write(f"第{cnt}个1v1问题，在\"{example_instance}{feasiblity}\"的情况下，{instance}，评分为{rating}，而无前提的评分是{single_rating_dict[instance]} \n")
                else:
                    if rating<=single_rating_dict[instance]:
                        score+=1
                    else:
                        log.write(f"第{cnt}个1v1问题，在\"{example_instance}{feasiblity}\"的情况下，{instance}，评分为{rating}，而无前提的评分是{single_rating_dict[instance]} \n")
                statements = data["statements"]
                for statement in statements:
                    example_related_ability = get_example_related_ability(statement)
                    instance_related_ability = get_instance_related_ability(statement)
                    # get the annotated abilities of the example instance from df_600
                    example_annotated_abilities = df_600.loc[df_600['expression']==example_instance]['annotation'].values[0].split(',')
                    # get the annotated abilities of the instance from df_600
                    instance_annotated_abilities = df_600.loc[df_600['expression']==instance]['annotation'].values[0].split(',')
                    for ability in example_related_ability:
                        cnt+=1
                        ability_children_list = get_children_list(ability)
                        ability_children_list.append(ability)
                        print(f"ability:{ability},ability_children_list:{ability_children_list}")
                        #check if any of the children of the ability is in the annotated abilities of the example instance
                        if any([child in example_annotated_abilities for child in ability_children_list]):
                            score+=1
                        else:
                            #log the ability and all the annotated abilities of the example instance
                            log.write(f"第{cnt}个1v1问题中的样例\"{example_instance}\", 用户标注了和样例相关的\"{ability}\"tag，但样例本有的tag只有\"{','.join(example_annotated_abilities)}\"\n")
                    for ability in instance_related_ability:
                        cnt+=1
                        ability_children_list = get_children_list(ability)
                        ability_children_list.append(ability)
                        print(f"ability:{ability},ability_children_list:{ability_children_list}")
                        #check if any of the children of the ability is in the annotated abilities of the instance
                        if any([child in instance_annotated_abilities for child in ability_children_list]):
                            score+=1
                        else:
                            #log the ability and all the annotated abilities of the instance
                            log.write(f"第{cnt}个1v1问题中的样例\"{instance}\", 用户标注了和当前例子相关的\"{ability}\"tag，但当前例子本有的tag只有\"{','.join(instance_annotated_abilities)}\"\n")
                cnt+=1
        # print the average score
    print(f"user's average score is {score/cnt}")
    
def main():
    # parse the sys args: python test_data.py heatup xxx
    if len(sys.argv) < 3:
        print("Usage: python test_data.py [command] [user_id]")
        print("Available commands:")
        print("- heatup: test heatup answer")
        print("- formal: test formal answer")
        return
    else:
        command = sys.argv[1]
        user_id = sys.argv[2]
        check_data(command,user_id)


if __name__ == "__main__":
    main()