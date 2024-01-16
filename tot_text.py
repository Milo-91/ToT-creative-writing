from llama_cpp import Llama
from parameters import *
import random
import time

llm = Llama(
    model_path = "openhermes-2.5-mistral-7b.Q8_0.gguf",
    n_ctx=2048,
    # n_gpu_layers=-1    
)

def Generator(llm, node):
    new_node ={}
    output = []
        
    for _ in range(5):## k=5
        ans_from_llm = {}
        filtered_ans = ""
        
        if node[0] == None:
            prompt = cot_prompt_1.format(input = node[1]['answer'])   
            ans_from_llm = llm(
                prompt,
                max_tokens = 2048,
                stop=["\n\n", "known"],
                echo = False,
                repeat_penalty = 1.1,
                temperature = 0.7,
                top_k = 40,
                top_p = 0.9,
            )
            filtered_ans = ans_from_llm["choices"][0]["text"].replace("Plans:\n", "")
        else:
            # b = node[1]['answer'][0].split('.')##chop input into 4 elements in list
            # b = [sentence.strip() for sentence in b if sentence.strip()]
            # for j in range(4):
            #     b[j] += '.'
            # if node[0][0]['answer'][0].count('\n') >= 3:##examine if plan have at least 4
            #     a = node[0][0]['answer'][0].split('\n')
            #     a = [sentence.strip() for sentence in a if sentence.strip()]
            # else:
            #     a = node[0][0]['answer'][0].split('.')##plan < 4, then copy a[0]
            #     if len(a) < 4:
            #         for _ in range(1, 5):
            #             a.append(a[0])
            #     for k in range(len(a)):
            #         a[k] = a[0]
                          
            prompt = cot_prompt_2.format(input = node[1]['answer'], plan = node[0][0]['answer'][0])
            check_1 = False        
            for _ in range(5):      
                if check_1 == False:
                    ans_from_llm = llm(
                        prompt,
                        max_tokens = 2048,
                        stop=["\n\n", "known"],
                        echo = False,
                        repeat_penalty = 1.1,
                        temperature = 0.7,
                        top_k = 40,
                        top_p = 0.9,
                    )
                    check_1 = check(ans_from_llm["choices"][0]["text"], node[1]['answer'][0])
                else: break 
            filtered_ans = ans_from_llm["choices"][0]["text"] + "\n"
        
        new_node['id'] = id
        increase_id()
        new_node['answer'] = [filtered_ans]
        new_node['value'] = None
        new_node['parent_node'] = node[1]['id']
        new_node['ancester_value'] = None

        output.append(new_node)
    return output

        

def Evaluator(llm, node):#node = []
    new_node = {}
    output = []
    best = []
    ans_from_llm = {}

    prompt  = vote_prompt + 'Choices: ' + node[0]['answer'][0] + node[1]['answer'][0] + node[2]['answer'][0] + node[3]['answer'][0] + node[4]['answer'][0]

    ans_from_llm = llm(
        prompt,
        max_tokens = 2048,
        stop=["\n\n", "known"],
        echo = False,
        repeat_penalty = 1.1,
        temperature = 0.7,
        top_k = 40,
        top_p = 0.9,
    )
    best = ans_from_llm["choices"][0]["text"].split()##暫時用random解決

    if len(best) == 5:    
        for i in range(5):
            if best[4] == str(node[i]['id']):
                break
        new_node = node[i]
    else:
        new_node = node[random.randint(0, 4)]
    output.append(new_node)
    return output

def check(text, input_data):##examine if last sentence is matched input
    fragment_1 = text.replace(', ', '. ')
    fragments_1 = fragment_1.split('. ')

    for i in range(len(fragments_1)):
        fragments_1[i] = fragments_1[i].strip()

    if fragments_1[-1] in input_data:
        return True
    else:
        return False


if __name__ == '__main__':
    start = time.time()
    with open('data_100_random_text.txt', 'r', encoding='utf-8') as file:
        data = file.readlines()
    
    root_node = {
        'id':id,
        'answer':[data[1]],
        'value':None,
        'parent_node':None,
        'ancester_value':None
    }
    increase_id()

    writing_plans = Generator(llm, [None, root_node])### Generator(llm, [plan, root_node])  no plan -->None
    best_plan = Evaluator(llm, writing_plans)

    passages = Generator(llm, [best_plan, root_node])
    best_passage = Evaluator(llm, passages)

    with open('result.txt', 'w', encoding='utf-8') as file:### open new txt
        file.write(root_node['answer'][0])
        file.write('\n...........................\n')
        file.write(best_plan[0]['answer'][0])
        file.write('\n--- --- --- --- --- --- ---\n')
        file.write(best_passage[0]['answer'][0])
        file.write('\n---------------------------\n')
    # for i in range(1, 3):
    #     root_node = {
    #         'id':id,
    #         'answer':[data[i]],
    #         'value':None,
    #         'parent_node':None,
    #         'ancester_value':None
    #     }
    #     increase_id()

    #     writing_plans = Generator(llm, [None, root_node])
    #     best_plan = Evaluator(llm, writing_plans)

    #     passages = Generator(llm, [best_plan, root_node])
    #     best_passage = Evaluator(llm, passages)

    #     with open('result.txt', 'a', encoding='utf-8') as file:### continue writing in txt
    #         file.write(root_node['answer'][0])
    #         file.write('\n...........................\n')
    #         file.write(best_plan[0]['answer'][0])
    #         file.write('\n--- --- --- --- --- --- ---\n')
    #         file.write(best_passage[0]['answer'][0])
    #         file.write('\n---------------------------\n')
    finish = time.time()
    print(finish - start)