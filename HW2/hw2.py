import pandas as pd
import promptbench as pb
import time
import tqdm


file_path = './mmlu_sample.csv'
data = pd.read_csv(file_path)
data_list = data.to_dict(orient='records')

promptList = pb.Prompt(["The following are multiple choice questions (with answers) about {task}. You are an expert in {task}. You will be given a question in {task}.\n\
                        '''{input}'''\n\
                        Which one of the four choices is correct about the question, (A), (B), (C) or (D)?:\n\
                        Choices:\n\
                        (A) {A}\n\
                        (B) {B}\n\
                        (C) {C}\n\
                        (D) {D}\n\'''",
                        "The following are multiple choice questions (with answers) about {task}. You are an expert in {task}. You will be given a question in {task}.\n\
                        '''{input}'''\n\
                        What is the best choice for the question, (A), (B), (C) or (D)?:\n\
                        Choices:\n\
                        (A) {A}\n\
                        (B) {B}\n\
                        (C) {C}\n\
                        (D) {D}\n\'''",
                        "The following are multiple choice questions (with answers) about {task}. You are an expert in {task}. You will be given a question in {task}.\n\
                        '''{input}'''\n\
                        Which one of the four choices completes the question correctly, (A), (B), (C) or (D)?:\n\
                        Choices:\n\
                        (A) {A}\n\
                        (B) {B}\n\
                        (C) {C}\n\
                        (D) {D}\n\'''",
                        "The following are multiple choice questions (with answers) about {task}. You are an expert in {task}. You will be given a question in {task}.\n\
                        '''{input}'''\n\
                        Choices:\n\
                        (A) {A}\n\
                        (B) {B}\n\
                        (C) {C}\n\
                        (D) {D}\n\'''"
                        ])


def extractSubstringForResponse(string, start_index=-1):
    if string is None:
        string = 'DCBA'
    string = string.replace(" ", "").replace("(", "").replace(")", "")
    print('\n' + string)
    return string[start_index + 1:start_index + 2]


def projFunc(pred):
    mapping = {
        'A': 0,
        'B': 1,
        'C': 2,
        'D': 3
    }
    return mapping.get(pred, -1)


if __name__ == '__main__':
    with open('./palm_key.txt', 'r') as file:
        palm_key = file.read()
        model = pb.LLMModel(model='palm', max_new_tokens=10, temperature=0.0001, palm_key=palm_key)
    count = 0
    taskType_list = ['high_school_european_history',
                    'high_school_us_history',
                    'high_school_world_history',
                    'high_school_microeconomics',
                    'high_school_biology',
                    'high_school_government_and_politics',
                    'high_school_geography',
                    'high_school_psychology',
                    'high_school_computer_science',
                    'high_school_macroeconomics']
    preds = []
    labels = []
    
    for data in tqdm.tqdm(data_list):
        input = data['input']
        label = data['target']
        taskType = data['task']
        data['task'] = data['task'].replace("_", " ")
        
        if str(input).replace(" ", "").endswith('?'):
            prompt = promptList[3]
        elif taskType in ['high_school_european_history',
                        'high_school_us_history',
                        'high_school_world_history']:
            prompt = promptList[0]
        else:
            prompt = promptList[2]
        
        input_text = pb.InputProcess.basic_format(prompt, data)
        
        try:
            output = model(input_text)
        except:
            output = None
            time.sleep(10)
        
        raw_pred = extractSubstringForResponse(output)
        pred = projFunc(raw_pred)
        label = projFunc(label)
        print(pred, label)
        
        preds.append(pred)
        labels.append(label)
        
    with open('./record.txt', 'a') as file:
        score = pb.Eval.compute_cls_accuracy(preds, labels)
        file.write(f'{score:.3f}, {prompt}' + '\n' + '\n')
        print(f'{score:.3f}, {prompt}' + '\n' + '\n')
