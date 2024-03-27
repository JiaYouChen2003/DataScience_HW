import csv
import google.generativeai as genai
import pandas as pd
import promptbench as pb
import time
import tqdm


file_path = './submit.csv'
data = pd.read_csv(file_path)
data_list = data.to_dict(orient='records')
header = ['ID', 'target']
sample_file_path = './mmlu_sample.csv'
sample_data = pd.read_csv(sample_file_path)
sample_data_list = sample_data.to_dict(orient='records')

promptList = pb.Prompt(["Q: The following is a multiple choice question (with answers) about european history. You are an expert of european history that need to take responsible of the answer.\n\
                            '''\n" + sample_data_list[0]['input'] + "\n'''\n\
                            Choices:'''\n\
                            (A) " + sample_data_list[0]['A'] + "\n\
                            (B) " + sample_data_list[0]['B'] + "\n\
                            (C) " + sample_data_list[0]['C'] + "\n\
                            (D) " + sample_data_list[0]['D'] + "\n\
                            '''\n\
                            Let's think it step by step. Then output which one of the four choices is correct about the question, (A), (B), (C) or (D)?\n\
                            A: After I examine the question carefully, the answer is choice (D) " + sample_data_list[0]['D'] + "\n\
                            Q: The following is a multiple choice question (with answers) about macroeconomics. You are an expert of macroeconomics that need to take responsible of the answer.\n\
                            '''\n" + sample_data_list[-1]['input'] + "\n'''\n\
                            Choices:'''\n\
                            (A) " + sample_data_list[-1]['A'] + "\n\
                            (B) " + sample_data_list[-1]['B'] + "\n\
                            (C) " + sample_data_list[-1]['C'] + "\n\
                            (D) " + sample_data_list[-1]['D'] + "\n\
                            '''\n\
                            Let's think it step by step. Then output which one of the four choices is correct about the question, (A), (B), (C) or (D)?\n\
                            A: After I examine the question carefully, the answer is choice (B) " + sample_data_list[-1]['B'] + "\n\
                            Q: The following is a multiple choice question (with answers) about {task}. You are an expert of {task} that need to take responsible of the answer.\n\
                            '''\n{input}\n'''\n\
                            Choices:'''\n\
                            (A) {A}\n\
                            (B) {B}\n\
                            (C) {C}\n\
                            (D) {D}\n\
                            '''\n\
                            Let's think it step by step. Then output which one of the four choices is correct about the question, (A), (B), (C) or (D)?\n\
                            A: After I examine the question carefully, the answer is choice ",
                        "Q: The following is a multiple choice question (with answers) about european history. You are an expert of european history that need to take responsible of the answer.\n\
                            '''\n" + sample_data_list[0]['input'] + "\n'''\n\
                            Choices:'''\n\
                            (A) " + sample_data_list[0]['A'] + "\n\
                            (B) " + sample_data_list[0]['B'] + "\n\
                            (C) " + sample_data_list[0]['C'] + "\n\
                            (D) " + sample_data_list[0]['D'] + "\n\
                            '''\n\
                            Let's think it step by step. Then output which one of the four choices is correct about the question, (A), (B), (C) or (D)?\n\
                            A: After I examine the question carefully, the answer is choice (" + sample_data_list[0]['target'] + ") " + sample_data_list[0][sample_data_list[0]['target']] + "\n\
                            Q: The following is a multiple choice question (with answers) about macroeconomics. You are an expert of macroeconomics that need to take responsible of the answer.\n\
                            '''\n" + sample_data_list[200]['input'] + "\n'''\n\
                            Choices:'''\n\
                            (A) " + sample_data_list[200]['A'] + "\n\
                            (B) " + sample_data_list[200]['B'] + "\n\
                            (C) " + sample_data_list[200]['C'] + "\n\
                            (D) " + sample_data_list[200]['D'] + "\n\
                            '''\n\
                            Let's think it step by step. Then output which one of the four choices is correct about the question, (A), (B), (C) or (D)?\n\
                            A: After I examine the question carefully, the answer is choice (" + sample_data_list[200]['target'] + ") " + sample_data_list[200][sample_data_list[200]['target']] + "\n\
                            Q: The following is a multiple choice question (with answers) about macroeconomics. You are an expert of macroeconomics that need to take responsible of the answer.\n\
                            '''\n" + sample_data_list[-1]['input'] + "\n'''\n\
                            Choices:'''\n\
                            (A) " + sample_data_list[-1]['A'] + "\n\
                            (B) " + sample_data_list[-1]['B'] + "\n\
                            (C) " + sample_data_list[-1]['C'] + "\n\
                            (D) " + sample_data_list[-1]['D'] + "\n\
                            '''\n\
                            Let's think it step by step. Then output which one of the four choices is correct about the question, (A), (B), (C) or (D)?\n\
                            A: After I examine the question carefully, the answer is choice (" + sample_data_list[-1]['target'] + ") " + sample_data_list[-1][sample_data_list[-1]['target']] + "\n\
                            Q: The following is a multiple choice question (with answers) about {task}. You are an expert of {task} that need to take responsible of the answer.\n\
                            '''\n{input}\n'''\n\
                            Choices:'''\n\
                            (A) {A}\n\
                            (B) {B}\n\
                            (C) {C}\n\
                            (D) {D}\n\
                            '''\n\
                            Let's think it step by step. Then output which one of the four choices is correct about the question, (A), (B), (C) or (D)?\n\
                            A: After I examine the question carefully, the answer is choice ",
                        "Q: You are an expert of {task} that need to take responsible of the answer. The following is a multiple choice question (with answers) about {task}.\n\
                            '''\n{input}\n'''\n\
                            Choices:'''\n\
                            (A) {A}\n\
                            (B) {B}\n\
                            (C) {C}\n\
                            (D) {D}\n\
                            '''\n\
                            Let's think it step by step, output which one of the four choices completes the question correctly, (A), (B), (C) or (D)?\n\
                            A: After I examine the question carefully, the answer is choice ",
                        "Q: You are an expert of {task} that need to take responsible of the answer. The following is a multiple choice question (with answers) about {task}.\n\
                            '''\n{input}\n'''\n\
                            Choices:'''\n\
                            (A) {A}\n\
                            (B) {B}\n\
                            (C) {C}\n\
                            (D) {D}\n\
                            '''\n\
                            Let's think it step by step, output what is the best choice for the question, (A), (B), (C) or (D)?\n\
                            A: After I examine the question carefully, the answer is choice ",
                        "Q: The following is a multiple choice question (with answers) about macroeconomics. You are an expert of macroeconomics that need to take responsible of the answer.\n\
                            '''\n" + sample_data_list[-1]['input'] + "\n'''\n\
                            Choices:'''\n\
                            (A) " + sample_data_list[-1]['A'] + "\n\
                            (B) " + sample_data_list[-1]['B'] + "\n\
                            (C) " + sample_data_list[-1]['C'] + "\n\
                            (D) " + sample_data_list[-1]['D'] + "\n\
                            '''\n\
                            Let's think it step by step. Then output which one of the four choices is correct about the question, (A), (B), (C) or (D)?\n\
                            A: After I examine the question carefully, the answer is choice (" + sample_data_list[-1]['target'] + ") " + sample_data_list[-1][sample_data_list[-1]['target']] + "\n\
                            Q: The following is a multiple choice question (with answers) about macroeconomics. You are an expert of macroeconomics that need to take responsible of the answer.\n\
                            '''\n" + sample_data_list[-4]['input'] + "\n'''\n\
                            Choices:'''\n\
                            (A) " + sample_data_list[-4]['A'] + "\n\
                            (B) " + sample_data_list[-4]['B'] + "\n\
                            (C) " + sample_data_list[-4]['C'] + "\n\
                            (D) " + sample_data_list[-4]['D'] + "\n\
                            '''\n\
                            Let's think it step by step. Then output which one of the four choices is correct about the question, (A), (B), (C) or (D)?\n\
                            A: After I examine the question carefully, the answer is choice (" + sample_data_list[-4]['target'] + ") " + sample_data_list[-4][sample_data_list[-4]['target']] + "\n\
                            Q: The following is a multiple choice question (with answers) about macroeconomics. You are an expert of macroeconomics that need to take responsible of the answer.\n\
                            '''\n" + sample_data_list[-31]['input'] + "\n'''\n\
                            Choices:'''\n\
                            (A) " + sample_data_list[-31]['A'] + "\n\
                            (B) " + sample_data_list[-31]['B'] + "\n\
                            (C) " + sample_data_list[-31]['C'] + "\n\
                            (D) " + sample_data_list[-31]['D'] + "\n\
                            '''\n\
                            Let's think it step by step. Then output which one of the four choices is correct about the question, (A), (B), (C) or (D)?\n\
                            A: After I examine the question carefully, the answer is choice (" + sample_data_list[-31]['target'] + ") " + sample_data_list[-31][sample_data_list[-31]['target']] + "\n\
                            Q: The following is a multiple choice question (with answers) about {task}. You are an expert of {task} that need to take responsible of the answer.\n\
                            '''\n{input}\n'''\n\
                            Choices:'''\n\
                            (A) {A}\n\
                            (B) {B}\n\
                            (C) {C}\n\
                            (D) {D}\n\
                            '''\n\
                            Let's think it step by step. Then output which one of the four choices is correct about the question, (A), (B), (C) or (D)?\n\
                            A: After I examine the question carefully, the answer is choice "
                        ])


def extractSubstringForResponse(string, start_index=-1):
    if string is None:
        string = 'DCBA'
    string = string.split("(", 1)[-1].strip()
    print("(" + string)
    string = string.replace(" ", "").replace("(", "").replace(")", "")
    return string[start_index + 1:start_index + 2]


def projFunc(pred):
    mapping = {
        'A': 0,
        'B': 1,
        'C': 2,
        'D': 3
    }
    return mapping.get(pred, -1)


def getModel(modelName, apiKey):
    if modelName == 'palm':
        return pb.LLMModel(model='palm', max_new_tokens=10, temperature=0.0001, palm_key=apiKey)
    elif modelName == 'gemini':
        genai.configure(api_key=apiKey)
        return genai.GenerativeModel('gemini-pro')


if __name__ == '__main__':
    with open('./palm_key.txt', 'r') as file:
        palmKey = file.read()
        geminiKey = file.read()
    mode = 'palm'
    model = getModel(mode, palmKey)
    
    count = 0
    previousTypeCount = 0
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
    
    raw_preds = []
    prev_i = 0
    for i, data in tqdm.tqdm(enumerate(data_list), total=len(data_list)):
        input = data['input']
        taskType = data['task']
        
        data['task'] = data['task'][12:].replace("_", " ")
        print('\n' + data['task'])
        
        if taskType in ['high_school_macroeconomics']:
            prompt = promptList[4]
        elif taskType in ['high_school_psychology']:
            if str(input).replace(" ", "").endswith('?'):
                prompt = promptList[3]
            else:
                prompt = promptList[2]
        elif taskType in ['high_school_european_history',
                        'high_school_us_history']:
            prompt = promptList[1]
        else:
            prompt = promptList[0]
        
        input_text = pb.InputProcess.basic_format(prompt, data)
        
        if mode == 'palm' and taskType in ['high_school_world_history',
                                        'high_school_biology',
                                        'high_school_government_and_politics',
                                        'high_school_geography',
                                        'high_school_computer_science',
                                        'high_school_macroeconomics']:
            mode = 'gemini'
            model = getModel(mode, geminiKey)
        elif mode == 'gemini' and taskType in ['high_school_european_history',
                                            'high_school_microeconomics',
                                            'high_school_psychology']:
            mode = 'palm'
            model = getModel(mode, palmKey)
        
        try:
            if mode == 'palm':
                output = model(input_text)
            elif mode == 'gemini':
                output = model.generate_content(input_text)
                output = output.text
        except:
            output = None
            time.sleep(10)
        
        raw_pred = extractSubstringForResponse(output)
        raw_preds.append(raw_pred)
    
    with open('./hw2_output.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        
        writer.writerow(header)
        for i, raw_pred in enumerate(raw_preds):
            writer.writerow([data_list[i]['ID'], raw_pred])
